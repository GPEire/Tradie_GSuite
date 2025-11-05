# Development Guide
## Virtual Environment Best Practices

This project uses **virtual environments** to isolate dependencies and ensure consistent development environments across the team.

---

## Virtual Environment Quick Reference

### Python Virtual Environment

#### Create Virtual Environment
```bash
python3 -m venv venv
```

#### Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

#### Verify Activation
When activated, you should see `(venv)` at the beginning of your terminal prompt:
```bash
(venv) user@machine:~/Tradie_GSuite$
```

#### Deactivate Virtual Environment
```bash
deactivate
```

#### Install Dependencies
```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate    # Windows

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Install a new package
pip install package-name

# Add package to requirements.txt
pip freeze > requirements.txt
```

---

## Automated Setup

### Quick Setup (macOS/Linux)
```bash
./setup.sh
```

### Quick Setup (Windows)
```powershell
.\setup.ps1
```

The setup script will:
- ✅ Check prerequisites
- ✅ Create Python virtual environment
- ✅ Install Python dependencies
- ✅ Set up Node.js environment
- ✅ Create `.env` template file
- ✅ Configure `.gitignore`

---

## Development Workflow

### Before Starting Work

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Verify you're in the virtual environment:**
   ```bash
   which python  # Should point to venv/bin/python
   pip list      # Should show installed packages
   ```

3. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

### During Development

1. **Always work with activated virtual environment**
   - If you see errors about missing packages, check if venv is activated
   - Never install packages globally (`pip install --user` is acceptable if needed)

2. **Install new dependencies:**
   ```bash
   # Activate venv first
   source venv/bin/activate
   
   # Install package
   pip install new-package
   
   # Update requirements.txt
   pip freeze > requirements.txt
   
   # Commit the updated requirements.txt
   git add requirements.txt
   git commit -m "Add new-package dependency"
   ```

3. **Run backend server:**
   ```bash
   source venv/bin/activate
   python -m uvicorn app.main:app --reload --port 8000
   ```

4. **Run tests:**
   ```bash
   source venv/bin/activate
   pytest
   pytest --cov=app tests/  # With coverage
   ```

### Before Committing

1. **Ensure virtual environment is activated**
2. **Run tests:**
   ```bash
   pytest
   ```
3. **Check code style:**
   ```bash
   black --check .
   flake8 .
   ```
4. **Update requirements.txt if needed:**
   ```bash
   pip freeze > requirements.txt
   ```

---

## Troubleshooting Virtual Environments

### Problem: Virtual environment not activating

**Solution:**
```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Problem: Packages installed but not found

**Check:**
1. Is virtual environment activated? (Look for `(venv)` in prompt)
2. Which Python is being used?
   ```bash
   which python
   # Should show: .../venv/bin/python
   ```
3. Reinstall packages:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

### Problem: "Command not found" errors

**Solution:**
- Ensure you're using the correct Python/pip from the virtual environment
- Try: `python -m pip install package-name` instead of `pip install package-name`

### Problem: Virtual environment is too large

**Solution:**
- This is normal. Virtual environments contain all dependencies
- Ensure `venv/` is in `.gitignore` (it should be)
- Never commit the `venv/` folder to Git

---

## Virtual Environment Best Practices

✅ **DO:**
- Always activate virtual environment before working
- Commit `requirements.txt` to version control
- Use `pip freeze > requirements.txt` to update dependencies
- Keep virtual environment local (don't commit it)
- Use descriptive commit messages when updating dependencies

❌ **DON'T:**
- Commit `venv/` folder to Git
- Install packages globally when working on this project
- Share virtual environment folders between machines
- Forget to activate virtual environment before running commands

---

## IDE Integration

### VS Code

VS Code can detect and use your virtual environment automatically:

1. Open the project in VS Code
2. VS Code should detect the virtual environment
3. Select the Python interpreter: `Cmd+Shift+P` → "Python: Select Interpreter"
4. Choose: `./venv/bin/python`

### PyCharm

1. Open project in PyCharm
2. Go to Settings → Project → Python Interpreter
3. Click the gear icon → "Add..."
4. Select "Existing environment"
5. Point to: `./venv/bin/python`

---

## Environment Variables

Never commit `.env` files. They contain sensitive credentials.

### Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### Load environment variables:
The project uses `python-dotenv` to automatically load `.env` files:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Additional Resources

- [Python Virtual Environments Official Docs](https://docs.python.org/3/tutorial/venv.html)
- [Pip User Guide](https://pip.pypa.io/en/stable/user_guide/)
- [Best Practices for Python Dependencies](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

---

## Quick Commands Cheat Sheet

```bash
# Setup
./setup.sh                    # Run setup script
source venv/bin/activate      # Activate venv

# Development
pip install -r requirements.txt    # Install dependencies
python -m uvicorn app.main:app --reload  # Run server
pytest                          # Run tests

# Maintenance
pip freeze > requirements.txt  # Update requirements
deactivate                     # Deactivate venv
```


