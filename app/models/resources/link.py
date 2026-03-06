from sqlalchemy import Column, Integer, String, ForeignKey

from app.models.resource import Resource, ResourceType


class LinkResource(Resource):
    __tablename__ = "link_resources"

    id = Column(Integer, ForeignKey("resources.id"), primary_key=True)
    url = Column(String(1000), unique=True, index=True, nullable=False)
    source = Column(String(200), nullable=True)
    category = Column(String(100), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.LINK,
    }
