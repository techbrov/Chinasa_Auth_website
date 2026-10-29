from datetime import datetime, timedelta

from sqlalchemy import select

from app.database import SessionLocal
from app.main import date_range
from app.models import Enquiry, Event, Subscriber

PAGES = ["/", "/about", "/services", "/services/book-editing", "/books", "/books/the-drive",
         "/speaking", "/events", "/press-kit", "/reviews", "/contact", "/privacy"]

GOOD = {"name": "Ada Obi", "email": "ada@example.com", "topic": "Speaking",
        "message": "We would like to invite you to our writers' conference.", "consent": "yes"}


def test_all_public_pages_load(client):
    for path in PAGES:
        r = client.get(path)
        assert r.status_code == 200, path
        assert "<title>" in r.text and 'name="description"' in r.text, path


def test_author_photo_on_home_and_about(client):
    assert "img/author-photo.jpg" in client.get("/").text
    assert "img/author-photo.jpg" in client.get("/about").text


def test_books_page_lists_reading_order(client):
    html = client.get("/books").text
    assert html.index("The Drive") < html.index("Upgrade to Explore")


def test_unknown_page_returns_branded_404(client):
    r = client.get("/does-not-exist")
    assert r.status_code == 404 and "Page not found" in r.text


def test_contact_saves_enquiry(client):
    r = client.post("/contact", data=GOOD, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/thanks"
    with SessionLocal() as db:
        assert db.scalar(select(Enquiry).where(Enquiry.email == "ada@example.com")) is not None


def test_contact_requires_consent_and_valid_email(client):
    bad = {**GOOD, "consent": "", "email": "not-an-email"}
    r = client.post("/contact", data=bad)
    assert r.status_code == 400
    assert "tick the box" in r.text and "valid email" in r.text


def test_honeypot_blocks_bots_silently(client):
    r = client.post("/contact", data={**GOOD, "email": "bot@example.com", "website": "http://spam"},
                    follow_redirects=False)
    assert r.status_code == 303
    with SessionLocal() as db:
        assert db.scalar(select(Enquiry).where(Enquiry.email == "bot@example.com")) is None


def test_contact_rate_limit(client):
    codes = [client.post("/contact", data=GOOD, follow_redirects=False).status_code for _ in range(7)]
    assert codes[:5] == [303] * 5 and codes[5] == 429


def test_subscribe_needs_consent_and_ignores_duplicates(client):
    assert client.post("/subscribe", data={"email": "x@example.com"}).status_code == 400
    ok = {"email": "Reader@Example.com", "consent": "yes"}
    assert client.post("/subscribe", data=ok, follow_redirects=False).status_code == 303
    assert client.post("/subscribe", data=ok, follow_redirects=False).status_code == 303
    with SessionLocal() as db:
        assert len(db.scalars(select(Subscriber).where(Subscriber.email == "reader@example.com")).all()) == 1


def test_sitemap_and_robots(client):
    sm = client.get("/sitemap.xml")
    assert sm.status_code == 200 and "/books/the-drive" in sm.text
    assert "Disallow: /admin" in client.get("/robots.txt").text


def test_unpublished_reviews_are_hidden(client):
    assert "[CONFIRM" not in client.get("/reviews").text


def test_admin_requires_login(client):
    r = client.get("/admin/", follow_redirects=False)
    assert r.status_code in (302, 303, 307) and "login" in r.headers["location"]


def test_admin_login_works(client):
    r = client.post("/admin/login", data={"username": "tester", "password": "test-pass"}, follow_redirects=False)
    assert r.status_code in (302, 303)
    assert client.get("/admin/").status_code == 200
    bad = client.post("/admin/login", data={"username": "tester", "password": "wrong"}, follow_redirects=False)
    assert bad.status_code == 400


def test_date_range_formats():
    assert date_range(datetime(2025, 7, 6), datetime(2025, 7, 18)) == "6 to 18 July 2025"
    assert date_range(datetime(2026, 9, 28), datetime(2026, 10, 3)) == "28 September to 3 October 2026"
    assert date_range(datetime(2025, 10, 31), None) == "Friday 31 October 2025"


def test_past_events_show_flyers_and_hidden_draft_does_not(client):
    html = client.get("/events").text
    for name in ("event-upgrade-to-explore", "event-book-launch", "event-beyond-the-book",
                 "event-book-writing-bootcamp"):
        assert name in html
    assert "Past events" in html
    assert "The Lockdown Feast" not in html
    assert "No events are scheduled right now" in html


def test_home_hides_next_event_when_none_upcoming(client):
    assert "Next event" not in client.get("/").text


def test_upcoming_event_appears_on_events_and_home(client):
    start = datetime.now() + timedelta(days=10)
    with SessionLocal() as db:
        ev = Event(title="Test Workshop Upcoming", starts_at=start, ends_at=start + timedelta(days=2),
                   time_label="6pm", location="Online", description="A test.", image="img/event-book-launch.jpg",
                   image_alt="Test flyer", is_published=True)
        db.add(ev)
        db.commit()
        ev_id = ev.id
    try:
        home = client.get("/").text
        assert "Next event" in home and "Test Workshop Upcoming" in home and "Test flyer" in home
        events = client.get("/events").text
        assert events.index("Upcoming") < events.index("Test Workshop Upcoming") < events.index("Past events")
    finally:
        with SessionLocal() as db:
            db.delete(db.get(Event, ev_id))
            db.commit()


def test_event_still_running_counts_as_upcoming(client):
    today = datetime.now()
    with SessionLocal() as db:
        ev = Event(title="Running Right Now Course", starts_at=today - timedelta(days=3),
                   ends_at=today + timedelta(days=3), description="x", is_published=True)
        db.add(ev)
        db.commit()
        ev_id = ev.id
    try:
        html = client.get("/events").text
        assert html.index("Running Right Now Course") < html.index("Past events")
    finally:
        with SessionLocal() as db:
            db.delete(db.get(Event, ev_id))
            db.commit()


def test_reviews_page_shows_text_and_card_images(client):
    html = client.get("/reviews").text
    assert "How you multiplied the book".lower() in html.lower() or "multiplied the book" in html
    assert "review-email" in html and "review-whatsapp" in html
    assert "Peremobo" not in html


def test_services_page_has_banner_and_manuscript_evaluation(client):
    html = client.get("/services").text
    assert "services-flyer" in html and "Manuscript Evaluation" in html
    assert "Ghostwriting" in html
