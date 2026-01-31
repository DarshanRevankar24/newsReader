import sys
import os

# Ensure app/ is in pythonpath
sys.path.append(os.getcwd())

try:
    import db
    print(f"db file: {getattr(db, '__file__', 'unknown')}")
    try:
        import db.core
        print(f"db.core file: {getattr(db.core, '__file__', 'unknown')}")
        print(f"db.core attributes: {dir(db.core)}")
    except ImportError as e:
        print(f"Could not import db.core: {e}")

    from db.core import engine
    from db.models import Base
    from agents.profile_agent import update_user_profile
    
    print("Imports successful!")

    def test_profile_update():
        print("Creating tables if not exist...")
        Base.metadata.create_all(bind=engine)
        
        print("Updating user profile...")
        try:
            update_user_profile(user_id=1, new_signal="I love technology and space.")
            print("Profile updated successfully!")
        except Exception as e:
            print(f"Error updating profile: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        test_profile_update()

except Exception as e:
    print(f"Top level error: {e}")
    import traceback
    traceback.print_exc()
