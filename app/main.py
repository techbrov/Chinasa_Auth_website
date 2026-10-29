import re
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, time as dtime
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from .admin import setup_admin
from .config import settings
from .database import Base, engine, get_db
from .models import Book, Certification, Enquiry, Event, Page, Review, Service, Subscriber
from .notify import send_enquiry_email

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals.update(site_name=settings.site_name, site_url=settings.site_url)


def date_range(start: datetime, end: datetime | None) -> str:
    """'6 to 18 July 2025', '30 September to 4 October 2026' or 'Friday 31 October 2025'."""
    if end is None or end.date() == start.date():
        return f"{start.strftime('%A')} {start.day} {start.strftime('%B %Y')}"
    if (start.year, start.month) == (end.year, end.month):
        return f"{start.day} to {end.day} {end.strftime('%B %Y')}"
    if start.year == end.year:
        return f"{start.day} {start.strftime('%B')} to {end.day} {end.strftime('%B %Y')}"
    return f"{start.day} {start.strftime('%B %Y')} to {end.day} {end.strftime('%B %Y')}"


templates.env.filters["date_range"] = lambda e: date_range(e.starts_at, e.ends_at)

TOPICS = ["Speaking", "Book editing", "Ghostwriting", "Coaching and consultation",
          "Writing training", "Press and media", "Something else"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.site_url.startswith("https") and settings.admin_password == "change-me":
        raise RuntimeError("Set a strong ADMIN_PASSWORD (and SECRET_KEY) before going live.")
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title=settings.site_name, lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
setup_admin(app)


class RateLimiter:
    """Allow `limit` hits per `window` seconds per key. In-memory: fine for one server.
    (With several server processes, move this to Redis.)"""

    def __init__(self, limit: int, window: int) -> None:
        self.limit, self.window = limit, window
        self.hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        q = self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True


contact_limiter = RateLimiter(limit=5, window=3600)
subscribe_limiter = RateLimiter(limit=5, window=3600)


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")


def render(request: Request, name: str, status_code: int = 200, **ctx):
    ctx.setdefault("year", datetime.now().year)
    return templates.TemplateResponse(request, name, ctx, status_code=status_code)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return render(request, "404.html", status_code=404)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


def start_of_today() -> datetime:
    return datetime.combine(datetime.now().date(), dtime.min)


def end_of_event():
    """An event is over once its last day (ends_at, or starts_at for one-day events) has passed."""
    return func.coalesce(Event.ends_at, Event.starts_at)


def get_page(db: Session, slug: str) -> Page:
    page = db.scalar(select(Page).where(Page.slug == slug))
    if page is None:
        raise HTTPException(status_code=404)
    return page


# ---------- Public pages ----------
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    services = db.scalars(select(Service).where(Service.is_published).order_by(Service.sort_order).limit(4)).all()
    books = db.scalars(select(Book).where(Book.is_published, Book.kind == "authored")
                       .order_by(Book.reading_order)).all()
    reviews = db.scalars(select(Review).where(Review.is_published, Review.permission_confirmed).limit(3)).all()
    cert_count = len(db.scalars(select(Certification.id)).all())
    next_event = db.scalar(select(Event).where(Event.is_published, end_of_event() >= start_of_today())
                           .order_by(Event.starts_at).limit(1))
    return render(request, "home.html", services=services, books=books, reviews=reviews, cert_count=cert_count,
                  next_event=next_event,
                  title=f"{settings.site_name} | Book editor, ghostwriter and writing coach",
                  description="Turning raw manuscripts into global books. Book editing, ghostwriting, coaching and training.")


@app.get("/about")
def about(request: Request, db: Session = Depends(get_db)):
    page = get_page(db, "about")
    certs = db.scalars(select(Certification).order_by(Certification.sort_order)).all()
    return render(request, "page.html", page=page, certs=certs, photo="img/author-photo.jpg",
                  title=page.title, description=page.meta_description)


@app.get("/speaking")
def speaking(request: Request, db: Session = Depends(get_db)):
    page = get_page(db, "speaking")
    return render(request, "page.html", page=page, cta_topic="Speaking", title=page.title,
                  description=page.meta_description)


@app.get("/privacy")
def privacy(request: Request, db: Session = Depends(get_db)):
    page = get_page(db, "privacy")
    return render(request, "page.html", page=page, title=page.title, description=page.meta_description)


@app.get("/press-kit")
def press_kit(request: Request, db: Session = Depends(get_db)):
    page = get_page(db, "press-kit")
    books = db.scalars(select(Book).where(Book.is_published, Book.kind == "authored")
                       .order_by(Book.reading_order)).all()
    return render(request, "press.html", page=page, books=books, title=page.title,
                  description=page.meta_description)


@app.get("/services")
def services(request: Request, db: Session = Depends(get_db)):
    items = db.scalars(select(Service).where(Service.is_published).order_by(Service.sort_order)).all()
    return render(request, "services.html", services=items, title="Services",
                  description="Book editing, ghostwriting, formatting, publishing support, coaching and training.")


@app.get("/services/{slug}")
def service_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    item = db.scalar(select(Service).where(Service.slug == slug, Service.is_published))
    if item is None:
        raise HTTPException(status_code=404)
    return render(request, "service_detail.html", service=item, title=item.title, description=item.summary)


@app.get("/books")
def books(request: Request, db: Session = Depends(get_db)):
    own = db.scalars(select(Book).where(Book.is_published, Book.kind == "authored")
                     .order_by(Book.reading_order)).all()
    edited = db.scalars(select(Book).where(Book.is_published, Book.kind == "edited").order_by(Book.title)).all()
    return render(request, "books.html", own=own, edited=edited, title="Books",
                  description="Books by Chinasa Elukposi, in reading order, and books she has edited.")


@app.get("/books/{slug}")
def book_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    book = db.scalar(select(Book).where(Book.slug == slug, Book.is_published))
    if book is None:
        raise HTTPException(status_code=404)
    return render(request, "book_detail.html", book=book, title=book.title,
                  description=(book.blurb or book.title)[:300])


@app.get("/events")
def events(request: Request, db: Session = Depends(get_db)):
    today = start_of_today()
    upcoming = db.scalars(select(Event).where(Event.is_published, end_of_event() >= today)
                          .order_by(Event.starts_at)).all()
    past = db.scalars(select(Event).where(Event.is_published, end_of_event() < today)
                      .order_by(Event.starts_at.desc()).limit(12)).all()
    return render(request, "events.html", upcoming=upcoming, past=past, title="Events",
                  description="Upcoming and past speaking events, trainings, workshops and book launches.")


@app.get("/reviews")
def reviews(request: Request, db: Session = Depends(get_db)):
    items = db.scalars(select(Review).where(Review.is_published, Review.permission_confirmed)).all()
    return render(request, "reviews.html", reviews=items, title="Client reviews",
                  description="What authors say about working with The Seasoned Book Editor.")


# ---------- Forms ----------
@app.get("/contact")
def contact_form(request: Request, topic: str = ""):
    return render(request, "contact.html", topics=TOPICS, form={"topic": topic}, errors=[],
                  title="Contact", description="Send an enquiry or a speaking request.")


@app.post("/contact")
def contact_submit(request: Request, background: BackgroundTasks, db: Session = Depends(get_db),
                   name: str = Form(""), email: str = Form(""), topic: str = Form(""),
                   message: str = Form(""), consent: str = Form(""), website: str = Form("")):
    if website:  # honeypot: real people never fill this hidden field
        return RedirectResponse("/thanks", status_code=303)
    if not contact_limiter.allow(client_ip(request)):
        return render(request, "message.html", status_code=429, heading="Too many messages",
                      text="Please try again later.", title="Too many messages", description="")
    errors = []
    name, email, message = name.strip(), email.strip(), message.strip()
    if not name:
        errors.append("Please enter your name.")
    if not EMAIL_RE.match(email):
        errors.append("Please enter a valid email address.")
    if topic not in TOPICS:
        errors.append("Please choose a topic.")
    if len(message) < 10:
        errors.append("Please write a message of at least 10 characters.")
    if not consent:
        errors.append("Please tick the box so we may store your details and reply.")
    if errors:
        return render(request, "contact.html", status_code=400, topics=TOPICS, errors=errors,
                      form={"name": name, "email": email, "topic": topic, "message": message},
                      title="Contact", description="")
    db.add(Enquiry(name=name, email=email, topic=topic, message=message, consent=True))
    db.commit()
    background.add_task(send_enquiry_email, name, email, topic, message)
    return RedirectResponse("/thanks", status_code=303)


@app.post("/subscribe")
def subscribe(request: Request, db: Session = Depends(get_db), email: str = Form(""),
              consent: str = Form(""), website: str = Form("")):
    if website:
        return RedirectResponse("/subscribed", status_code=303)
    if not subscribe_limiter.allow(client_ip(request)):
        return render(request, "message.html", status_code=429, heading="Too many attempts",
                      text="Please try again later.", title="Too many attempts", description="")
    email = email.strip().lower()
    if not EMAIL_RE.match(email) or not consent:
        return render(request, "message.html", status_code=400, heading="Please check your details",
                      text="Enter a valid email and tick the consent box.", title="Check your details",
                      description="")
    try:
        db.add(Subscriber(email=email, consent=True))
        db.commit()
    except IntegrityError:
        db.rollback()  # already subscribed: treat as success
    return RedirectResponse("/subscribed", status_code=303)


@app.get("/thanks")
def thanks(request: Request):
    return render(request, "message.html", heading="Message received",
                  text="Thank you. Chinasa will reply to your email soon.", title="Thank you", description="")


@app.get("/subscribed")
def subscribed(request: Request):
    return render(request, "message.html", heading="You are subscribed",
                  text="Thank you for joining the list.", title="Subscribed", description="")


# ---------- SEO and health ----------
@app.get("/robots.txt")
def robots():
    return PlainTextResponse(f"User-agent: *\nDisallow: /admin\nSitemap: {settings.site_url}/sitemap.xml\n")


@app.get("/sitemap.xml")
def sitemap(db: Session = Depends(get_db)):
    paths = ["/", "/about", "/services", "/books", "/speaking", "/events", "/press-kit", "/reviews",
             "/contact", "/privacy"]
    paths += [f"/books/{s}" for s in db.scalars(select(Book.slug).where(Book.is_published, Book.kind == "authored"))]
    paths += [f"/services/{s}" for s in db.scalars(select(Service.slug).where(Service.is_published))]
    urls = "".join(f"<url><loc>{settings.site_url}{p}</loc></url>" for p in paths)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, media_type="application/xml")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
