from app.database.connection import engine
from app.database.models import Base

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("✅ All tables created successfully!")