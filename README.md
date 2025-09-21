# Pharmacist Agent

A fast, research-based OTC medication recommendation assistant powered by MCP (Model Context Protocol) servers and scientific literature.

## Overview

The Pharmacist Agent provides immediate over-the-counter medication suggestions based on scientific research papers. It uses a minimal research approach - finding the first relevant paper and providing quick recommendations without extensive analysis.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   MCP Chatbot    │───▶│  Claude API     │
│  (Symptoms)     │    │  (mcp_chatbot.py)│    │  (Anthropic)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   MCP Servers       │
                     │   (server_config)   │
                     └─────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
             ┌─────────────┐ ┌─────────┐ ┌──────────┐
             │  Research   │ │  File   │ │  Fetch   │
             │   Server    │ │ System  │ │  Server  │
             │(arXiv API)  │ │         │ │          │
             └─────────────┘ └─────────┘ └──────────┘
```

## MCP Server Architecture

### What is MCP?
Model Context Protocol (MCP) is a protocol that allows AI assistants to securely connect to external data sources and tools. It provides a standardized way for the chatbot to access different services.

### MCP Servers

1. **Research Server** (`research_server.py`)
   - **Purpose**: Searches and manages scientific research papers from arXiv
   - **Tools**: `search_papers()`, `extract_info()`, `research_active_ingredient()`
   - **Resources**: Access to paper collections via `@folders` and `@topic`
   - **Why helpful**: Provides evidence-based medication recommendations from peer-reviewed research

2. **Filesystem Server** (npm package)
   - **Purpose**: Reads and writes local files
   - **Why helpful**: Stores and retrieves cached research papers locally

3. **Fetch Server** (npm package)
   - **Purpose**: Makes HTTP requests to external APIs
   - **Why helpful**: Can fetch additional data from web sources if needed

### MCP Benefits for the Agent

- **Modularity**: Each server handles specific functionality
- **Scalability**: Easy to add new data sources without changing core chatbot code
- **Security**: Controlled access to external resources
- **Caching**: Local storage of research papers reduces API calls
- **Tool Ecosystem**: Standardized interface for diverse capabilities

## Program Control Flow

```
1. User Input
   │
   ▼
2. Safety Check (Emergency Detection)
   │
   ▼
3. MCP Server Initialization
   │
   ▼
4. Research Workflow:
   ┌─────────────────────────────────┐
   │ Check Existing Papers           │
   │ (@folders → pick first match)   │
   └─────────────────────────────────┘
   │
   ▼
   ┌─────────────────────────────────┐
   │ If No Existing Papers:          │
   │ Search arXiv (1 paper max)      │
   └─────────────────────────────────┘
   │
   ▼
5. Extract Medication Recommendations
   │
   ▼
6. Format Response (1-2 sentences)
   │
   ▼
7. Return to User
```

## Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js (for filesystem server)
- uv package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pharmacist-agent
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   uv sync
   # OR manually install:
   pip install anthropic mcp arxiv python-dotenv nest-asyncio
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
   ```

5. **Install Node.js dependencies** (for filesystem server)
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   ```

## Running the Program

### Start the Chatbot
```bash
uv run mcp_chatbot.py
# OR
python mcp_chatbot.py
```

### Usage Example
```
📋 Research-Based OTC Recommendations
===================================
Describe your symptom:
Type 'quit' to exit
===================================

Query: headache

Research suggests ibuprofen 200mg for headaches. Source: Pain Management Study 2023.

Query: quit
```

## Configuration

### MCP Server Configuration (`server_config.json`)
```json
{
    "mcpServers": {
        "research": {
            "command": "sh",
            "args": ["-c", "uv run research_server.py 2>/dev/null"]
        },
        "filesystem": {
            "command": "sh",
            "args": ["-c", "npx -y @modelcontextprotocol/server-filesystem . 2>/dev/null"]
        },
        "fetch": {
            "command": "sh",
            "args": ["-c", "uvx mcp-server-fetch 2>/dev/null"]
        }
    }
}
```

## Key Features

- **Minimal Research**: Maximum 1 paper lookup per query
- **Fast Responses**: 1-2 sentence recommendations only
- **Research-Based**: Only suggests medications found in scientific papers
- **Cached Papers**: Reuses existing research to avoid redundant API calls
- **Emergency Detection**: Basic safety checks for serious symptoms

## Limitations

- Cannot diagnose medical conditions
- Only recommends over-the-counter medications
- Limited to research findings (no general medical knowledge)
- Single paper per recommendation
- No safety warnings or detailed medical advice

## File Structure

```
pharmacist-agent/
├── mcp_chatbot.py          # Main chatbot application
├── research_server.py      # MCP server for arXiv research
├── server_config.json      # MCP server configuration
├── .env                    # API keys (create manually)
├── papers/                 # Cached research papers
└── README.md              # This file
```
