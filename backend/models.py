from sqlalchemy import Column, Integer, String, Text, Float
from backend.db import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    content = Column(Text)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    query = Column(Text)
    answer = Column(Text)
    actions = Column(Text)