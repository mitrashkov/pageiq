from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models import ApiKey

def migrate_api_key_prefixes():
    """Populate key_prefix for existing API keys if they are empty"""
    db = SessionLocal()
    try:
        # This is a bit tricky since we don't have the plain key for existing hashes.
        # But for a prototype-to-production migration, we might just have to 
        # ask users to rotate or use a dummy prefix if we can't recover the plain key.
        # However, if we're in a fresh state, this isn't an issue.
        
        # If we have any keys with empty prefixes, we can't easily recover the prefix 
        # from the hash (bcrypt is one-way).
        
        keys_to_fix = db.query(ApiKey).filter(ApiKey.key_prefix == "").all()
        if not keys_to_fix:
            print("No API keys with empty prefixes found.")
            return

        print(f"Found {len(keys_to_fix)} keys with empty prefixes.")
        print("Note: Cannot recover prefixes from hashed keys. These keys will use fallback lookup.")
        
    finally:
        db.close()

if __name__ == "__main__":
    migrate_api_key_prefixes()
