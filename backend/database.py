from config import settings
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from collections.abc import Iterator

database_url = URL.create(
    "postgresql+psycopg",
    username = settings.database_user,
    password = settings.database_password,
    host = settings.database_host,
    port = settings.database_port,
    database = settings.database_name
)

engine = create_engine(database_url, pool_pre_ping=True)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine)

def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session

if __name__ == "__main__":
    with engine.connect() as connection:
        result = connection.execute(
            text('SELECT current_database(), current_user')
        )
        
        print(result.one())
    
    engine.dispose()