from app.services.user_service import create_user, UserCreate
from unittest.mock import Mock

# Create a mock database session
mock_db = Mock()
mock_db.query.return_value.filter.return_value.first.return_value = None
mock_db.add = Mock()
mock_db.commit = Mock()
mock_db.refresh = Mock()

# Test data
user_data = UserCreate(
    email="test@example.com",
    full_name="Test User",
    password="password123",
    is_active=True,
    is_verified=False
)

# Test the create_user function
try:
    result = create_user(mock_db, user_data)
    print("SUCCESS: User created without bcrypt error")
    print(f"Result: {result}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()