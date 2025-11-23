import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from core.mcp.mcp_discovery import MCPDiscovery
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from mcp import StdioServerParameters


class MCPConnect:
    """
      Discovers the MCP servers from the config.
      Config will be loaded by the MCP discovery class
      Then it lists each server's tools
      and then caches them as MCPToolsets that are compatible with
      Google's Agent Development Kit
    """

    def __init__(self, config_file: str = None):
        self.discovery = MCPDiscovery(config_file=config_file)
        self.tools: list[MCPToolset] = []


    async def _load_all_tools(self):
        """
          Loads all the tools from each discovered MCP server
        """
        tools = []
        for name, server in self.discovery.list_mcp_servers().items():
            try:
                if server.get("command") == "streamable_http":
                    conn = StreamableHTTPServerParams(url=server["args"][0])
                else:
                    conn = StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command=server["command"],
                            args=server["args"]
                        ),
                        timeout=5
                    )

                toolset = MCPToolset(connection_params=conn)
                loaded_tools = await toolset.load_tools()
                tool_names = [tool.name for tool in loaded_tools]
                print(f"Loaded tools from server '{name}': {', '.join(tool_names)}")
                tools.append(toolset)

            except Exception as e:
                print(f"Error loading tools from server '{name}': {e}")

        return tools

    async def get_tools(self) -> list:
        """
        Get all tools from all MCP servers.
        Returns a flat list of tools.
        """
        if not self.tools:
            self.tools = await self._load_all_tools()

        all_tools = []
        for toolset in self.tools:
            all_tools.extend(toolset)

        return all_tools


# Alias for backward compatibility with imports expecting MCPConnector
MCPConnector = MCPConnect
