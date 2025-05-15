from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models import user, finance

def init_db() -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
