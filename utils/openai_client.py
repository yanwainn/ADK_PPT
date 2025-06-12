"""
OpenAI client initialization and configuration management.
Supports both Azure OpenAI and direct OpenAI APIs.
"""
import os
from openai import AsyncOpenAI, AsyncAzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_api_provider():
    """Get the configured API provider (azure or openai)."""
    return os.getenv("API_PROVIDER", "azure").lower()

def get_gpt_client():
    """
    Get the appropriate GPT client based on configuration.
    
    Returns:
        AsyncOpenAI or AsyncAzureOpenAI: Configured client
    """
    provider = get_api_provider()
    
    if provider == "azure":
        return AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
        )
    else:  # openai
        return AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

def get_dalle_client():
    """
    Get the appropriate DALL-E client based on configuration.
    
    Returns:
        AsyncOpenAI or AsyncAzureOpenAI: Configured client
    """
    provider = get_api_provider()
    
    if provider == "azure":
        # Use separate DALL-E credentials if provided, otherwise use GPT credentials
        dalle_key = os.getenv("DALLE_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
        dalle_endpoint = os.getenv("DALLE_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")
        
        return AsyncAzureOpenAI(
            api_key=dalle_key,
            api_version=os.getenv("DALLE_API_VERSION", "2024-02-01"),
            azure_endpoint=dalle_endpoint,
            azure_deployment=os.getenv("DALLE_DEPLOYMENT", "dall-e-3")
        )
    else:  # openai
        return AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

def get_gpt_model():
    """
    Get the GPT model name based on configuration.
    
    Returns:
        str: Model name
    """
    provider = get_api_provider()
    
    if provider == "azure":
        return os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    else:
        return os.getenv("OPENAI_MODEL", "gpt-4")

def get_dalle_model():
    """
    Get the DALL-E model name based on configuration.
    
    Returns:
        str: Model name
    """
    provider = get_api_provider()
    
    if provider == "azure":
        return os.getenv("DALLE_DEPLOYMENT", "dall-e-3")
    else:
        return os.getenv("DALLE_MODEL", "dall-e-3")

def update_openai_settings(gpt_settings=None, dalle_settings=None, provider=None):
    """
    Update OpenAI settings in environment variables.
    
    Args:
        gpt_settings (dict): GPT configuration
        dalle_settings (dict): DALL-E configuration
        provider (str): API provider ("azure" or "openai")
    """
    if provider:
        os.environ["API_PROVIDER"] = provider
    
    current_provider = get_api_provider()
    
    if gpt_settings:
        if current_provider == "azure":
            if "api_key" in gpt_settings:
                os.environ["AZURE_OPENAI_API_KEY"] = gpt_settings["api_key"]
            if "endpoint" in gpt_settings:
                os.environ["AZURE_OPENAI_ENDPOINT"] = gpt_settings["endpoint"]
            if "deployment" in gpt_settings:
                os.environ["AZURE_OPENAI_DEPLOYMENT"] = gpt_settings["deployment"]
            if "api_version" in gpt_settings:
                os.environ["AZURE_OPENAI_API_VERSION"] = gpt_settings["api_version"]
        else:  # openai
            if "api_key" in gpt_settings:
                os.environ["OPENAI_API_KEY"] = gpt_settings["api_key"]
            if "model" in gpt_settings:
                os.environ["OPENAI_MODEL"] = gpt_settings["model"]
    
    if dalle_settings:
        if current_provider == "azure":
            if "api_key" in dalle_settings:
                os.environ["DALLE_API_KEY"] = dalle_settings["api_key"]
            if "endpoint" in dalle_settings:
                os.environ["DALLE_ENDPOINT"] = dalle_settings["endpoint"]
            if "api_version" in dalle_settings:
                os.environ["DALLE_API_VERSION"] = dalle_settings["api_version"]
            if "deployment" in dalle_settings:
                os.environ["DALLE_DEPLOYMENT"] = dalle_settings["deployment"]
        else:  # openai
            if "api_key" in dalle_settings:
                os.environ["OPENAI_API_KEY"] = dalle_settings["api_key"]
            if "model" in dalle_settings:
                os.environ["DALLE_MODEL"] = dalle_settings["model"]
