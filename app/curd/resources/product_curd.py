from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.resources.product import Product
from app.schemas.resources.product import ProductCreate


class ProductCURD:
    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()
    
    
    @staticmethod
    def create_product(db: Session, product_in: ProductCreate) -> Product:
        data = product_in.model_dump(exclude_unset=True)
        product = Product(**data)
        db.add(product)
        db.commit()
        db.refresh(product)

 

        return product
    
    @staticmethod
    def list_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        products = db.query(Product).offset(skip).limit(limit).all()
        return products
    
    @staticmethod
    def delete_product(db: Session, product: Product) -> None:
        db.delete(product)
        db.commit() 