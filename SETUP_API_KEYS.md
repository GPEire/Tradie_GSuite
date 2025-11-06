# API Key Configuration Guide

## OpenAI API Key Setup (Required)

This project uses **OpenAI GPT-4** as the AI/LLM provider for email grouping and project detection.

### Step 1: Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click **"Create new secret key"**
5. Name it (e.g., "Tradie GSuite Email Extension")
6. **Copy the key immediately** - you won't be able to see it again!

### Step 2: Add Your API Key to the Project

#### Option A: Root Directory `.env` File (Recommended for Development)

1. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in your editor

3. Find the line:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Replace `your_openai_api_key_here` with your actual API key:
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. Save the file

#### Option B: Development Environment File

1. Copy the development example file:
   ```bash
   cp config/development.env.example config/development.env
   ```

2. Edit `config/development.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Step 3: Verify Configuration

The configuration is automatically loaded from:
1. `.env` file in the root directory (if exists)
2. Environment variables (if set)
3. `config/development.env` (if exists)

### Step 4: Test Your API Key

You can verify your API key works by running:

```bash
# Activate your virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Test OpenAI connection (will be available after TASK-008)
python -c "from app.config import settings; print('API Key configured:', bool(settings.openai_api_key))"
```

## Current Configuration

- **AI Provider:** OpenAI (confirmed)
- **Model:** GPT-4 (default, can be changed to `gpt-4-turbo` or `gpt-3.5-turbo`)
- **Configuration File:** `backend/app/config.py`

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AI_PROVIDER` | AI service provider | No | `openai` |
| `OPENAI_API_KEY` | Your OpenAI API key | **Yes** | - |
| `OPENAI_MODEL` | OpenAI model to use | No | `gpt-4` |

## Security Notes

⚠️ **Important:**
- Never commit your `.env` file to Git (it's already in `.gitignore`)
- Never share your API key publicly
- Keep your API key secure
- Rotate keys if compromised
- Monitor usage in [OpenAI Dashboard](https://platform.openai.com/usage)

## Cost Considerations

- GPT-4 pricing: ~$0.03 per 1K tokens (input), ~$0.06 per 1K tokens (output)
- GPT-4 Turbo: ~$0.01/$0.03 per 1K tokens (cheaper, faster)
- GPT-3.5 Turbo: ~$0.0005/$0.0015 per 1K tokens (much cheaper, less accurate)

For email grouping, GPT-4 or GPT-4 Turbo is recommended for better accuracy.

## Next Steps

Once your API key is configured:
1. ✅ API key is set up
2. Continue with TASK-008: Research and select AI/LLM service provider (already confirmed: OpenAI)
3. Continue with TASK-009: Implement prompt engineering for project detection

---

**Need Help?**
- OpenAI API Documentation: https://platform.openai.com/docs
- OpenAI Pricing: https://openai.com/pricing
- API Key Management: https://platform.openai.com/api-keys

