from sqlalchemy import Column, Integer, String,DateTime,Boolean,Text
# from sqlalchemy.orm import relationship
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    #relationships

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"
    



