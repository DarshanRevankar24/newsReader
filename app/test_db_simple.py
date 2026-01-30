import sys
import os
sys.path.append(os.getcwd())

try:
    from db.session import SessionLocal
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
