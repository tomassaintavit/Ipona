import os

os.environ["SCHEDULER_ENABLED"] = "false"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://ipona:ipona_dev@localhost:5432/ipona_test"
