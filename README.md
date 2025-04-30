# Agent Programs

This repository contains an AI agent system that can perform various tasks like web searches, RSS feed processing, and content improvement.

## Setup Instructions

### 1. Setting up a Virtual Environment

Creating a virtual environment is recommended to isolate the project dependencies:

```powershell
# Navigate to the project root
cd d:\git\agent-programs

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate

# You should see (venv) at the beginning of your command prompt
```

### 2. Installing Requirements

Install all required dependencies using the requirements.txt file:

```powershell
pip install -r requirements.txt
```

This will install necessary packages including:
- requests
- googlesearch-python
- feedparser
- beautifulsoup4
- PyPDF2
- mimetypes-magic
- selenium
- webdriver-manager
- pandas
- aiohttp

### 3. Configuring Worker Settings

Before running the program, you may need to modify the settings in `worker/settings.py`. The main parameters to configure are:

#### Content and Claim

The `content` is the initial text that will be processed and improved. The `claim` defines the target state or goal for the content improvement.

```python
# In worker/settings.py
content: str = "Your initial content here"  # Replace with your content

settings: dict = {
    "claim": "your target goal",  # Define what you want to achieve
    "content": [content],
    # Other settings...
}
```

#### Other Important Settings

- `iterations`: Number of processing cycles
- `pass_value`: Threshold for success (0.0-1.0)
- `agent.llm_url`: URL for the language model service
- `tools`: List of tools available to the agent

### 4. Running the Program

Execute the program using the following command from the project root:

```powershell
python -m worker.main
```

This will start the agent program with the settings defined in `worker/settings.py`. The program will:
1. Initialize with the specified action (default is "test")
2. Run through iterations of test and work actions
3. Process the content according to the specified claim
4. Output results to the console and save data as configured

## Project Structure Overview

- `worker/`: Core agent functionality
  - `main.py`: Entry point
  - `settings.py`: Configuration
  - `plan.py`, `work.py`, `test.py`: Action modules
  - `tools/`: Agent tools
  - `prompts/`: Prompt templates

- `tools/`: Utility tools for various tasks
- `webget/`: Web crawling and data extraction
- `web_crawler/`: Advanced web crawling capabilities

## Troubleshooting

If you encounter any issues:
1. Ensure your virtual environment is activated
2. Verify all dependencies are installed correctly
3. Check that the settings in `worker/settings.py` are configured properly
4. Make sure you're running the command from the project root directory
