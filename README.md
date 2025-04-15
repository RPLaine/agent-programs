# Dolphin AI Example

A versatile AI assistant that uses an LLM API for natural language processing, web research, and content generation.

## Overview

Dolphin AI is a framework that:
- Creates and manages AI-powered jobs based on user requests
- Performs automated web research and content analysis
- Supports various text processing tasks through specialized tools
- Generates reports based on collected information

The system uses the Dolphin LLM API (https://www.northbeach.fi/dolphin) as its core processing engine.

## Setup Instructions

1. Create a virtual environment:
   ```
   # Install virtualenv if not already installed
   pip install virtualenv
   
   # Create a virtual environment
   virtualenv venv
   ```

2. Activate the virtual environment:
   ```
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running Dolphin AI

Start the application by running:

```
python main.py
```

This will launch the Dolphin AI interactive menu with the following options:
1. Create a new job
2. Get status report
3. Exit

## Using the System

### Creating a Job
When prompted, describe the job you want Dolphin AI to perform. Examples:
- "Find out the height of Donald Trump"
- "Research the latest developments in quantum computing"
- "Summarize news articles about climate change"

The system will analyze your request, gather information from the web if needed, and generate a result file in the `output` directory.

### Getting Status Reports
You can check the status of all jobs or a specific job by ID. The system will show:
- Job ID
- Description
- Status (Created, Analyzing, In Progress, Working, Completed, Failed)
- Creation and last updated timestamps

## Project Structure

- **main.py**: Core application entry point
- **utility/**: Contains core system components
  - job_manager.py: Manages job creation and tracking
  - tool_manager.py: Discovers and loads tools
  - file_handler.py: Handles file operations
  - user_interaction.py: Manages user interface elements
- **tools/**: Collection of specialized AI tools
  - web/: Tools for web interactions and research
  - utils/: Utility functions and helpers
  - Various specialized tools (summarization, fact checking, etc.)
- **output/**: Generated results from completed jobs
- **files/**: Storage for user files and data

## Tool Capabilities

Dolphin AI includes tools for:
- Web research and content extraction
- Text summarization and distillation
- Fact checking and verification
- Information extraction and analysis
- Sentiment analysis
- Content generation
- And many more specialized text processing tasks

### Key Tools

#### Web Research (`tools/web/web_research.py`)
The web research component powers Dolphin AI's ability to search the internet and extract relevant information:

- **Automatic Search Optimization**: Intelligently determines the optimal number of search results needed (1-5) based on the query complexity
- **Focused Content Extraction**: Retrieves HTML content from search results and extracts meaningful text
- **Smart Summarization**: Applies targeted summarization to each webpage with custom focus parameters
- **Information Distillation**: Consolidates information from multiple sources into a comprehensive summary
- **Source Attribution**: Maintains references to source URLs for fact-checking and citation

Usage example:
```python
from tools.web.web_research import get_web_research

results = get_web_research(
    query="What are the health benefits of intermittent fasting?",
    num_results=3,
    custom_focus="scientific studies and medical consensus"
)
```

#### Text Summarization (`tools/summarization.py`)
The summarization engine processes and condenses long-form content:

- **Recursive Processing**: Handles texts of any length through recursive summarization techniques
- **Focus-Based Filtering**: Concentrates on specific topics or aspects within larger texts
- **Intelligent Text Splitting**: Breaks large documents into semantically coherent segments
- **Content Relevance Validation**: Evaluates if content matches the specified focus area
- **Context Preservation**: Maintains important context and factual accuracy while reducing text volume

The summarization engine can handle documents of virtually any length by utilizing a recursive approach that splits content, summarizes each part, and then creates a consolidated summary.

## License

[Your license information here]