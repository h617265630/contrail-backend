"""
Script to insert hierarchical categories into the database.
Run this script from the backend directory:
    python -m scripts.insert_hierarchical_categories
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base

# Import all models to resolve SQLAlchemy relationships
# Import in order to avoid circular dependency issues
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
import app.models.user_learning_path  # Import association table
import app.models.learning_path
import app.models.path_item
import app.models.progress

from app.models.category import Category


def create_category(db: Session, name: str, code: str, parent_id: int = None, level: int = 0, is_leaf: bool = True):
    """Create a category if it doesn't exist"""
    existing = db.query(Category).filter(Category.code == code).first()
    if existing:
        print(f"  ⏭️  Category '{name}' already exists (id={existing.id})")
        return existing
    
    category = Category(
        name=name,
        code=code,
        parent_id=parent_id,
        level=level,
        is_leaf=is_leaf,
        is_system=True,
        description=f"{name} category"
    )
    db.add(category)
    db.flush()  # Get the ID without committing
    print(f"  ✅ Created category '{name}' (id={category.id}, level={level})")
    return category


def insert_hierarchical_categories():
    """Insert all hierarchical categories"""
    db = SessionLocal()
    
    try:
        print("\n🚀 Starting hierarchical category insertion...\n")
        
        # Define the hierarchical structure
        categories_data = [
            {
                "name": "🚀 Business & Productivity",
                "code": "business_productivity",
                "children": [
                    {"name": "Startups", "code": "startups"},
                    {"name": "Entrepreneurship", "code": "entrepreneurship"},
                    {"name": "Marketing", "code": "marketing"},
                    {"name": "Finance", "code": "finance"},
                    {"name": "Productivity", "code": "productivity"},
                    {"name": "Remote Work", "code": "remote_work"},
                ]
            },
            {
                "name": "🏠 Lifestyle",
                "code": "lifestyle",
                "children": [
                    {"name": "Home Decor", "code": "home_decor"},
                    {"name": "Organization", "code": "organization"},
                    {"name": "Minimalism", "code": "minimalism"},
                    {"name": "Travel", "code": "travel"},
                    {"name": "Wellness", "code": "wellness"},
                    {"name": "Fitness", "code": "fitness"},
                ]
            },
            {
                "name": "🍳 Food & Cooking",
                "code": "food_cooking",
                "children": [
                    {"name": "Recipes", "code": "recipes"},
                    {"name": "Baking", "code": "baking"},
                    {"name": "Healthy eating", "code": "healthy_eating"},
                    {"name": "Meal prep", "code": "meal_prep"},
                ]
            },
            {
                "name": "🎮 Entertainment",
                "code": "entertainment",
                "children": [
                    {"name": "Gaming", "code": "gaming"},
                    {"name": "Movies", "code": "movies"},
                    {"name": "Anime", "code": "anime"},
                    {"name": "Music", "code": "music"},
                    {"name": "Pop Culture", "code": "pop_culture"},
                ]
            },
            {
                "name": "🧠 Personal Development",
                "code": "personal_development",
                "children": [
                    {"name": "Habits", "code": "habits"},
                    {"name": "Psychology", "code": "psychology"},
                    {"name": "Motivation", "code": "motivation"},
                ]
            },
        ]
        
        # Insert categories
        for parent_data in categories_data:
            print(f"\n📁 Processing parent category: {parent_data['name']}")
            
            # Create parent category (not a leaf since it has children)
            parent = create_category(
                db=db,
                name=parent_data['name'],
                code=parent_data['code'],
                parent_id=None,
                level=0,
                is_leaf=False
            )
            
            # Create child categories
            for child_data in parent_data['children']:
                create_category(
                    db=db,
                    name=child_data['name'],
                    code=child_data['code'],
                    parent_id=parent.id,
                    level=1,
                    is_leaf=True
                )
        
        # Commit all changes
        db.commit()
        print("\n✅ All categories inserted successfully!\n")
        
        # Display summary
        total_categories = db.query(Category).count()
        parent_categories = db.query(Category).filter(Category.level == 0).count()
        child_categories = db.query(Category).filter(Category.level == 1).count()
        
        print("📊 Summary:")
        print(f"  Total categories: {total_categories}")
        print(f"  Parent categories (level 0): {parent_categories}")
        print(f"  Child categories (level 1): {child_categories}")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error inserting categories: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    insert_hierarchical_categories()
