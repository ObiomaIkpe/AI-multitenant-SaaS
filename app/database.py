import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()


SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{os.environ.get('DB_USERNAME')}:"
    f"{os.environ.get('DB_PASSWORD')}@"
    f"{os.environ.get('DB_HOST')}:"
    f"{os.environ.get('DB_PORT')}/"
    f"{os.environ.get('DB_DATABASE')}"
)


engine = create_engine(SQLALCHEMY_DATABASE_URL)

# --- 3. Session Maker ---
# The SessionLocal object is a factory for creating Session objects.
# We set autoflush=False and autocommit=False to manage transactions manually.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 4. Base Declaration ---
# Base is the foundation for creating all your models (the Python classes 
# that represent your database tables).
Base = declarative_base()

#