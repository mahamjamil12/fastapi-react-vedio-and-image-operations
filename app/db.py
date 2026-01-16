from _collections_abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase,relationship
from datetime import datetime


DATABASE_URL = "sqlite+aiosqlite:///./test.db"


class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "posts"
# as_uuid = True means : when we create a new post a unique id will be generated
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type= Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Creating the database
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# it search the database engine and creates all the tables and creates db
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



# it will get a session which will allow you to access the db and read and write from it 
# asyncronously
async def get_async_session() -> AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        yield session
