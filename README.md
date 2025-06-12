# 🚀 Agentic PPT - AI-Powered PDF to Presentation Generator

An intelligent application that transforms PDF documents into professional HTML and PowerPoint presentations using OpenAI GPT and DALL-E.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)

## ✨ Features

- **🔍 PDF Content Extraction**: Automatically extracts key sections from PDF documents
- **🤖 AI-Powered Analysis**: Uses GPT to identify the most important content for presentation slides
- **🎨 Image Generation**: Creates relevant images for each slide using DALL-E 3
- **🔄 Flexible API Support**: Works with both Azure OpenAI and direct OpenAI APIs
- **📊 Multiple Output Formats**: 
  - Professional HTML slides with modern styling
  - PowerPoint presentations (.pptx)
  - Template-based PowerPoint generation
- **🎯 Customizable Branding**: Support for company logos and templates
- **💻 Interactive Web Interface**: Built with Streamlit for easy use

## 📁 Project Structure

```
.
├── app.py                              # Main Streamlit application
├── run.py                              # Application startup script
├── pyproject.toml                      # Project configuration and dependencies
├── Makefile                            # Project management commands
├── modules/                            # Core logic and processing
│   ├── agents.py                       # OpenAI agent definitions
│   ├── helpers.py                      # Helper functions for PDF processing
│   ├── models.py                       # Pydantic data models
│   ├── processor.py                    # Main processing pipeline
│   ├── slide_generator.py              # HTML slide generation
│   ├── pptx_converter.py              # Standard PowerPoint conversion
│   └── template_pptx_converter.py     # Template-based PowerPoint conversion
├── utils/                              # Utility scripts
│   ├── logo_test.py                   # Logo loading test utility
│   └── openai_client.py               # OpenAI client initialization
├── requirements.txt                    # Python dependencies (legacy)
├── env_template.txt                   # Environment variables template
├── OPENAI_MODELS.md                   # OpenAI models reference guide
└── Project_description.md             # Detailed project description
```

## 🚀 Quick Start

### Method 1: Using Make Commands (Recommended)

The fastest way to get started:

```bash
# 1. Install dependencies
make install

# 2. Set up environment variables
make env

# 3. Edit .env with your API keys
nano .env  # or your preferred editor

# 4. Start the application
make run-streamlit
```

### Method 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
.venv/bin/pip install -r requirements.txt

# 4. Set up environment variables
cp env_template.txt .env
# Edit .env with your API keys

# 5. Start the application
.venv/bin/streamlit run app.py
```

### Method 3: Using UV (Alternative)

If you prefer UV package manager:

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt

# 3. Set up environment variables
cp env_template.txt .env
# Edit .env with your API keys

# 4. Start the application
uv run streamlit run app.py
```

## 📋 Available Commands

Run `make help` to see all available commands:

```bash
make help          # Show available commands
make setup         # Complete project setup
make install       # Install dependencies
make run           # Start the application
make clean         # Clean up temporary files
make format        # Format code with black
make lint          # Run code linting
make env           # Copy environment template
make status        # Show project status
```

## 🔧 Installation Requirements

- **Python 3.8+** (Python 3.11 recommended)
- **UV package manager** (automatically installed with `make setup`)
- **OpenAI API key** or **Azure OpenAI credentials**

## 💻 Usage

