# Quick Start Guide

Get the Framework Assistant running in 3 simple steps:

## Step 1: Add Your OpenAI API Key

Edit the `.env` file:
```bash
nano framework-assistant/.env
```

Replace `your-api-key-here` with your actual OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

Save and exit (Ctrl+X, then Y, then Enter).

## Step 2: Install Dependencies (if needed)

If you haven't already installed the dependencies, run:
```bash
./setup.sh
```

Or manually:
```bash
pip install -r framework-assistant/requirements.txt
```

## Step 3: Run the Application

### Easiest way:
```bash
./run.sh
```

### Or directly with Streamlit:
```bash
cd framework-assistant
streamlit run app.py
```

The application will open automatically in your browser at http://localhost:8501

## Troubleshooting

**"Permission denied" when running scripts:**
```bash
chmod +x setup.sh run.sh
```

**"OpenAI API key not found":**
- Make sure you edited `framework-assistant/.env`
- Check that there are no extra spaces in the API key

**"Streamlit command not found":**
```bash
pip install streamlit
```

**Database errors:**
- Ensure `framework-assistant/frameworks.db` exists
- Check that the file is not corrupted

## That's it!

For more detailed deployment options, see [DEPLOYMENT.md](DEPLOYMENT.md)
