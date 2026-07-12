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


def test_conflict_detection_and_resolution(db_session, sample_process_domain):
    process_repo = ProcessRepository(db_session)
    sync_manager = SyncManager(db_session)

    # 1. Clear any active conflicts cache
    from database.sync.sync_manager import _conflicts_cache
    _conflicts_cache.clear()

    # 2. Create local record
    process_repo.create(sample_process_domain)

    # 3. Create a local pending update to trigger conflict check later
    sample_process_domain.name = "Local Modified Name"
    process_repo.update(sample_process_domain)

    # Verify we have 2 local transactions now (INSERT + UPDATE)
    pending = sync_manager.get_pending_transactions()
    assert len(pending) == 2

    # 4. Pull from cloud with a different name to trigger conflict
    cloud_records = [
        {
            "tableName": "processes",
            "recordId": sample_process_domain.id,
            "updatedAt": "2026-07-12T12:00:00Z",
            "payload": {
                "name": "Cloud Conflicting Name",
                "description": "Cloud desc",
                "goal": "Cloud goal",
                "priority": 5,
                "deadline": "2026-07-17T00:00:00Z",
                "estimatedEffortHours": 10.0,
                "remainingEffortHours": 10.0,
                "status": "Active",
                "progress": 0.0
            }
        }
    ]

    conflicts = sync_manager.pull_from_cloud(cloud_records)
    assert len(conflicts) == 1
    assert conflicts[0].record_id == sample_process_domain.id
    assert conflicts[0].local_value == "Local Modified Name"
    assert conflicts[0].cloud_value == "Cloud Conflicting Name"

    # Verify conflicts exist in manager list
    assert len(sync_manager.get_conflicts()) == 1

    # 5. Resolve conflict using "cloud" resolution
    success = sync_manager.resolve_conflict(
        conflict_id=f"processes:{sample_process_domain.id}",
        resolution="cloud",
        cloud_payload=cloud_records[0]["payload"]
    )
    assert success is True

    # 6. Verify conflict is cleared and local record is updated to cloud version
    assert len(sync_manager.get_conflicts()) == 0
    updated_local = process_repo.get(sample_process_domain.id)
    assert updated_local.name == "Cloud Conflicting Name"

    # Also verify local pending transactions are marked as synced (so we don't overwrite the cloud)
    assert len(sync_manager.get_pending_transactions()) == 0

