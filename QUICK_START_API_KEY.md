# Quick Start: Add Your OpenAI API Key

## ✅ OpenAI Confirmed as AI Provider

This project uses **OpenAI GPT-4** for email grouping and project detection.

## 📝 Where to Add Your API Key

### Option 1: Root Directory `.env` File (Recommended)

1. **Create `.env` file in the root directory:**
   ```bash
   cd /Users/james/Documents/Project_Repo/Tradie_GSuite
   cp config/development.env.example .env
   ```

2. **Open `.env` in your editor**

3. **Find this line:**
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Replace with your actual API key:**
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. **Save the file**

### Option 2: Edit config/development.env.example

1. **Copy the example file:**
   ```bash
   cp config/development.env.example config/development.env
   ```

2. **Edit `config/development.env`** and add your key

## 🎯 Your API Key Location

Your OpenAI API key should be in one of these files:

```
Tradie_GSuite/
├── .env                          ← ADD IT HERE (recommended)
│   └── OPENAI_API_KEY=sk-proj-...
│
└── config/
    └── development.env           ← OR HERE
        └── OPENAI_API_KEY=sk-proj-...
```

## ✅ Verify It's Working

After adding your API key, test it:

```bash
# Activate virtual environment
source venv/bin/activate

# Check configuration
python -c "from app.config import settings; print('OpenAI configured:', bool(settings.openai_api_key))"
```

## 📚 Full Documentation

See [SETUP_API_KEYS.md](SETUP_API_KEYS.md) for complete setup instructions.

---

**Your API key is secure:** The `.env` file is already in `.gitignore` and will never be committed to Git.

