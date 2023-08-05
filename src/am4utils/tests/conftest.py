import pytest
from am4utils.db import init, reset

pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    init(db_name='main_test')
    reset()
    yield