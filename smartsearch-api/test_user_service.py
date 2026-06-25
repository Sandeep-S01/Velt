from app.services.user_service import create_user, UserCreate
from app.core.database import SessionLocal

db = SessionLocal()
user_data = UserCreate(email='test@example.com', full_name='Test User', password='password123')
user = create_user(db, user_data)
print('User created successfully:', user.id)