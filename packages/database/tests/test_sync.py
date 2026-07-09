import pytest
from database.repositories.process_repo import ProcessRepository
from database.sync.sync_manager import SyncManager

def test_repository_atomic_sync_logging(db_session, sample_process_domain):
    process_repo = ProcessRepository(db_session)
    sync_manager = SyncManager(db_session)

    # 1. Initially no sync transactions
    pending = sync_manager.get_pending_transactions()
    assert len(pending) == 0

    # 2. Create Process -> Should write transaction INSERT
    created = process_repo.create(sample_process_domain)
    pending = sync_manager.get_pending_transactions()
    assert len(pending) == 1
    assert pending[0].action == "INSERT"
    assert pending[0].table_name == "processes"
    assert pending[0].record_id == "test-p1"
    assert pending[0].synced is False

    # 3. Update Process -> Should write transaction UPDATE
    created.name = "Updated persistence name"
    process_repo.update(created)
    pending = sync_manager.get_pending_transactions()
    assert len(pending) == 2
    assert pending[1].action == "UPDATE"
    assert pending[1].record_id == "test-p1"

    # 4. Mark first transaction as synced
    first_tx_id = pending[0].id
    second_tx_id = pending[1].id
    sync_manager.mark_as_synced([first_tx_id])
    
    # Reload and check
    pending = sync_manager.get_pending_transactions()
    assert len(pending) == 1
    assert pending[0].id == second_tx_id # Only the UPDATE is pending now

    # 5. Clear synced transactions
    deleted_count = sync_manager.clear_synced_transactions()
    assert deleted_count == 1  # The first INSERT transaction is deleted from logs
