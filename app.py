import streamlit as st
import os
import json
from datetime import datetime
from chatbot import ChatBot
from database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    [data-testid="stSidebar"] h2 {
        color: #495057;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #6c757d;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 1rem;
    }
    
    /* Chat message styling */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-left: 4px solid #667eea;
    }
    
    [data-testid="stChatMessage"][data-testid*="assistant"] {
        background: linear-gradient(135deg, #f093fb15 0%, #f5576c15 100%);
        border-left: 4px solid #f093fb;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Input styling */
    [data-testid="stChatInput"] {
        border-radius: 12px;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #e3f2fd;
        border-radius: 8px;
    }
    
    .stSuccess {
        background-color: #e8f5e9;
        border-radius: 8px;
    }
    
    .stWarning {
        background-color: #fff3e0;
        border-radius: 8px;
    }
    
    .stError {
        background-color: #ffebee;
        border-radius: 8px;
    }
    
    /* Expander styling */
    [data-testid="stExpander"] {
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    
    /* Metric styling */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #dee2e6, transparent);
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "api_provider" not in st.session_state:
        st.session_state.api_provider = "openai"
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a helpful AI assistant."
    if "uploaded_file_context" not in st.session_state:
        st.session_state.uploaded_file_context = None
    if "db" not in st.session_state:
        try:
            st.session_state.db = DatabaseManager()
        except Exception as e:
            st.session_state.db = None
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None

def load_conversation(conversation_id: int):
    """Load a conversation from the database"""
    if st.session_state.db:
        messages = st.session_state.db.get_conversation_messages(conversation_id)
        st.session_state.messages = []
        for msg in messages:
            st.session_state.messages.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%H:%M:%S")
            })
        st.session_state.current_conversation_id = conversation_id
        
        # Sync chatbot history with loaded conversation
        if st.session_state.chatbot:
            st.session_state.chatbot.conversation_history = []
            for msg in messages:
                st.session_state.chatbot.conversation_history.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                })

def save_message_to_db(role: str, content: str):
    """Save a message to the database"""
    if st.session_state.db and st.session_state.current_conversation_id:
        st.session_state.db.add_message(
            st.session_state.current_conversation_id,
            role,
            content
        )

def export_conversation():
    """Export current conversation as JSON"""
    if st.session_state.messages:
        export_data = {
            "conversation": st.session_state.messages,
            "exported_at": datetime.now().isoformat(),
            "message_count": len(st.session_state.messages)
        }
        return json.dumps(export_data, indent=2)
    return None

