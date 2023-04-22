from sqlalchemy import create_engine
from backend.backend.database.secrets import DATABASE_PASSWORD

DATABASE_URL = f'postgresql://postgres:{DATABASE_PASSWORD}@localhost:5432/autogenerations_auth'
ENGINE = create_engine(DATABASE_URL)
