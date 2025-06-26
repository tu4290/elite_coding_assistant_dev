#!/usr/bin/env python3
"""
Real-Time Server Startup Script

This script provides an easy way to start the real-time features server
with proper configuration, logging, and monitoring.
"""

import asyncio
import logging
import os
import sys
import signal
from pathlib import Path
from typing import Optional

import uvicorn
import redis.asyncio as redis
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Add main directory to path
sys.path.append(str(Path(__file__).parent / "main"))

from realtime_api_server import app

# Configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8001
DEFAULT_REDIS_URL = "redis://localhost:6379/0"
DEFAULT_LOG_LEVEL = "INFO"

console = Console()

def setup_logging(log_level: str = "INFO") -> None:
    """Setup rich logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                show_path=False
            )
        ]
    )

async def check_redis_connection(redis_url: str) -> bool:
    """Check if Redis is available"""
    try:
        client = redis.from_url(redis_url)
        await client.ping()
        await client.close()
        return True
    except Exception as e:
        console.print(f"[red]Redis connection failed: {e}[/red]")
        return False

def display_startup_info(host: str, port: int, redis_url: str) -> None:
    """Display startup information"""
    # Create startup panel
    startup_text = Text()
    startup_text.append("🚀 Elite Coding Assistant - Real-Time Server\n\n", style="bold blue")
    startup_text.append(f"Server URL: ", style="bold")
    startup_text.append(f"http://{host}:{port}\n", style="green")
    startup_text.append(f"WebSocket URL: ", style="bold")
    startup_text.append(f"ws://{host}:{port}/ws\n", style="green")
    startup_text.append(f"Redis URL: ", style="bold")
    startup_text.append(f"{redis_url}\n", style="yellow")
    
    panel = Panel(
        startup_text,
        title="[bold green]Server Configuration[/bold green]",
        border_style="green"
    )
    console.print(panel)
    
    # Create endpoints table
    table = Table(title="Available Endpoints", show_header=True, header_style="bold magenta")
    table.add_column("Method", style="cyan")
    table.add_column("Endpoint", style="green")
    table.add_column("Description", style="white")
    
    endpoints = [
        ("GET", "/", "API documentation (Swagger UI)"),
        ("GET", "/health", "Health check endpoint"),
        ("GET", "/stats", "System statistics"),
        ("WS", "/ws", "WebSocket connection endpoint"),
        ("POST", "/metrics", "Publish metrics"),
        ("POST", "/feedback", "Submit feedback"),
        ("GET/POST", "/notifications", "Notification management"),
        ("POST", "/collaboration/start", "Start collaborative session"),
        ("POST", "/debug/start", "Start debug session"),
    ]
    
    for method, endpoint, description in endpoints:
        table.add_row(method, endpoint, description)
    
    console.print(table)
    console.print()

def display_usage_examples() -> None:
    """Display usage examples"""
    examples_text = Text()
    examples_text.append("📝 Usage Examples:\n\n", style="bold blue")
    
    examples_text.append("1. WebSocket Connection (JavaScript):\n", style="bold")
    examples_text.append("   const ws = new WebSocket('ws://localhost:8001/ws?token=user123:session456');\n\n", style="green")
    
    examples_text.append("2. Health Check (curl):\n", style="bold")
    examples_text.append("   curl http://localhost:8001/health\n\n", style="green")
    
    examples_text.append("3. Submit Metrics (curl):\n", style="bold")
    examples_text.append("   curl -X POST http://localhost:8001/metrics \\\n", style="green")
    examples_text.append("        -H 'Authorization: Bearer user123:session456' \\\n", style="green")
    examples_text.append("        -H 'Content-Type: application/json' \\\n", style="green")
    examples_text.append("        -d '{\"metric_type\": \"test\", \"value\": 42.0}'\n\n", style="green")
    
    examples_text.append("4. Start Collaboration (curl):\n", style="bold")
    examples_text.append("   curl -X POST http://localhost:8001/collaboration/start \\\n", style="green")
    examples_text.append("        -H 'Authorization: Bearer user123:session456' \\\n", style="green")
    examples_text.append("        -H 'Content-Type: application/json' \\\n", style="green")
    examples_text.append("        -d '{\"file_path\": \"test.py\", \"content\": \"print('hello')\"}'", style="green")
    
    panel = Panel(
        examples_text,
        title="[bold yellow]Usage Examples[/bold yellow]",
        border_style="yellow"
    )
    console.print(panel)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    console.print("\n[yellow]Received shutdown signal. Stopping server...[/yellow]")
    sys.exit(0)

async def main():
    """Main startup function"""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Start the Elite Coding Assistant Real-Time Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_realtime_server.py                    # Start with defaults
  python start_realtime_server.py --port 8002       # Custom port
  python start_realtime_server.py --host 0.0.0.0    # Bind to all interfaces
  python start_realtime_server.py --debug           # Enable debug mode
        """
    )
    
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", DEFAULT_HOST),
        help=f"Host to bind to (default: {DEFAULT_HOST})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", DEFAULT_PORT)),
        help=f"Port to bind to (default: {DEFAULT_PORT})"
    )
    
    parser.add_argument(
        "--redis-url",
        default=os.getenv("REDIS_URL", DEFAULT_REDIS_URL),
        help=f"Redis connection URL (default: {DEFAULT_REDIS_URL})"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL),
        help=f"Log level (default: {DEFAULT_LOG_LEVEL})"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (auto-reload, detailed logging)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Show usage examples and exit"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else args.log_level
    setup_logging(log_level)
    
    # Show examples if requested
    if args.examples:
        display_usage_examples()
        return
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Display startup information
    console.print("[bold blue]🚀 Starting Elite Coding Assistant Real-Time Server...[/bold blue]\n")
    
    # Check Redis connection
    console.print("[yellow]Checking Redis connection...[/yellow]")
    if not await check_redis_connection(args.redis_url):
        console.print("[red]❌ Redis connection failed. Please ensure Redis is running.[/red]")
        console.print("[yellow]💡 To start Redis with Docker:[/yellow]")
        console.print("   docker run -d -p 6379:6379 redis:alpine")
        sys.exit(1)
    
    console.print("[green]✅ Redis connection successful[/green]\n")
    
    # Display configuration
    display_startup_info(args.host, args.port, args.redis_url)
    
    # Set environment variables for the app
    os.environ["REDIS_URL"] = args.redis_url
    
    # Configure uvicorn
    config = uvicorn.Config(
        app="realtime_api_server:app",
        host=args.host,
        port=args.port,
        log_level=log_level.lower(),
        reload=args.debug,
        workers=args.workers if not args.debug else 1,
        access_log=True,
        app_dir="main"
    )
    
    # Start server
    server = uvicorn.Server(config)
    
    try:
        console.print("[green]🎉 Server starting...[/green]")
        console.print("[dim]Press Ctrl+C to stop the server[/dim]\n")
        await server.serve()
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Server error: {e}[/red]")
        sys.exit(1)

def run_sync():
    """Synchronous entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Startup interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Startup error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    run_sync()