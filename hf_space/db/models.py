from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    profile_text = Column(Text)
    embedding = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Article(Base):
    __tablename__ = "articles"
    id = Column(String, primary_key=True)
    title = Column(Text)
    summary = Column(Text)
    source = Column(String)
    published = Column(DateTime)
    embedding = Column(Text)

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    article_link = Column(String)
    interaction_type = Column(String) # like, dislike, click
    timestamp = Column(DateTime, default=datetime.utcnow)
