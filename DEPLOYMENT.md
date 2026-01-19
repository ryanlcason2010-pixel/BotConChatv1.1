# BotConChat v1.1 - Local Deployment Guide

This guide explains how to deploy and run the Framework Assistant application on your local machine using Streamlit.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git (optional, for cloning the repository)

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Create necessary directories
   - Generate a `.env` file

2. **Configure your API key:**
   ```bash
   nano framework-assistant/.env
   ```
   Add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Run the application:**
   ```bash
   ./run.sh
   ```

The application will start and automatically open in your default browser at `http://localhost:8501`

### Option 2: Manual Setup

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r framework-assistant/requirements.txt
   ```

3. **Create environment file:**
   ```bash
   cd framework-assistant
   cp .env.example .env
   ```

4. **Configure your API key:**
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Running the Application

### Using the run script (easiest):
```bash
./run.sh
```

### Using Streamlit directly:
```bash
cd framework-assistant
streamlit run app.py
```

### Using the full command path from anywhere:
```bash
cd /path/to/BotConChatv1.1
streamlit run framework-assistant/app.py
```

## Environment Configuration

The application uses environment variables for configuration. All variables have sensible defaults, but you can customize them in `framework-assistant/.env`:

### Required:
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Optional (with defaults):
- `DATABASE_PATH`: Path to SQLite database (default: `frameworks.db`)
- `FEEDBACK_LOG_FILE`: Path to feedback log (default: `logs/feedback.json`)
- `OPENAI_LLM_MODEL`: OpenAI model to use (default: `gpt-4o-mini`)
- `OPENAI_EMBEDDING_MODEL`: Embedding model (default: `text-embedding-3-small`)
- `EMBEDDING_DIMENSIONS`: Embedding dimensions (default: `1536`)
- `EMBEDDINGS_CACHE_FILE`: Cache file path (default: `cache/embeddings_cache.pkl`)
- `SEARCH_TOP_K`: Number of search results (default: `5`)
- `SEARCH_MIN_SIMILARITY`: Similarity threshold (default: `0.6`)

See `framework-assistant/.env.example` for a complete list with descriptions.

## First Run

On first run, the application will:
1. Load the framework database (`frameworks.db`)
2. Generate embeddings for semantic search (this may take a few minutes)
3. Cache the embeddings for faster subsequent startups
4. Open the web interface in your browser

The embedding generation only happens once. Subsequent runs will be much faster as they use the cached embeddings.

## Accessing the Application

Once running, access the application at:
- **Local URL**: http://localhost:8501
- **Network URL**: http://your-ip:8501 (shown in terminal)

## Stopping the Application

Press `Ctrl+C` in the terminal where Streamlit is running.

## Troubleshooting

### "Module not found" errors
Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r framework-assistant/requirements.txt
```

### "OpenAI API key not found" error
1. Check that `framework-assistant/.env` exists
2. Verify your `OPENAI_API_KEY` is set correctly
3. Make sure there are no extra spaces or quotes around the key

### "Database file not found" error
Ensure `framework-assistant/frameworks.db` exists. If you're starting fresh, you'll need to create or import your framework database.

### Port already in use
If port 8501 is already in use, Streamlit will try the next available port (8502, 8503, etc.). Check the terminal output for the actual URL.

Or specify a different port:
```bash
streamlit run app.py --server.port 8502
```

### Slow first startup
The first run generates embeddings for all frameworks, which can take several minutes depending on the number of frameworks. This is normal. Subsequent runs will be much faster.

## Development Mode

For development with auto-reload on file changes:
```bash
cd framework-assistant
streamlit run app.py --server.runOnSave true
```

## Production Deployment

For production deployment, consider:
1. Using a production WSGI server
2. Setting up SSL/HTTPS
3. Configuring proper authentication
4. Setting up a reverse proxy (nginx/Apache)
5. Using a proper secrets management system

## Directory Structure

```
BotConChatv1.1/
├── setup.sh                    # Automated setup script
├── run.sh                      # Run script
├── DEPLOYMENT.md              # This file
└── framework-assistant/
    ├── .env                   # Environment configuration (create from .env.example)
    ├── .env.example           # Example environment file
    ├── requirements.txt       # Python dependencies
    ├── app.py                 # Main Streamlit application
    ├── frameworks.db          # SQLite database
    ├── components/            # UI components
    ├── handlers/              # Business logic handlers
    ├── utils/                 # Utility modules
    ├── logs/                  # Application logs
    └── cache/                 # Embedding cache
```

## Need Help?

- Check the main README.md for application usage
- Review the logs in `framework-assistant/logs/`
- Ensure all prerequisites are installed
- Verify your `.env` configuration

## Command Reference

```bash
# Setup (run once)
./setup.sh

# Run the application
./run.sh

# Or manually:
cd framework-assistant && streamlit run app.py

# Deactivate virtual environment when done
deactivate
```
