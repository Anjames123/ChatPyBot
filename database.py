import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")

class DatabaseManager:
    """Manage database connections and operations"""
    
    def __init__(self):
        # Use DATABASE_URL if provided; otherwise default to a local SQLite file.
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            database_url = f"sqlite:///./chatbot.db"

        # For SQLite ensure check_same_thread is disabled for multithreaded webservers
        connect_args = {}
        if database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

        self.engine = create_engine(database_url, connect_args=connect_args)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def create_conversation(self, title: str = "New Conversation") -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(title=title)
        self.session.add(conversation)
        self.session.commit()
        return conversation
    
    def get_conversation(self, conversation_id: int) -> Conversation:
        """Get a conversation by ID"""
        return self.session.query(Conversation).filter_by(id=conversation_id).first()
    
    def get_all_conversations(self):
        """Get all conversations ordered by updated_at"""
        return self.session.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    
    def add_message(self, conversation_id: int, role: str, content: str) -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.session.add(message)
        
        # Update conversation's updated_at timestamp
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        self.session.commit()
        return message
    
    def get_conversation_messages(self, conversation_id: int):
        """Get all messages for a conversation"""
        return self.session.query(Message).filter_by(
            conversation_id=conversation_id
        ).order_by(Message.timestamp.asc()).all()
    
    def delete_conversation(self, conversation_id: int):
        """Delete a conversation and all its messages"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self.session.delete(conversation)
            self.session.commit()
            return True
        return False
    
    def update_conversation_title(self, conversation_id: int, title: str):
        """Update conversation title"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        return False
    
    def close(self):
        """Close the database session"""
        self.session.close()