import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import DjangoBase
from app.models import Game, PriceEntry, PriceHistory


TEST_DATABASE_URL = 'sqlite:///:memory:'

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={'check_same_thread': False})
    DjangoBase.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()