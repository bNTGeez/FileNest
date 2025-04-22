import os
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL) # create a synchronous SQLAlchemy Engine, which knows how to talk to Postgres

# this will manage transactions, and provide a session for database operations
SessionLocal = sessionmaker(
  autocommit=False, # I control when transactions are committed
  autoflush=False, # I control when pending changes are flushed to the database
  bind=engine # tell SQLAlchemy to use the engine we created
)

# this is a base class for all database models
Base = declarative_base()

def get_db():
  db = SessionLocal() # create a new session
  try:
    yield db # route function runs
  finally:
    db.close() # close the session after the route function runs
