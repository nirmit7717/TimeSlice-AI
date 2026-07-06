import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from scheduling_system.models.process import Process, ProcessLifecycle

@pytest.fixture(scope="function")
def db_session():
    # Setup in-memory SQLite engine
    engine = create_engine("sqlite:///:memory:")
    
    # Enable SQLite foreign key constraint enforcement
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_process_domain():
    return Process(
        id="test-p1",
        name="Build SQLite Persistence",
        description="Build and test repo CRUD",
        goal="Complete Sprint 3",
        priority=4,
        deadline=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_effort_hours=8.0,
        remaining_effort_hours=8.0,
        status=ProcessLifecycle.ACTIVE,
        tags=["database", "backend"],
        attention_debt=0.0,
        attention_equity=0.0
    )