1. **Start the application**:
   ```bash
   make run
   # or
   uv run python run.py
   # or
   uv run streamlit run app.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Configure API provider** in the sidebar:
   - Choose between Azure OpenAI or direct OpenAI
   - Enter your API credentials

4. **Upload a PDF document** through the web interface

5. **Generate presentation** by clicking the "Generate Presentation" button

6. **Preview and download** your slides in HTML or PowerPoint format

## 🎨 Optional Customization

### Add Company Logo
Place your `logo.png` file in one of these locations:
- Project root directory
- `static/` folder
- `assets/` folder

### Add PowerPoint Template
Place your `template.pptx` file in:
- Project root directory
- `templates/` folder

### Test Logo Loading
```bash
uv run python utils/logo_test.py
```

## 🔧 API Configuration

The application supports two API providers:

### Option 1: Azure OpenAI (Recommended for Enterprise)

Set `API_PROVIDER=azure` in your `.env` file and configure:

**GPT Configuration:**
- **API Key**: Your Azure OpenAI API key
- **Endpoint**: Your Azure OpenAI endpoint URL
- **Deployment**: Your GPT model deployment name
- **API Version**: API version (default: 2024-02-01)

**DALL-E Configuration:**
- **API Key**: Your DALL-E API key (can be same as GPT)
- **Endpoint**: Your DALL-E endpoint URL (can be same as GPT)
- **Deployment**: DALL-E model name (default: dall-e-3)
- **API Version**: API version (default: 2024-02-01)

### Option 2: Direct OpenAI API

Set `API_PROVIDER=openai` in your `.env` file and configure:

**Configuration:**
- **API Key**: Your OpenAI API key
- **GPT Model**: Model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
- **DALL-E Model**: Model to use (dall-e-3, dall-e-2)

## Environment Variables

Example `.env` configuration:

```bash
# For Azure OpenAI
API_PROVIDER=azure
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
DALLE_DEPLOYMENT=dall-e-3

# For Direct OpenAI
API_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4
DALLE_MODEL=dall-e-3
```

## 📦 Dependencies

Core dependencies are automatically managed by UV:

- **streamlit**: Web application framework
- **openai**: OpenAI API client (supports both Azure and direct APIs)
- **pydantic**: Data validation and modeling
- **python-dotenv**: Environment variable management
- **PyPDF2**: PDF text extraction
- **Pillow**: Image processing
- **numpy**: Numerical operations
- **requests**: HTTP requests
- **python-pptx**: PowerPoint file generation
- **aiofiles**: Async file operations
- **httpx**: Modern HTTP client

Development dependencies (optional):
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking

## Features in Detail

### Content Extraction
- Automatically identifies 3-7 key sections suitable for presentation slides
- Extracts essential content with importance ratings
- Identifies key themes and visual elements

### Image Generation
- Creates photorealistic images using DALL-E 3 or DALL-E 2
- Generates contextually relevant visuals for each slide
- Fallback to gradient placeholders if image generation fails
- Supports both Azure and direct OpenAI DALL-E endpoints

### Slide Generation
- Multiple layout types: balanced, text-focus, image-focus, comparison
- Professional styling with Bosch color scheme
- Responsive design with modern typography

### PowerPoint Export
- Standard PowerPoint generation with custom styling
- Template-based generation using organization templates
- Automatic logo placement and branding

## 🔧 Troubleshooting

### Common Issues

1. **Setup Issues**: 
   ```bash
   # Check project status
   make status
   
   # Clean and reinstall
   make clean
   make install
   ```

2. **API Key Errors**: 
   - Ensure your API credentials are correctly set in the .env file or sidebar settings
   - Verify you've selected the correct API provider (azure/openai)
   - Check that your API keys have the necessary permissions
   - See [OPENAI_MODELS.md](OPENAI_MODELS.md) for model recommendations

3. **Image Generation Failures**: 
   - The app will create placeholder images if DALL-E fails
   - Check your DALL-E API configuration and quotas
   - Verify your API provider supports DALL-E

4. **PDF Extraction Issues**: 
   - Ensure your PDF contains extractable text (not just images)
   - Try with a different PDF file

5. **PowerPoint Template Issues**: 
   - Ensure your template.pptx file has standard slide layouts
   - Template should include title and content placeholders

### Testing and Debugging

```bash
# Test logo loading
uv run python utils/logo_test.py

# Check project status
make status

# Format and lint code
make format
make lint

# Clean temporary files
make clean
```

### API Provider Switching
You can switch between Azure OpenAI and direct OpenAI:
1. Update the `API_PROVIDER` setting in the sidebar
2. Configure the appropriate API credentials
3. Restart the application if needed

### Performance Tips
- Use `gpt-4o-mini` for faster, cost-effective processing
- Use `gpt-4o` for best quality results
- See [OPENAI_MODELS.md](OPENAI_MODELS.md) for detailed model comparison

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test them: `make test`
4. Format your code: `make format`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Additional Resources

- [OpenAI Models Reference](OPENAI_MODELS.md) - Complete guide to available models
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [UV Package Manager](https://github.com/astral-sh/uv) 