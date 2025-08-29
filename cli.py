"""Command Line Interface for MCP Terminal Server."""

import argparse
import asyncio
import logging
import sys
import os
from typing import Optional

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_terminal_server import main as server_main

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=os.path.join(log_dir, "mcp_terminal_server.log"),
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="mcp-terminal-server",
        description="MCP Terminal Server - Execute terminal commands via MCP protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,        
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def main(args: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Setup logging
    setup_logging(parsed_args.verbose)
    
    # Create logger
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting MCP Terminal Server")
        
        # Run the server
        server_main.mcp_server.run(transport='stdio')
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())