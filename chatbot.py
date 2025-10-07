import os
import sys
from typing import List, Dict, Any
from datetime import datetime

class ChatBot:
    """AI Chatbot class supporting OpenAI and Anthropic APIs"""
    
    # Available models for each provider
    OPENAI_MODELS = {
        "GPT-5": "gpt-5",
        "GPT-4o": "gpt-4o",
        "GPT-4": "gpt-4",
        "GPT-3.5 Turbo": "gpt-3.5-turbo"
    }
    
    ANTHROPIC_MODELS = {
        "Claude Sonnet 4": "claude-sonnet-4-20250514",
        "Claude Opus 4": "claude-opus-4-20250514",
        "Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022"
    }
    
    def __init__(self, provider: str = "openai", model: str = None, system_prompt: str = None):
        """
        Initialize the chatbot with specified provider and model
        
        Args:
            provider (str): Either "openai" or "anthropic"
            model (str): Specific model to use (optional)
            system_prompt (str): Custom system prompt (optional)
        """
        self.provider = provider.lower()
        self.conversation_history = []
        self.client = None
        self.model = model
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        
        if self.provider == "openai":
            self._initialize_openai()
        elif self.provider == "anthropic":
            self._initialize_anthropic()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _initialize_openai(self):
        """Initialize OpenAI client and model"""
        try:
            from openai import OpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            self.client = OpenAI(api_key=api_key)
            
            # Set model if not provided
            if not self.model:
                self.model = "gpt-5"
            
            # Test the connection
            self._test_openai_connection()
            
        except ImportError:
            raise ImportError("OpenAI package is required. Please install it.")
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI: {str(e)}")
    
    def _initialize_anthropic(self):
        """Initialize Anthropic client and model"""
        try:
            from anthropic import Anthropic
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
            self.client = Anthropic(api_key=api_key)
            
            # Set model if not provided
            if not self.model:
                self.model = "claude-sonnet-4-20250514"
            
            # Test the connection
            self._test_anthropic_connection()
            
        except ImportError:
            raise ImportError("Anthropic package is required. Please install it.")
        except Exception as e:
            raise Exception(f"Failed to initialize Anthropic: {str(e)}")
    
    def _test_openai_connection(self):
        """Test OpenAI API connection"""
        pass
    
    def _test_anthropic_connection(self):
        """Test Anthropic API connection"""
        pass
    
    def get_response(self, user_message: str) -> str:
        """
        Get AI response for user message
        
        Args:
            user_message (str): User's input message
            
        Returns:
            str: AI generated response
        """
        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user", 
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            if self.provider == "openai":
                response = self._get_openai_response()
            elif self.provider == "anthropic":
                response = self._get_anthropic_response()
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Add AI response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            # Add error to history for context
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg,
                "timestamp": datetime.now().isoformat()
            })
            raise Exception(error_msg)
    
    def _get_openai_response(self) -> str:
        """Get response from OpenAI API"""
        try:
            # Prepare messages for OpenAI format
            messages = [{"role": "system", "content": self.system_prompt}]
            for msg in self.conversation_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=2048
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _get_anthropic_response(self) -> str:
        """Get response from Anthropic API"""
        try:
            # Prepare messages for Anthropic format
            messages = []
            for msg in self.conversation_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=self.system_prompt,
                messages=messages
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get current conversation history"""
        return self.conversation_history.copy()
    
    def get_model_info(self) -> str:
        """Get current model information"""
        return f"{self.provider.upper()} - {self.model}"
    
    def get_message_count(self) -> int:
        """Get total number of messages in conversation"""
        return len([msg for msg in self.conversation_history if msg["role"] in ["user", "assistant"]])
