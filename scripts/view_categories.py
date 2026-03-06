"""
Script to view hierarchical categories from the database.
Run this script from the backend directory:
    python -m scripts.view_categories
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base

# Import all models to resolve SQLAlchemy relationships
import app.models.rbac.associations
import app.models.rbac.user
import app.models.rbac.role
import app.models.rbac.permission
import app.models.category
import app.models.resource
import app.models.resources.video
import app.models.resources.doc
import app.models.resources.article
import app.models.user_resource
import app.models.user_learning_path
import app.models.learning_path
import app.models.path_item
import app.models.progress

from app.models.category import Category


def display_categories():
    """Display all categories in hierarchical structure"""
    db = SessionLocal()
    
    try:
        print("\n📁 Category Hierarchy\n")
        print("=" * 80)
        
        # Get all parent categories (level 0)
        parent_categories = db.query(Category).filter(Category.level == 0).order_by(Category.id).all()
        
        for parent in parent_categories:
            # Display parent category
            print(f"\n{parent.name}")
            print(f"  └─ Code: {parent.code}")
            print(f"  └─ ID: {parent.id}")
            print(f"  └─ Level: {parent.level}")
            print(f"  └─ Is Leaf: {parent.is_leaf}")
            
            # Get child categories
            children = db.query(Category).filter(
                Category.parent_id == parent.id
            ).order_by(Category.id).all()
            
            if children:
                print(f"  └─ Children ({len(children)}):")
                for i, child in enumerate(children, 1):
                    is_last = i == len(children)
                    prefix = "    └─" if is_last else "    ├─"
                    print(f"{prefix} {child.name} (id={child.id}, code={child.code})")
        
        print("\n" + "=" * 80)
        
        # Summary statistics
        total = db.query(Category).count()
        parents = db.query(Category).filter(Category.level == 0).count()
        children = db.query(Category).filter(Category.level == 1).count()
        
        print(f"\n📊 Statistics:")
        print(f"  Total categories: {total}")
        print(f"  Parent categories: {parents}")
        print(f"  Child categories: {children}")
        
        # Test get_full_path method
        print(f"\n🔍 Sample Full Paths:")
        sample_children = db.query(Category).filter(Category.level == 1).limit(3).all()
        for cat in sample_children:
            print(f"  {cat.name}: {cat.get_full_path()}")
        
        print()
        
    except Exception as e:
        print(f"\n❌ Error displaying categories: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    display_categories()
