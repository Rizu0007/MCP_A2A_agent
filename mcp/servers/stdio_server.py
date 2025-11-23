import json
import sys
import logging

# CRITICAL: All logging must go to stderr, not stdout
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("FastMCP")

class FastMCP:
    """
    Minimal Model Context Protocol (MCP) server handler.
    Communicates using JSON-RPC 2.0 over stdin/stdout.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools = {}
        self.initialized = False

    # ------------------------------------------------------------------
    # Decorator for registering tools
    # ------------------------------------------------------------------
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            logger.info(f"[FastMCP] Tool registered: {func.__name__}")
            return func
        return decorator

    # ------------------------------------------------------------------
    # Main run loop
    # ------------------------------------------------------------------
    def run(self):
        logger.info(f"[FastMCP] {self.name} v{self.version} starting...")
        logger.info(f"[FastMCP] Registered tools: {list(self.tools.keys())}")
        
        try:
            # Read from stdin line by line
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                logger.debug(f"[FastMCP] Received: {line}")
                
                try:
                    message = json.loads(line)
                    self.handle_message(message)
                except json.JSONDecodeError as e:
                    logger.error(f"[FastMCP] Invalid JSON: {e}")
                    continue
                except Exception as e:
                    logger.error(f"[FastMCP] Error handling message: {e}", exc_info=True)
                    continue
                    
        except KeyboardInterrupt:
            logger.info("[FastMCP] Server stopped by KeyboardInterrupt.")
        except Exception as e:
            logger.error(f"[FastMCP] Fatal error in run loop: {e}", exc_info=True)
        finally:
            logger.info("[FastMCP] Server shutting down.")

    # ------------------------------------------------------------------
    # Handle JSON-RPC message
    # ------------------------------------------------------------------
    def handle_message(self, message: dict):
        method = message.get("method")
        msg_id = message.get("id")
        
        logger.debug(f"[FastMCP] Handling method: {method}, id: {msg_id}")

        # Handle initialization
        if method == "initialize":
            self.initialized = True
            tool_list = []
            for tool_name, tool_func in self.tools.items():
                tool_list.append({
                    "name": tool_name,
                    "description": tool_func.__doc__ or "No description",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                })
            
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": self.name,
                        "version": self.version
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }
            self.send(response)
            logger.info("[FastMCP] Initialized successfully")
            return

        # Handle notifications/ping
        if method == "notifications/initialized":
            logger.info("[FastMCP] Client confirmed initialization")
            return

        if method == "ping":
            response = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            self.send(response)
            return

        # Handle tools/list request
        if method == "tools/list":
            tool_list = []
            for tool_name, tool_func in self.tools.items():
                tool_list.append({
                    "name": tool_name,
                    "description": tool_func.__doc__ or "No description",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                })
            
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": tool_list
                }
            }
            self.send(response)
            return

        # Handle tool call
        if method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            logger.info(f"[FastMCP] Calling tool: {tool_name} with args: {args}")

            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](**args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": str(result)
                                }
                            ]
                        }
                    }
                    logger.info(f"[FastMCP] Tool {tool_name} executed successfully")
                except Exception as e:
                    logger.error(f"[FastMCP] Tool execution error: {e}", exc_info=True)
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        }
                    }
            else:
                logger.warning(f"[FastMCP] Unknown tool: {tool_name}")
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            self.send(response)
            return

        # Unknown method
        logger.warning(f"[FastMCP] Unknown method: {method}")
        if msg_id is not None:
            self.send({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })

    # ------------------------------------------------------------------
    # Send message to client
    # ------------------------------------------------------------------
    def send(self, message: dict):
        output = json.dumps(message)
        logger.debug(f"[FastMCP] Sending: {output}")
        sys.stdout.write(output + "\n")
        sys.stdout.flush()