from sqlalchemy.orm import Session

class BaseRepository:
    """Base class for repositories, storing the SQL database session."""
    def __init__(self, db: Session):
        self.db = db
