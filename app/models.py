from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Page(Base):
    """Editable text pages: about, speaking, press-kit, privacy."""
    __tablename__ = "pages"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    meta_description: Mapped[str] = mapped_column(String(300), default="")
    body_html: Mapped[str] = mapped_column(Text, default="")

    def __str__(self) -> str:
        return self.title


class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    summary: Mapped[str] = mapped_column(String(300))
    details_html: Mapped[str] = mapped_column(Text, default="")
    price_note: Mapped[str] = mapped_column(String(200), default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=100)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    def __str__(self) -> str:
        return self.title


class Book(Base):
    """kind = 'authored' (her own books) or 'edited' (books she worked on)."""
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    subtitle: Mapped[str] = mapped_column(String(300), default="")
    kind: Mapped[str] = mapped_column(String(20), default="authored", index=True)
    author_name: Mapped[str] = mapped_column(String(160), default="Chinasa Elukposi")
    blurb: Mapped[str] = mapped_column(Text, default="")
    cover_image: Mapped[str] = mapped_column(String(200), default="")
    reading_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    excerpt_html: Mapped[str] = mapped_column(Text, default="")
    buy_url: Mapped[str] = mapped_column(String(500), default="")
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    def __str__(self) -> str:
        return self.title


class Certification(Base):
    __tablename__ = "certifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    issuer: Mapped[str] = mapped_column(String(200))
    date_label: Mapped[str] = mapped_column(String(80))
    image: Mapped[str] = mapped_column(String(200), default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=100)

    def __str__(self) -> str:
        return self.title


class Review(Base):
    """Client testimonials. Publish only with the client's written permission."""
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    client_name: Mapped[str] = mapped_column(String(160))
    client_detail: Mapped[str] = mapped_column(String(200), default="")
    quote: Mapped[str] = mapped_column(Text)
    image: Mapped[str] = mapped_column(String(200), default="")
    image_alt: Mapped[str] = mapped_column(String(300), default="")
    permission_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    def __str__(self) -> str:
        return self.client_name


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    time_label: Mapped[str] = mapped_column(String(120), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    image: Mapped[str] = mapped_column(String(200), default="")
    image_alt: Mapped[str] = mapped_column(String(300), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    link_url: Mapped[str] = mapped_column(String(500), default="")
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    def __str__(self) -> str:
        return self.title


class Enquiry(Base):
    """Messages from the contact form (includes speaking requests)."""
    __tablename__ = "enquiries"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(254))
    topic: Mapped[str] = mapped_column(String(60))
    message: Mapped[str] = mapped_column(Text)
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __str__(self) -> str:
        return f"{self.name} ({self.topic})"


class Subscriber(Base):
    __tablename__ = "subscribers"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __str__(self) -> str:
        return self.email
