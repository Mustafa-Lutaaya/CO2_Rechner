from models.models import Item, Category # Imports the CO2 model used for querying the database
from sqlalchemy.orm import Session, joinedload # Imports SQLAlchemy Session for DB operations, and loading strategies for relationships

# SQL OPERATIONS
class SQLCRUD:
    # Function to get all items from the database with active database session as parameter
    def fetch_items_from_db(self, db: Session):
        return (db.query(Item)
            .options(joinedload(Item.category))  # Eager loads category
            .order_by(Item.category_id.asc(), Item.name.asc())  # Sorts by category_id
            .all()
        )
    
    def fetch_categories_from_db(self, db: Session):
        return (db.query(Category)
            .options(joinedload(Category.items))  # Eager loads items
            .order_by(Category.name.asc())
            .all()
        )
