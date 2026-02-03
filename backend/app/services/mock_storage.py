"""
Mock storage for testing without Supabase
"""
from typing import Dict, Any
from uuid import uuid4


# In-memory storage for mock mode
mock_projects: Dict[str, Any] = {}
mock_scenarios: Dict[str, Any] = {}
mock_scenes: Dict[str, Any] = {}
