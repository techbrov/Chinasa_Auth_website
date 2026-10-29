import os

from dotenv import load_dotenv

load_dotenv()  # copies the lines in .env into the environment (never overrides values already set)


class Settings:
    """Reads configuration from environment variables (see .env.example)."""

    def __init__(self) -> None:
        self.site_name = os.getenv("SITE_NAME", "The Seasoned Book Editor")
        self.site_url = os.getenv("SITE_URL", "http://localhost:8000").rstrip("/")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
        self.admin_user = os.getenv("ADMIN_USER", "admin")
        self.admin_password = os.getenv("ADMIN_PASSWORD", "change-me")
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.notify_to = os.getenv("NOTIFY_TO", "")


settings = Settings()
