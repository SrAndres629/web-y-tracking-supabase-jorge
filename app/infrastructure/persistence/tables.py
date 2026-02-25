"""
🗄️ Database Tables Definition.

Defines the schema for SQLAlchemy Core usage.
"""

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text
from sqlalchemy.types import JSON

metadata = MetaData()

events_table = Table(
    "events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("event_id", String, unique=True, nullable=False),
    Column("event_name", String, nullable=False),
    Column("external_id", String, nullable=False, index=True),
    Column("event_time", DateTime, nullable=False, index=True),
    Column("source_url", Text),
    Column("custom_data", JSON),
    Column("utm_source", String),
    Column("utm_medium", String),
    Column("utm_campaign", String),
)

visitors_table = Table(
    "visitors",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("external_id", String, unique=True, nullable=False),
    Column("fbclid", String, index=True),
    Column("fbp", String),
    Column("ip_address", String),
    Column("user_agent", Text),
    Column("source", String),
    Column("utm_source", String),
    Column("utm_medium", String),
    Column("utm_campaign", String),
    Column("country", String),
    Column("city", String),
    Column("created_at", DateTime, nullable=False),
    Column("last_seen", DateTime, nullable=False, index=True),
    Column("visit_count", Integer, default=1),
)
