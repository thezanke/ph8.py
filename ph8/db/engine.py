from sqlalchemy import create_engine

DATABASE_URI = "postgresql+psycopg2://postgres:postgres@localhost:5555/postgres"

engine = create_engine(DATABASE_URI)
