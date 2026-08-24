import os

os.environ["SCHEDULER_ENABLED"] = "false"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://ipona:ipona_dev@localhost:5432/ipona_test"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only-0000000000"
os.environ["INVITE_CODE"] = "test-invite-2026"
