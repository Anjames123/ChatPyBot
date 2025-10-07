import streamlit as st
import os
from datetime import datetime
from chatbot import ChatBot

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "api_provider" not in st.session_state:
        st.session_state.api_provider = "openai"

def display_chat_messages():
    """Display all chat messages in the conversation"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"*{message['timestamp']}*")

def main():
    initialize_session_state()
    
    st.title("🤖 AI Chatbot")
    st.markdown("Chat with AI using OpenAI or Anthropic models")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Provider selection
        api_provider = st.selectbox(
            "Choose AI Provider:",
            ["openai", "anthropic"],
            index=0 if st.session_state.api_provider == "openai" else 1,
            key="api_provider_select"
        )
        
        # Update session state if provider changed
        if api_provider != st.session_state.api_provider:
            st.session_state.api_provider = api_provider
            st.session_state.chatbot = None  # Reset chatbot instance
        
        # Initialize chatbot if not exists or provider changed
        if st.session_state.chatbot is None:
            try:
                st.session_state.chatbot = ChatBot(provider=api_provider)
                st.success(f"✅ Connected to {api_provider.upper()}")
            except Exception as e:
                error_str = str(e)
                st.error(f"❌ Failed to connect to {api_provider.upper()}")
                
                # Provide helpful guidance based on error type
                if "429" in error_str or "quota" in error_str.lower():
                    st.warning("**API Quota Exceeded**")
                    st.info(f"Your {api_provider.upper()} API key has exceeded its quota or rate limit. Please:\n"
                            f"- Check your API usage at {'https://platform.openai.com/usage' if api_provider == 'openai' else 'https://console.anthropic.com/'}\n"
                            f"- Add billing information to your account\n"
                            f"- Or try the other AI provider option")
                elif "api key" in error_str.lower() or "not found" in error_str.lower():
                    st.info(f"Please make sure your {api_provider.upper()}_API_KEY is correctly configured in Secrets.")
                else:
                    st.info(f"Error details: {error_str}")
        
        # Display current model info
        if st.session_state.chatbot:
            st.info(f"**Model:** {st.session_state.chatbot.get_model_info()}")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation", type="secondary"):
            st.session_state.messages = []
            if st.session_state.chatbot:
                st.session_state.chatbot.clear_history()
            st.rerun()
        
        # Display message count
        if st.session_state.messages:
            st.metric("Messages", len(st.session_state.messages))
    
    # Main chat interface
    st.markdown("---")
    
    # Display existing messages
    if st.session_state.messages:
        display_chat_messages()
    else:
        st.info("👋 Start a conversation by typing a message below!")
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        if not st.session_state.chatbot:
            st.error("Please configure your API connection in the sidebar first.")
            return
        
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_message = {
            "role": "user", 
            "content": prompt, 
            "timestamp": timestamp
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"*{timestamp}*")
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chatbot.get_response(prompt)
                    st.markdown(response)
                    
                    # Add assistant message to chat history
                    assistant_timestamp = datetime.now().strftime("%H:%M:%S")
                    assistant_message = {
                        "role": "assistant", 
                        "content": response,
                        "timestamp": assistant_timestamp
                    }
                    st.session_state.messages.append(assistant_message)
                    st.caption(f"*{assistant_timestamp}*")
                    
                except Exception as e:
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_message)
                    
                    # Add error message to chat history
                    error_timestamp = datetime.now().strftime("%H:%M:%S")
                    error_msg = {
                        "role": "assistant", 
                        "content": error_message,
                        "timestamp": error_timestamp
                    }
                    st.session_state.messages.append(error_msg)

if __name__ == "__main__":
    main()
