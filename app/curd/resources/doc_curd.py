from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.resources.doc import DocumentResource
from app.schemas.resources.doc import DocCreate


class DocCURD:
    @staticmethod
    def get_doc(db: Session, product_id: int) -> Optional[DocumentResource]:
        return db.query(DocumentResource).filter(DocumentResource.id == product_id).first()


    @staticmethod
    def create_doc(db: Session, doc_in: DocCreate) -> DocumentResource:
        data = doc_in.model_dump(exclude_unset=True)
        title = (data.get("title") or "").strip()
        description = data.get("description")
        url = (data.get("url") or "").strip() or None

        # Create a Resource-backed document.
        obj = DocumentResource(title=title, description=description, url=url)
        db.add(obj)
        db.flush()

        # Keep behavior consistent with other resources: attach to a user is handled by /resources.
        return obj


    @staticmethod
    def list_docs(db: Session, skip: int = 0, limit: int = 100) -> List[DocumentResource]:
        return db.query(DocumentResource).offset(skip).limit(limit).all()


    @staticmethod
    def delete_doc(db: Session, doc: DocumentResource) -> None:
        db.delete(doc)
        db.flush()