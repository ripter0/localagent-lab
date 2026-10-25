# CleanSignal Startup Guide

## Quick Start

### Step 1: Install Python

Download Python 3.8+ from https://www.python.org/downloads/

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
python database_init.py
```

### Step 4: Run Application

```bash
python app.py
```

### Step 5: Open Browser

Visit http://localhost:8000

## Troubleshooting

- If Python not found, install it from python.org
- Check that requirements.txt is installed with pip
- Ensure .env file exists with proper configuration

## Alternative: Using uvicorn directly

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```