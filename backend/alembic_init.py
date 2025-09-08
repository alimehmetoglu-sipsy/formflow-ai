#!/usr/bin/env python3
"""Initialize database schema with all required columns"""

from sqlalchemy import create_engine, text
from app.config import settings
import sys

def add_missing_columns():
    """Add missing columns to the users table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check and add missing columns
        columns_to_add = [
            ("subscription_tier", "VARCHAR DEFAULT 'free'"),
            ("subscription_status", "VARCHAR DEFAULT 'inactive'"),
            ("subscription_id", "VARCHAR"),
            ("subscription_expires_at", "TIMESTAMP"),
            ("onboarding_completed", "BOOLEAN DEFAULT FALSE"),
            ("typeform_connected", "BOOLEAN DEFAULT FALSE"),
            ("typeform_api_key", "VARCHAR")
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                # Check if column exists
                result = conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='{column_name}'
                """))
                
                if not result.fetchone():
                    # Add column if it doesn't exist
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"))
                    conn.commit()
                    print(f"✅ Added column: {column_name}")
                else:
                    print(f"✓ Column already exists: {column_name}")
                    
            except Exception as e:
                print(f"❌ Error adding column {column_name}: {e}")
                
        print("\n✨ Database schema updated successfully!")

if __name__ == "__main__":
    try:
        add_missing_columns()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)