from supabase import create_client, Client
from app.utils.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Check mock mode from settings
MOCK_MODE = settings.mock_mode if hasattr(settings, 'mock_mode') else False


class MockClient:
    """Mock Supabase client for testing"""
    def __init__(self):
        self._tables = {}

    def table(self, name):
        """Return a mock table object"""
        if name not in self._tables:
            self._tables[name] = MockTable(name)
        return self._tables[name]


class MockTable:
    def __init__(self, name):
        self.name = name
        self._data = []
        self._select_filters = {}
        self._update_data = {}

    def select(self, *columns):
        self._select_filters['columns'] = columns
        return self

    def insert(self, data):
        """Insert data and return mock response"""
        import uuid
        item = {"id": str(uuid.uuid4()), **data}
        self._data.append(item)
        return MockExecuteResponse([item])

    def update(self, data):
        self._update_data = data
        return self

    def delete(self):
        return self

    def eq(self, column, value):
        self._select_filters[f'eq_{column}'] = value
        return self

    def in_(self, column, values):
        self._select_filters[f'in_{column}'] = values
        return self

    def order(self, column):
        self._select_filters['order'] = column
        return self

    def execute(self):
        """Execute query and return mock response"""
        return MockExecuteResponse(self._data)


class MockExecuteResponse:
    def __init__(self, data):
        self.data = data


class SupabaseService:
    def __init__(self):
        self.client: Optional[Client] = None
        self.admin_client: Optional[Client] = None
        self._is_mock = MOCK_MODE
        self._connection_failed = False

    def connect(self):
        """Initialize Supabase clients"""
        if self._is_mock or self._connection_failed:
            return
        try:
            self.client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            self.admin_client = create_client(
                settings.supabase_url,
                settings.supabase_service_key
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.warning(f"Could not connect to Supabase: {e}. Falling back to mock mode.")
            self._connection_failed = True
            self._is_mock = True

    def get_client(self) -> Client:
        """Get regular Supabase client"""
        if self._is_mock or self._connection_failed:
            return MockClient()
        if self.client is None:
            self.connect()
        if self._connection_failed:
            return MockClient()
        return self.client

    def get_admin_client(self) -> Client:
        """Get admin Supabase client (bypasses RLS)"""
        if self._is_mock or self._connection_failed:
            return MockClient()
        if self.admin_client is None:
            self.connect()
        if self._connection_failed:
            return MockClient()
        return self.admin_client


# Singleton instance
supabase_service = SupabaseService()


def get_supabase() -> Client:
    """Dependency injection for FastAPI"""
    return supabase_service.get_client()


def get_supabase_admin() -> Client:
    """Get admin client for background tasks"""
    return supabase_service.get_admin_client()


def is_using_mock() -> bool:
    """Check if using mock mode"""
    return MOCK_MODE or supabase_service._connection_failed


__all__ = ["get_supabase", "get_supabase_admin", "MockClient", "MOCK_MODE", "is_using_mock"]
