from typing import List
from sqlalchemy.orm import Session
from database.models import DbTransaction

class SyncManager:
    """
    Manages local transactional logs for synchronization with external PostgreSQL cloud storage.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_pending_transactions(self) -> List[DbTransaction]:
        """
        Retrieves all transactions that have not yet been synchronized with the cloud.
        """
        return self.db.query(DbTransaction).filter(DbTransaction.synced == False).order_by(DbTransaction.created_at.asc()).all()

    def mark_as_synced(self, transaction_ids: List[str]) -> None:
        """
        Marks a list of transaction IDs as successfully synchronized.
        """
        if not transaction_ids:
            return
            
        self.db.query(DbTransaction).filter(DbTransaction.id.in_(transaction_ids)).update(
            {DbTransaction.synced: True},
            synchronize_session=False
        )
        self.db.commit()

    def clear_synced_transactions(self) -> int:
        """
        Cleans up and deletes all synced logs from the database to prevent storage bloat.
        Returns the count of deleted logs.
        """
        deleted_count = self.db.query(DbTransaction).filter(DbTransaction.synced == True).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count
