<img width="964" height="936" alt="image" src="https://github.com/user-attachments/assets/adba0b94-7f53-4574-bbb4-9101d782cd8b" />

# MCPA2A - Multi-Agent Communication Platform

## What Problem Does It Solve?

Modern AI systems need agents that can:
- **Communicate with each other** - Different AI agents (using different LLMs like Gemini, GPT-4, etc.) need to collaborate
- **Access external tools** - Agents need to use APIs, databases, and enterprise applications
- **Work together seamlessly** - No matter what framework they're built with

**MCPA2A solves this** by combining two protocols:
- **A2A (Agent-to-Agent)** - For agent communication
- **MCP (Model Context Protocol)** - For tool access


## How It Works

1. **Host Agent** receives user requests
2. **Discovers available agents** from registry (A2A protocol)
3. **Loads available tools** from MCP servers
4. **Routes the task** to the right agent or tool
5. **Returns the response** to the user

## Project Structure

```
MCPA2A/
├── app/cli/client.py              # CLI client
├── agents/
│   ├── host_agent/                # Orchestrator (port 10001)
│   └── website_builder/           # Child agent (port 10000)
├── mcp/servers/
│   ├── stdio_server.py            # MCP server implementation
│   ├── arithmetic_server.py       # HTTP MCP server
│   └── terminal/server.py         # Shell command server
├── core/
│   ├── a2a/                       # A2A utilities
│   ├── mcp/                       # MCP utilities
│   └── common/                    # Shared utilities
└── pyproject.toml
```

## Installation

```bash
git clone https://github.com/yourusername/MCPA2A.git
cd MCPA2A
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Add your `GOOGLE_API_KEY` to `.env` file.

## Configuration

### Register Agents

Edit `core/a2a/agent_registry.json`:

```json
[
    "http://localhost:10000"
]
```

### Configure MCP Servers

Edit `core/mcp/mcp_config.json`:

```json
{
  "mcpServers": {
    "terminal_server": {
      "command": "python",
      "args": ["mcp/servers/terminal/server.py"]
    }
  }
}
```

## Usage

```bash
# Terminal 1: Start child agent
python -m agents.website_builder --port 10000

# Terminal 2: Start host agent
python -m agents.host_agent --port 10001

# Terminal 3: Send queries
python app/cli/client.py --agent http://localhost:10001
```

## Dependencies

- a2a-sdk
- fastmcp
- google-adk
- uvicorn
- httpx

## License

MIT License