def display_chat_messages():
    """Display all chat messages in the conversation"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"*{message['timestamp']}*")

def main():
    initialize_session_state()
    
    # Header with better styling
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🤖 AI Chatbot")
        st.markdown("**Powered by OpenAI & Anthropic** • Multi-model support with conversation history")
    with col2:
        if st.session_state.messages:
            st.metric("💬 Messages", len(st.session_state.messages))
    
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
        
        # Model selection based on provider
        if api_provider == "openai":
            model_options = list(ChatBot.OPENAI_MODELS.keys())
            default_model = "GPT-5"
        else:
            model_options = list(ChatBot.ANTHROPIC_MODELS.keys())
            default_model = "Claude Sonnet 4"
        
        selected_model_name = st.selectbox(
            "Choose Model:",
            model_options,
            index=model_options.index(default_model) if default_model in model_options else 0,
            key="model_select"
        )
        
        # Get actual model ID
        if api_provider == "openai":
            selected_model = ChatBot.OPENAI_MODELS[selected_model_name]
        else:
            selected_model = ChatBot.ANTHROPIC_MODELS[selected_model_name]
        
        # System prompt customization
        with st.expander("🎯 System Prompt (Advanced)", expanded=False):
            system_prompt = st.text_area(
                "Customize AI behavior:",
                value=st.session_state.system_prompt,
                height=100,
                help="Define how the AI should behave and respond"
            )
            if st.button("Apply Prompt"):
                st.session_state.system_prompt = system_prompt
                st.session_state.chatbot = None
                st.success("System prompt updated!")
                st.rerun()
        
        # Update session state if provider or model changed
        if (api_provider != st.session_state.api_provider or 
            selected_model != st.session_state.selected_model):
            st.session_state.api_provider = api_provider
            st.session_state.selected_model = selected_model
            st.session_state.chatbot = None
        
        # Initialize chatbot if not exists or changed
        if st.session_state.chatbot is None:
            try:
                st.session_state.chatbot = ChatBot(
                    provider=api_provider, 
                    model=selected_model,
                    system_prompt=st.session_state.system_prompt
                )
                
                # Restore conversation history to chatbot if there's an active conversation
                if st.session_state.current_conversation_id and st.session_state.db:
                    messages = st.session_state.db.get_conversation_messages(
                        st.session_state.current_conversation_id
                    )
                    st.session_state.chatbot.conversation_history = []
                    for msg in messages:
                        st.session_state.chatbot.conversation_history.append({
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat()
                        })
                
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
        
        st.markdown("---")
        st.subheader("📎 File Context")
        
        # File upload for context
        uploaded_file = st.file_uploader(
            "Upload a file for context:",
            type=["txt", "md", "py", "js", "json", "csv", "pdf"],
            help="Upload a file to provide context to the AI"
        )
        
        if uploaded_file is not None:
            try:
                # Read file content
                if uploaded_file.type == "application/pdf":
                    st.warning("PDF files require additional processing. For now, please use text-based files.")
                else:
                    file_content = uploaded_file.read().decode("utf-8")
                    st.session_state.uploaded_file_context = f"[File: {uploaded_file.name}]\n{file_content}"
                    st.success(f"✅ Loaded: {uploaded_file.name}")
                    
                    # Show preview
                    with st.expander("📄 File Preview"):
                        st.text(file_content[:500] + ("..." if len(file_content) > 500 else ""))
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        if st.session_state.uploaded_file_context:
            if st.button("🗑️ Clear File Context"):
                st.session_state.uploaded_file_context = None
                st.rerun()
        
        st.markdown("---")
        st.subheader("💾 Conversations")
        
        # New conversation button
        if st.button("➕ New Conversation", type="primary"):
            if st.session_state.db:
                new_conv = st.session_state.db.create_conversation(
                    title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                st.session_state.current_conversation_id = new_conv.id
                st.session_state.messages = []
                if st.session_state.chatbot:
                    st.session_state.chatbot.clear_history()
                st.rerun()
        
        # Load existing conversations
        if st.session_state.db:
            conversations = st.session_state.db.get_all_conversations()
            if conversations:
                for conv in conversations[:5]:
                    is_active = st.session_state.current_conversation_id == conv.id
                    button_type = "primary" if is_active else "secondary"
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if st.button(
                            f"{'🔵' if is_active else '📝'} {conv.title[:25]}..." if len(conv.title) > 25 else f"{'🔵' if is_active else '📝'} {conv.title}",
                            key=f"load_{conv.id}",
                            use_container_width=True,
                            type=button_type
                        ):
                            load_conversation(conv.id)
                            st.rerun()
                    with col2:
                        if st.button("🗑️", key=f"del_{conv.id}", type="secondary"):
                            st.session_state.db.delete_conversation(conv.id)
                            if st.session_state.current_conversation_id == conv.id:
                                st.session_state.current_conversation_id = None
                                st.session_state.messages = []
                            st.rerun()
            else:
                st.info("No saved conversations yet")
        
        st.markdown("---")
        st.subheader("📤 Export & Actions")
        
        # Export conversation
        if st.session_state.messages:
            col1, col2 = st.columns(2)
            with col1:
                export_data = export_conversation()
                if export_data:
                    st.download_button(
                        label="📥 JSON",
                        data=export_data,
                        file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            with col2:
                # Export as text
                text_export = "\n\n".join([
                    f"{msg['role'].upper()}: {msg['content']}" 
                    for msg in st.session_state.messages
                ])
                st.download_button(
                    label="📄 TXT",
                    data=text_export,
                    file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # Clear conversation button
        if st.button("🗑️ Clear Current Chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.chatbot:
                st.session_state.chatbot.clear_history()
            st.rerun()
    
    # Main chat interface
    st.markdown("---")
    
    # Display current conversation info in a nice container
    if st.session_state.current_conversation_id and st.session_state.db:
        conv = st.session_state.db.get_conversation(st.session_state.current_conversation_id)
        if conv:
            st.markdown(f"**Current Conversation:** {conv.title}")
            st.caption(f"Started: {conv.created_at.strftime('%B %d, %Y at %I:%M %p')}")
    
    # Display existing messages
    if st.session_state.messages:
        display_chat_messages()
    else:
        # Enhanced empty state
        st.markdown("""
        <div style='text-align: center; padding: 3rem 0;'>
            <h2 style='color: #667eea; margin-bottom: 1rem;'>👋 Welcome to AI Chatbot!</h2>
            <p style='font-size: 1.1rem; color: #6c757d; margin-bottom: 1.5rem;'>
                Start a conversation by typing your message below
            </p>
            <p style='color: #adb5bd;'>
                💡 <strong>Tip:</strong> Upload a file in the sidebar to chat with context
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        if not st.session_state.chatbot:
            st.error("Please configure your API connection in the sidebar first.")
            return
        
        # Create new conversation if none exists
        if st.session_state.current_conversation_id is None and st.session_state.db:
            new_conv = st.session_state.db.create_conversation(
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            st.session_state.current_conversation_id = new_conv.id
        
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_message = {
            "role": "user", 
            "content": prompt, 
            "timestamp": timestamp
        }
        st.session_state.messages.append(user_message)
        save_message_to_db("user", prompt)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"*{timestamp}*")
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Add file context if available
                    message_with_context = prompt
                    if st.session_state.uploaded_file_context:
                        message_with_context = f"{st.session_state.uploaded_file_context}\n\nUser question: {prompt}"
                    
                    response = st.session_state.chatbot.get_response(message_with_context)
                    st.markdown(response)
                    
                    # Add assistant message to chat history
                    assistant_timestamp = datetime.now().strftime("%H:%M:%S")
                    assistant_message = {
                        "role": "assistant", 
                        "content": response,
                        "timestamp": assistant_timestamp
                    }
                    st.session_state.messages.append(assistant_message)
                    save_message_to_db("assistant", response)
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
