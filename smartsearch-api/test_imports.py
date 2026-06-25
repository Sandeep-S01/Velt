import sys
import os

# Add the smartsearch-api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'smartsearch-api'))

try:
    # Try importing the main application
    from app.main import app
    print("SUCCESS: Main application imported successfully!")

    # Check if we can import key modules
    from app.core.config import settings
    print(f"SUCCESS: Config loaded. Project: {settings.PROJECT_NAME}")

    from app.core.database import engine, SessionLocal
    print("SUCCESS: Database module imported")

    from app.utils.security import authenticate_user, create_access_token
    print("SUCCESS: Security utilities imported")

    print("\nAll critical imports working correctly!")

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()