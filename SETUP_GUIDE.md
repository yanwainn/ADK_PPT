# 🚀 Step-by-Step Setup Guide

This guide will walk you through setting up and running the Agentic PPT application from scratch.

## 📋 Prerequisites

- **Operating System**: macOS, Linux, or Windows
- **Python**: Version 3.8 or higher (3.11 recommended)
- **Internet Connection**: Required for downloading dependencies and API calls
- **API Access**: OpenAI API key or Azure OpenAI credentials

## 🔧 Step 1: Verify Python Installation

Make sure you have Python 3.8 or higher installed:

```bash
python --version
# Should show Python 3.8+ (Python 3.11 recommended)
```

If you don't have Python installed:
- **macOS**: Install via Homebrew: `brew install python@3.11`
- **Windows**: Download from [python.org](https://python.org)
- **Linux**: Use your package manager: `sudo apt install python3.11`

## 📁 Step 2: Get the Project

### Option A: Clone from Git (if available)
```bash
git clone <repository-url>
cd Agentic_PPT
```

### Option B: Download and Extract
1. Download the project files
2. Extract to a folder named `Agentic_PPT`
3. Open terminal/command prompt in that folder

## ⚡ Step 3: Quick Setup (Recommended)

Run the automated setup command:

```bash
make setup
```

This command will:
- Install UV (if not already installed)
- Create a virtual environment
- Install all dependencies
- Copy the environment template

**If you don't have `make` installed**, proceed to Step 4 for manual setup.

## 🔧 Step 4: Manual Setup (Alternative)

If the quick setup doesn't work, follow these manual steps:

### 4.1 Create Virtual Environment and Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
.venv/bin/pip install -r requirements.txt
```

### 4.2 Copy Environment Template
```bash
cp env_template.txt .env
```

## 🔑 Step 5: Configure API Keys

Edit the `.env` file with your preferred text editor:

```bash
# On macOS/Linux
nano .env

# On Windows
notepad .env

# Or use any text editor
```

### For OpenAI API (Recommended for individuals):
```env
API_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
OPENAI_MODEL=gpt-4o
DALLE_MODEL=dall-e-3
```

### For Azure OpenAI (Recommended for enterprises):
```env
API_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-01
DALLE_API_KEY=your-dalle-key
DALLE_ENDPOINT=https://your-resource.openai.azure.com/
DALLE_DEPLOYMENT=dall-e-3
DALLE_API_VERSION=2024-02-01
```

## 🚀 Step 6: Run the Application

### Method 1: Using Make (Recommended)
```bash
make run-streamlit
```

### Method 2: Using Virtual Environment
```bash
.venv/bin/streamlit run app.py
```

### Method 3: Using Python directly
```bash
.venv/bin/python run.py
```

## 🌐 Step 7: Access the Application

1. **Open your web browser**
2. **Navigate to**: `http://localhost:8501`
3. **The application should load automatically**

If the browser doesn't open automatically, manually navigate to the URL above.

## 🎯 Step 8: Test the Application

1. **Configure API settings** in the sidebar (if not using .env file)
2. **Upload a PDF file** using the file uploader
3. **Click "Generate Presentation"**
4. **Wait for processing** (this may take a few minutes)
5. **Download your generated presentation**

## 🎨 Step 9: Optional Customization

### Add Company Logo
Place your logo file in one of these locations:
```
logo.png              # Project root
static/logo.png        # Static folder
assets/logo.png        # Assets folder
```

### Add PowerPoint Template
Place your template file:
```
template.pptx          # Project root
templates/template.pptx # Templates folder
```

### Test Logo Loading
```bash
uv run python utils/logo_test.py
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. UV Not Found
```bash
# Restart your terminal and try again
# Or manually add UV to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

#### 2. Permission Errors (macOS/Linux)
```bash
# Make sure you have write permissions
chmod +x run.py
```

#### 3. Python Version Issues
```bash
# Check Python version
python --version

# If using older Python, install Python 3.11
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
```

#### 4. API Key Errors
- Double-check your API key is correct
- Ensure no extra spaces in the .env file
- Verify your API provider setting matches your credentials

#### 5. Port Already in Use
```bash
# Use a different port
uv run streamlit run app.py --server.port 8502
```

#### 6. Dependencies Issues
```bash
# Clean and reinstall
make clean
make install

# Or manually
uv sync --reinstall
```

### Getting Help

1. **Check project status**:
   ```bash
   make status
   ```

2. **View available commands**:
   ```bash
   make help
   ```

3. **Clean temporary files**:
   ```bash
   make clean
   ```

## 📊 Verification Checklist

Before using the application, verify:

- [ ] UV is installed and working (`uv --version`)
- [ ] Project dependencies are installed (`make status`)
- [ ] .env file exists and contains your API keys
- [ ] Application starts without errors (`make run`)
- [ ] Web interface loads at http://localhost:8501
- [ ] API provider is correctly configured in sidebar
- [ ] You can upload a PDF file

## 🎉 Success!

If you've completed all steps successfully:

1. **Your application is running** at http://localhost:8501
2. **You can upload PDFs** and generate presentations
3. **API calls are working** (test with a small PDF first)
4. **You can download** generated HTML and PowerPoint files

## 📚 Next Steps

- Read the [OpenAI Models Guide](OPENAI_MODELS.md) to optimize model selection
- Check the main [README.md](README.md) for detailed feature information
- Explore the application's different output formats
- Customize with your company branding

## 🆘 Still Having Issues?

1. **Check the main README.md** troubleshooting section
2. **Verify your API credentials** are valid and have sufficient quota
3. **Try with a simple PDF** first to test the system
4. **Check the terminal output** for specific error messages
5. **Ensure your internet connection** is stable for API calls

---

*Happy presenting! 🎉* 