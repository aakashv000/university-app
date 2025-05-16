from sqlalchemy.orm import Session

from app.db.session import Base, engine
# Import all models to ensure they are registered with SQLAlchemy
from app.models import user, academic, finance

def init_db() -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
def create_initial_data(db: Session) -> None:
    # This function can be used to create initial data for testing
    pass

if __name__ == "__main__":
    init_db()
