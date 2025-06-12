# OpenAI Models Reference Guide

This document provides a comprehensive list of OpenAI LLM models available through the OpenAI API platform as of 2024-2025.

## Table of Contents
- [Latest GPT-4 Series Models](#latest-gpt-4-series-models)
- [Reasoning Models (o-series)](#reasoning-models-o-series)
- [GPT-4 Legacy Models](#gpt-4-legacy-models)
- [GPT-3.5 Models](#gpt-35-models)
- [Preview/Experimental Models](#previewexperimental-models)
- [Model Capabilities Comparison](#model-capabilities-comparison)
- [Recommendations](#recommendations)
- [Usage Examples](#usage-examples)

## Latest GPT-4 Series Models

### GPT-4o (Omni) Series
The most advanced multimodal models supporting text and image inputs.

| Model Name | Version | Description | Context Window | Max Output | Training Data |
|------------|---------|-------------|----------------|------------|---------------|
| `gpt-4o` | `2024-11-20` | **Latest large GA model** with enhanced creative writing | 128,000 | 16,384 | Oct 2023 |
| `gpt-4o` | `2024-08-06` | Structured outputs, multimodal capabilities | 128,000 | 16,384 | Oct 2023 |
| `gpt-4o` | `2024-05-13` | Original GPT-4o release | 128,000 | 4,096 | Oct 2023 |
| `gpt-4o-mini` | `2024-07-18` | **Latest small GA model** - fast, cost-effective | 128,000 | 16,384 | Oct 2023 |

**Key Features:**
- Text and image processing
- JSON Mode
- Parallel function calling
- Enhanced accuracy and responsiveness
- Superior performance in non-English languages
- Structured outputs

### GPT-4.1 Series (Latest Release)
The newest generation of GPT models with enhanced capabilities.

| Model Name | Version | Description | Context Window | Max Output | Training Data |
|------------|---------|-------------|----------------|------------|---------------|
| `gpt-4.1` | `2025-04-14` | Latest flagship model | 1,047,576 | 32,768 | May 31, 2024 |
| `gpt-4.1-nano` | `2025-04-14` | **Fastest 4.1 model** | 1,047,576 | 32,768 | May 31, 2024 |
| `gpt-4.1-mini` | `2025-04-14` | Balanced performance and efficiency | 1,047,576 | 32,768 | May 31, 2024 |

**Key Features:**
- Massive context window (1M+ tokens)
- Text and image input
- Chat completions API
- Responses API
- Streaming support
- Function calling
- Structured outputs

### GPT-4 Turbo
| Model Name | Version | Description | Context Window | Max Output | Training Data |
|------------|---------|-------------|----------------|------------|---------------|
| `gpt-4-turbo` | `turbo-2024-04-09` | GPT-4 Turbo with Vision (GA) | 128,000 | 4,096 | Dec 2023 |

## Reasoning Models (o-series)

Advanced models designed for complex reasoning and problem-solving tasks.

| Model Name | Version | Description | Max Request Tokens | Training Data |
|------------|---------|-------------|-------------------|---------------|
| `o3` | `2025-04-16` | **Latest reasoning model** with enhanced abilities | Input: 200,000<br>Output: 100,000 | May 31, 2024 |
| `o4-mini` | `2025-04-16` | **New reasoning model** with enhanced capabilities | Input: 200,000<br>Output: 100,000 | May 31, 2024 |
| `o3-mini` | `2025-01-31` | Enhanced reasoning, text-only processing | Input: 200,000<br>Output: 100,000 | Oct 2023 |
| `o1` | `2024-12-17` | Enhanced reasoning with text and image processing | Input: 200,000<br>Output: 100,000 | Oct 2023 |
| `o1-preview` | `2024-09-12` | Older preview version | Input: 128,000<br>Output: 32,768 | Oct 2023 |
| `o1-mini` | `2024-09-12` | Faster, cost-efficient for coding tasks | Input: 128,000<br>Output: 65,536 | Oct 2023 |

**Key Features:**
- Advanced reasoning capabilities
- Excellent for science, coding, and math
- Structured outputs
- Functions/Tools support
- Enhanced problem-solving focus

## GPT-4 Legacy Models

Older but stable GPT-4 models still available for use.

| Model Name | Version | Description | Context Window | Training Data |
|------------|---------|-------------|----------------|---------------|
| `gpt-4` | `0613` | Older GA model with basic function calling | 8,192 | Sep 2021 |
| `gpt-4` | `0314` | Original GPT-4 release | 8,192 | Sep 2021 |
| `gpt-4-32k` | `0613` | Extended context version | 32,768 | Sep 2021 |
| `gpt-4-32k` | `0314` | Original 32k context version | 32,768 | Sep 2021 |

## GPT-3.5 Models

Cost-effective models for simpler tasks.

| Model Name | Version | Description | Max Request Tokens | Training Data |
|------------|---------|-------------|-------------------|---------------|
| `gpt-3.5-turbo` | `0125` | **Latest GA Model** with JSON Mode | Input: 16,385<br>Output: 4,096 | Sep 2021 |
| `gpt-3.5-turbo` | `1106` | Older GA Model with parallel function calling | Input: 16,385<br>Output: 4,096 | Sep 2021 |
| `gpt-3.5-turbo-instruct` | `0914` | **Completions endpoint only** | 4,097 | Sep 2021 |
| `gpt-3.5-turbo-16k` | `0613` | Extended context version | 16,384 | Sep 2021 |

**Key Features:**
- JSON Mode
- Parallel function calling
- Reproducible output (preview)
- Cost-effective for basic tasks

## Preview/Experimental Models

⚠️ **Warning:** Preview models are not recommended for production use.

| Model Name | Version | Description | Context Window | Max Output |
|------------|---------|-------------|----------------|------------|
| `gpt-4.5-preview` | `2025-02-27` | Preview of GPT-4.5 capabilities | 128,000 | 16,384 |
| `computer-use-preview` | `2025-03-11` | Specialized for computer control tasks | 8,192 | 1,024 |

## Model Capabilities Comparison

| Feature | GPT-4o | GPT-4.1 | o-series | GPT-4 Legacy | GPT-3.5 |
|---------|--------|---------|----------|--------------|---------|
| **Text Processing** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Image Processing** | ✅ | ✅ | ✅ (o1, o3) | ❌ | ❌ |
| **Function Calling** | ✅ | ✅ | ✅ | ✅ (basic) | ✅ |
| **Structured Outputs** | ✅ | ✅ | ✅ | ❌ | ✅ (0125+) |
| **JSON Mode** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Streaming** | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Reasoning Focus** | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Context Window** | 128K | 1M+ | 200K | 8K-32K | 16K |

## Recommendations

### For General Purpose Applications
- **`gpt-4o`** (`2024-11-20`) - Best overall performance and features
- **`gpt-4o-mini`** - Cost-effective with good performance

### For Complex Reasoning Tasks
- **`o3`** or **`o4-mini`** - Latest reasoning capabilities
- **`o1`** - Proven reasoning performance

### For Cost-Sensitive Applications
- **`gpt-4o-mini`** - Best price-to-performance ratio
- **`gpt-3.5-turbo`** (`0125`) - Most economical option

### For Legacy Compatibility
- **`gpt-4`** (`0613`) - Stable, well-tested
- **`gpt-3.5-turbo`** (`0125`) - Reliable fallback

### For Multimodal Applications
- **`gpt-4o`** series - Best image and text processing
- **`o1`** or **`o3`** - For reasoning with images

## Usage Examples

### Basic Chat Completion
```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",  # or any model from the list above
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing"}
    ]
)
```

### With Function Calling
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather like?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                }
            }
        }
    }]
)
```

### With Image Input (Multimodal)
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
    }]
)
```

## Configuration for This Project

For the PDF to PowerPoint generator project, recommended models:

```env
# Primary recommendation
OPENAI_MODEL=gpt-4o

# Cost-effective alternative
OPENAI_MODEL=gpt-4o-mini

# For complex document analysis
OPENAI_MODEL=o3
```

## Model Selection Guidelines

1. **Start with `gpt-4o-mini`** for development and testing
2. **Upgrade to `gpt-4o`** for production with better quality needs
3. **Use `o3` or `o1`** for complex reasoning tasks
4. **Consider `gpt-3.5-turbo`** only for very simple, cost-sensitive tasks
5. **Avoid preview models** in production environments

## Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Model Pricing](https://openai.com/pricing)
- [Rate Limits](https://platform.openai.com/docs/guides/rate-limits)
- [Best Practices](https://platform.openai.com/docs/guides/best-practices)

---

*Last updated: January 2025*
*This document reflects the latest available OpenAI models as of the update date.* 