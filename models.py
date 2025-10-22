from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import String, Integer, DateTime, Text, BigInteger, select
from datetime import datetime
import config

engine = create_async_engine(config.config.DATABASE_URL, echo=False)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

class UserIdea(Base):
    __tablename__ = 'user_ideas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str] = mapped_column(String(255))
    format: Mapped[str] = mapped_column(String(50), nullable=True)  # обучающий, развлекающий, etc.
    status: Mapped[str] = mapped_column(String(50), default='новая')  # новая, утверждено, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentPlan(Base):
    __tablename__ = 'content_plan'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str] = mapped_column(String(255))
    format: Mapped[str] = mapped_column(String(50))
    publication_date: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50), default='новая')
    content: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content_plan_id: Mapped[int] = mapped_column(Integer)
    message_id: Mapped[int] = mapped_column(BigInteger)  # Telegram message ID
    channel_id: Mapped[int] = mapped_column(BigInteger)  # Telegram channel ID
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    views: Mapped[int] = mapped_column(Integer, nullable=True)
    reactions: Mapped[int] = mapped_column(Integer, nullable=True)
    comments: Mapped[int] = mapped_column(Integer, nullable=True)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
