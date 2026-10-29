import hmac

from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from .config import settings
from .database import engine
from .models import Book, Certification, Enquiry, Event, Page, Review, Service, Subscriber


class AdminAuth(AuthenticationBackend):
    async def login(self, request) -> bool:
        form = await request.form()
        user = str(form.get("username", "")).encode()
        pwd = str(form.get("password", "")).encode()
        ok = hmac.compare_digest(user, settings.admin_user.encode()) and hmac.compare_digest(
            pwd, settings.admin_password.encode()
        )
        if ok:
            request.session.update({"admin": True})
        return ok

    async def logout(self, request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request) -> bool:
        return bool(request.session.get("admin"))


class PageAdmin(ModelView, model=Page):
    name_plural = "Pages"
    column_list = [Page.title, Page.slug]
    can_create = False
    can_delete = False


class ServiceAdmin(ModelView, model=Service):
    name_plural = "Services"
    column_list = [Service.title, Service.sort_order, Service.is_published]


class BookAdmin(ModelView, model=Book):
    name_plural = "Books"
    column_list = [Book.title, Book.kind, Book.reading_order, Book.is_published]


class CertificationAdmin(ModelView, model=Certification):
    name_plural = "Certifications"
    column_list = [Certification.title, Certification.issuer, Certification.date_label]


class ReviewAdmin(ModelView, model=Review):
    name_plural = "Reviews"
    column_list = [Review.client_name, Review.permission_confirmed, Review.is_published]


class EventAdmin(ModelView, model=Event):
    name_plural = "Events"
    column_list = [Event.title, Event.starts_at, Event.is_published]


class EnquiryAdmin(ModelView, model=Enquiry):
    name_plural = "Enquiries"
    column_list = [Enquiry.created_at, Enquiry.name, Enquiry.email, Enquiry.topic]
    column_default_sort = [(Enquiry.created_at, True)]
    can_create = False
    can_edit = False


class SubscriberAdmin(ModelView, model=Subscriber):
    name_plural = "Subscribers"
    column_list = [Subscriber.email, Subscriber.created_at]
    can_create = False
    can_edit = False


def setup_admin(app) -> None:
    admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key=settings.secret_key),
                  title="Site admin")
    for view in (PageAdmin, ServiceAdmin, BookAdmin, CertificationAdmin, ReviewAdmin,
                 EventAdmin, EnquiryAdmin, SubscriberAdmin):
        admin.add_view(view)
