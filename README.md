# ChatPyBot

This is a Streamlit-based AI chatbot that supports OpenAI, Anthropic, and Google Gemini (GenAI) providers.

## Environment variables

The application expects API keys to be provided via environment variables:

- OPENAI_API_KEY — OpenAI API key
- ANTHROPIC_API_KEY — Anthropic API key
- GEMINI_API_KEY — Google Gemini API key

You can set them in several ways:

### 1) Temporary (current PowerShell session)

```powershell
$env:OPENAI_API_KEY = "sk-..."
streamlit run app.py
```

### 2) Permanent (user environment variable on Windows)

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
# Start a new terminal/session for the change to take effect
```

### 3) Local .env file (development only)

- Copy `.env.example` to `.env` and fill in your keys. Do NOT commit `.env` to version control.
- This project will attempt to load `.env` automatically if `python-dotenv` is installed.

### 4) Deployment

- When deploying to a cloud provider, add the keys in the platform's Secrets / Environment Variables section.

## Notes

- Keep API keys secret.
- If you get errors about missing API keys, check that `OPENAI_API_KEY` or the provider-specific variable is set and that the provider is selected in the sidebar.

