# AI Chatbot Application

## Overview

This is a Streamlit-based AI chatbot application that provides a conversational interface supporting multiple AI providers (OpenAI and Anthropic). The application features persistent conversation storage, multi-model support, customizable system prompts, and file upload capabilities for context-aware conversations. Built with Python, it uses SQLAlchemy for database operations and provides a clean, user-friendly interface for interacting with various LLM models.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for the web interface
- **State Management**: Session-based state management using Streamlit's native `st.session_state`
- **Key State Variables**:
  - Message history tracking
  - Chatbot instance management
  - API provider and model selection
  - System prompt customization
  - File upload context handling
  - Current conversation tracking

**Rationale**: Streamlit provides rapid prototyping and deployment for data/AI applications with minimal frontend code. Session state allows for maintaining conversation context across user interactions without complex state management libraries.

### Backend Architecture
- **AI Provider Abstraction**: Unified `ChatBot` class supporting multiple LLM providers
- **Supported Providers**:
  - OpenAI (GPT-5, GPT-4o, GPT-4, GPT-3.5 Turbo)
  - Anthropic (Claude Sonnet 4, Claude Opus 4, Claude 3.5 Sonnet)
- **Provider Pattern**: Strategy pattern implementation allowing runtime switching between AI providers
- **Conversation Management**: History tracking with role-based message storage (user/assistant)

**Rationale**: Provider abstraction allows flexibility to switch between AI services without changing application logic. This design supports cost optimization, provider redundancy, and feature experimentation across different LLM capabilities.

### Data Storage
- **ORM**: SQLAlchemy for database abstraction
- **Database Schema**:
  - `Conversation` table: Stores conversation metadata (id, title, timestamps)
  - `Message` table: Stores individual messages (id, conversation_id, role, content, timestamp)
  - One-to-many relationship between conversations and messages
- **Cascade Operations**: Delete operations cascade to remove all associated messages

**Rationale**: SQLAlchemy provides database-agnostic code that can work with various SQL databases. The relational model naturally represents conversation threads and allows efficient querying of message history. Foreign key relationships ensure data integrity.

### Authentication & Authorization
- **API Key Management**: Environment variable-based API key storage
- **Supported Keys**:
  - `OPENAI_API_KEY` for OpenAI services
  - `ANTHROPIC_API_KEY` for Anthropic services
  - `DATABASE_URL` for database connection

**Rationale**: Environment variables keep sensitive credentials out of code repository and allow easy configuration across different deployment environments. No user authentication is implemented, suggesting single-user or trusted environment deployment.

### Design Patterns
- **Singleton-like Pattern**: DatabaseManager initialized once per session
- **Factory Pattern**: Chatbot initialization based on provider selection
- **Repository Pattern**: DatabaseManager encapsulates all database operations
- **Model-View Pattern**: Separation between UI (Streamlit), business logic (ChatBot), and data layer (DatabaseManager)

## External Dependencies

### AI Service Providers
- **OpenAI API**: Primary LLM provider supporting GPT model family
- **Anthropic API**: Alternative provider for Claude model family
- **Purpose**: Generate conversational responses based on user input and context

### Database
- **Connection**: SQLAlchemy-compatible database via `DATABASE_URL` environment variable
- **Supported Databases**: PostgreSQL, MySQL, SQLite, or any SQLAlchemy-supported database
- **Purpose**: Persistent storage of conversation history and messages

### Python Packages
- **streamlit**: Web application framework
- **sqlalchemy**: ORM and database toolkit
- **openai**: Official OpenAI Python client
- **anthropic**: Official Anthropic Python client (implied)
- **datetime**: Standard library for timestamp management
- **json**: Standard library for potential data serialization
- **os**: Environment variable access

### Configuration Requirements
- Environment variables must be set before application startup
- Database must be accessible and properly configured
- API keys must be valid and have appropriate service access