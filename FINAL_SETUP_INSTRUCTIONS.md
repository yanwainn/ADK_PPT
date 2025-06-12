# 🚀 Agentic PPT - Final Setup Instructions

## ✅ Working Setup (Tested and Verified)

This guide provides the exact steps to get the Agentic PPT application running successfully.

## 📋 Prerequisites

- **Python 3.8+** (Python 3.11 recommended)
- **Internet connection** for downloading dependencies
- **OpenAI API key** or **Azure OpenAI credentials**

## 🔧 Step-by-Step Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip
.venv/bin/pip install --upgrade pip

# Install all dependencies
.venv/bin/pip install -r requirements.txt
```

**Or use the Make command:**
```bash
make install
```

### 2. Configure Environment Variables

```bash
# Copy the environment template
cp env_template.txt .env

# Edit the .env file with your API credentials
nano .env  # or use your preferred editor
```

**Or use the Make command:**
```bash
make env
```

### 3. Configure Your API Keys

Edit the `.env` file with your API credentials:

#### For OpenAI API:
```env
API_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
OPENAI_MODEL=gpt-4o
DALLE_MODEL=dall-e-3
```

#### For Azure OpenAI:
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

### 4. Start the Application

```bash
# Using the virtual environment directly
.venv/bin/streamlit run app.py
```

**Or use the Make command:**
```bash
make run-streamlit
```

### 5. Access the Application

1. Open your web browser
2. Navigate to: `http://localhost:8501`
3. The application should load successfully

## 🎯 Usage Instructions

1. **Configure API Settings** (if not using .env file):
   - Use the sidebar to select your API provider
   - Enter your API credentials

2. **Upload a PDF**:
   - Click "Browse files" or drag & drop a PDF
   - Supported formats: PDF files up to 200MB

3. **Generate Presentation**:
   - Click "Generate Presentation"
   - Wait for processing (may take 2-5 minutes)
   - View progress in the status indicators

4. **Download Results**:
   - Preview slides in the "Generated Slides" tab
   - Download HTML version from "HTML Slides" tab
   - Download PowerPoint from "PowerPoint Slides" tab

## 📦 Key Dependencies Installed

- `streamlit==1.28.0` - Web application framework
- `openai-agents==0.0.17` - OpenAI Agents SDK
- `openai==1.86.0` - OpenAI API client (updated version)
- `pydantic==2.11.5` - Data validation (updated version)
- `python-dotenv==1.0.0` - Environment variables
- `PyPDF2==3.0.1` - PDF processing
- `Pillow==10.1.0` - Image processing
- `python-pptx==0.6.23` - PowerPoint generation
- `aiofiles==23.2.1` - Async file operations
- `httpx==0.28.1` - HTTP client (updated version)

## 🛠️ Available Make Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make env           # Copy environment template
make run-streamlit # Start the application
make clean         # Clean temporary files
make status        # Show project status
```

## 🔍 Troubleshooting

### Common Issues:

1. **Import Errors**: 
   - Make sure virtual environment is activated
   - Reinstall dependencies: `make install`

2. **API Key Errors**:
   - Check .env file format
   - Verify API keys are correct
   - Ensure no extra spaces in .env

3. **Port Already in Use**:
   ```bash
   .venv/bin/streamlit run app.py --server.port 8502
   ```

4. **Permission Errors**:
   ```bash
   chmod +x .venv/bin/streamlit
   ```

### Verification Commands:

```bash
# Check if all imports work
.venv/bin/python -c "from modules.agents import extract_key_sections, create_content_extraction_agent; print('Agents: Success!')"
.venv/bin/python -c "from modules.processor import process_pdf_to_presentation; print('Processor: Success!')"
.venv/bin/python -c "import app; print('App: Success!')"

# Check if Streamlit is accessible
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501
# Should return: 200
```

## 🎨 Optional Customization

### Add Company Logo:
Place `logo.png` in:
- Project root directory
- `static/` folder  
- `assets/` folder

### Add PowerPoint Template:
Place `template.pptx` in:
- Project root directory
- `templates/` folder

### Test Logo Loading:
```bash
.venv/bin/python utils/logo_test.py
```

## ✅ Success Indicators

You know the setup is working when:

1. ✅ Dependencies install without errors
2. ✅ Application starts on `http://localhost:8501`
3. ✅ No import errors in the console
4. ✅ Sidebar shows API configuration options
5. ✅ File upload area is visible
6. ✅ HTTP status 200 when accessing the URL

## 🚀 Next Steps

1. **Test with a sample PDF** to ensure full functionality
2. **Configure your preferred API provider** in the sidebar
3. **Customize branding** by adding your logo and template
4. **Explore different slide layouts** and generation options

---

**🎉 Congratulations!** Your Agentic PPT application is now ready to transform PDFs into professional presentations using AI. 