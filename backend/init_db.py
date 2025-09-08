#!/usr/bin/env python
"""Initialize database with all tables"""

from app.database import engine, Base
from app.models.user import User
from app.models.form import FormSubmission, Dashboard

print("Creating database tables...")

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ Database tables created successfully!")
print("Tables created:")
print("  - users")
print("  - form_submissions")
print("  - dashboards")