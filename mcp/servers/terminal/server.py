import os
import sys
import subprocess
import logging

# -------------------------------------------------------------------
# Ensure the project root (where "mcp" package lives) is on sys.path
# -------------------------------------------------------------------
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# -------------------------------------------------------------------
# Import FastMCP from your local mcp.servers.fastmcp
# -------------------------------------------------------------------
try:
    from mcp.servers.stdio_server import FastMCP
except ModuleNotFoundError as e:
    print(f"[ERROR] Could not import FastMCP. Check your project structure.", file=sys.stderr)
    print(f"Expected file: {project_root}/mcp/servers/stdio_server.py", file=sys.stderr)
    print(f"Current sys.path: {sys.path}", file=sys.stderr)
    raise e

# -------------------------------------------------------------------
# Logging Setup - LOG TO STDERR (not stdout, which is for JSON-RPC)
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    stream=sys.stderr  # CRITICAL: Log to stderr, not stdout
)
logger = logging.getLogger("terminal_server")

# -------------------------------------------------------------------
# Initialize the MCP Server
# -------------------------------------------------------------------
mcp = FastMCP("Terminal Server", version="1.0.0")

# -------------------------------------------------------------------
# Default project directory
# -------------------------------------------------------------------
DEFAULT_PROJECT_DIR = os.path.abspath("C:/Users/Documents/mcp/MCP---A2A")

# -------------------------------------------------------------------
# Tools
# -------------------------------------------------------------------
@mcp.tool()
def run_command(command: str) -> str:
    """Execute a shell command and return its output."""
    try:
        logger.info(f"[Tool] Executing command: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"Exit code: {result.returncode}")

        if not output:
            return "(Command executed successfully, no output)"

        return "\n\n".join(output)

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        logger.error(f"[Tool] Command execution failed: {e}")
        return f"Command execution failed: {str(e)}"


@mcp.tool()
def list_files(path: str = None) -> str:
    """List all files and folders in a given path. Defaults to the project directory."""
    try:
        target_path = path or DEFAULT_PROJECT_DIR
        logger.info(f"[Tool] Listing files in: {target_path}")
        abs_path = os.path.abspath(target_path)

        if not os.path.exists(abs_path):
            return f"Error: Path does not exist: {abs_path}"

        if not os.path.isdir(abs_path):
            return f"Error: Path is not a directory: {abs_path}"

        items = os.listdir(abs_path)
        if not items:
            return f"(Empty directory: {abs_path})"

        # Separate directories and files
        dirs = []
        files = []
        for item in sorted(items):
            item_path = os.path.join(abs_path, item)
            if os.path.isdir(item_path):
                dirs.append(f"[DIR]  {item}")
            else:
                files.append(f"[FILE] {item}")

        result = [f"Contents of: {abs_path}", ""]
        result.extend(dirs)
        result.extend(files)
        result.append(f"\nTotal: {len(dirs)} directories, {len(files)} files")

        return "\n".join(result)

    except Exception as e:
        logger.error(f"[Tool] List files failed: {e}")
        return f"Error: {str(e)}"

# -------------------------------------------------------------------
# Start Server
# -------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("[MCP] Terminal Server Starting...")
    logger.info(f"[MCP] Python: {sys.version}")
    logger.info(f"[MCP] Working directory: {os.getcwd()}")
    logger.info(f"[MCP] Project root: {project_root}")
    logger.info("=" * 60)

    try:
        mcp.run()
        logger.info("[MCP] Server exited normally.")
    except KeyboardInterrupt:
        logger.warning("[MCP] Server stopped manually.")
    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        sys.exit(1)
