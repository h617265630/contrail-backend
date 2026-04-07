from datetime import datetime
import json

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.db.database import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)

    event_id = Column(String(128), nullable=True, index=True)
    event_type = Column(String(128), nullable=True, index=True)

    payload_json = Column(Text, nullable=False, default="{}")
    headers_json = Column(Text, nullable=False, default="{}")

    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    processed = Column(Boolean, nullable=False, default=False)
    error = Column(Text, nullable=True)

    def set_payload(self, payload: object):
        self.payload_json = json.dumps(payload, ensure_ascii=False)

    def set_headers(self, headers: object):
        self.headers_json = json.dumps(headers, ensure_ascii=False)
