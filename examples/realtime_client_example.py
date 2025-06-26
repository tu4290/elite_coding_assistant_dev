#!/usr/bin/env python3
"""
Real-Time Client Example

This example demonstrates how to interact with the Elite Coding Assistant
real-time features, including WebSocket communication, collaborative editing,
and live data streaming.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import websockets
import httpx
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text

# Configuration
SERVER_URL = "http://localhost:8001"
WEBSOCKET_URL = "ws://localhost:8001/ws"
USER_ID = "demo_user_123"
SESSION_ID = "demo_session_456"
TOKEN = f"{USER_ID}:{SESSION_ID}"

console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, show_path=False)]
)
logger = logging.getLogger(__name__)

class RealTimeClient:
    """Real-time client for interacting with the server"""
    
    def __init__(self, server_url: str, websocket_url: str, token: str):
        self.server_url = server_url
        self.websocket_url = websocket_url
        self.token = token
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.message_handlers: Dict[str, callable] = {}
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "connection_time": None,
            "last_heartbeat": None
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Connect to the server"""
        # Setup HTTP client
        self.http_client = httpx.AsyncClient(
            base_url=self.server_url,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        # Connect WebSocket
        try:
            self.websocket = await websockets.connect(
                f"{self.websocket_url}?token={self.token}"
            )
            self.stats["connection_time"] = datetime.now()
            console.print("[green]✅ Connected to WebSocket server[/green]")
        except Exception as e:
            console.print(f"[red]❌ WebSocket connection failed: {e}[/red]")
            raise
    
    async def disconnect(self):
        """Disconnect from the server"""
        if self.websocket:
            await self.websocket.close()
            console.print("[yellow]🔌 WebSocket disconnected[/yellow]")
        
        if self.http_client:
            await self.http_client.aclose()
            console.print("[yellow]🔌 HTTP client closed[/yellow]")
    
    def register_handler(self, event_type: str, handler: callable):
        """Register a message handler for specific event types"""
        self.message_handlers[event_type] = handler
    
    async def send_message(self, event_type: str, data: Dict[str, Any]):
        """Send a message via WebSocket"""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        message = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.websocket.send(json.dumps(message))
        self.stats["messages_sent"] += 1
        logger.info(f"Sent {event_type} message")
    
    async def listen_for_messages(self):
        """Listen for incoming WebSocket messages"""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    event_type = data.get("event_type")
                    
                    self.stats["messages_received"] += 1
                    
                    if event_type == "heartbeat":
                        self.stats["last_heartbeat"] = datetime.now()
                        continue
                    
                    # Handle message with registered handler
                    if event_type in self.message_handlers:
                        await self.message_handlers[event_type](data)
                    else:
                        logger.info(f"Received {event_type}: {data.get('data', {})}")
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            console.print("[yellow]WebSocket connection closed[/yellow]")
        except Exception as e:
            console.print(f"[red]WebSocket error: {e}[/red]")
    
    async def check_health(self) -> Dict[str, Any]:
        """Check server health"""
        response = await self.http_client.get("/health")
        response.raise_for_status()
        return response.json()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        response = await self.http_client.get("/stats")
        response.raise_for_status()
        return response.json()
    
    async def submit_metric(self, metric_type: str, value: float, tags: Dict[str, str] = None):
        """Submit a metric to the server"""
        payload = {
            "metric_type": metric_type,
            "value": value,
            "tags": tags or {}
        }
        
        response = await self.http_client.post("/metrics", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def submit_feedback(self, feedback_type: str, content: str, rating: int = None):
        """Submit feedback to the server"""
        payload = {
            "feedback_type": feedback_type,
            "content": content,
            "rating": rating
        }
        
        response = await self.http_client.post("/feedback", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def start_collaboration(self, file_path: str, content: str):
        """Start a collaborative editing session"""
        payload = {
            "file_path": file_path,
            "content": content
        }
        
        response = await self.http_client.post("/collaboration/start", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def apply_code_operation(self, file_path: str, operation_type: str, position: int, content: str):
        """Apply a code operation in collaborative editing"""
        payload = {
            "operation_type": operation_type,
            "position": position,
            "content": content
        }
        
        response = await self.http_client.post(
            f"/collaboration/{file_path}/operation",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def start_debug_session(self, file_path: str, breakpoints: list = None):
        """Start a debugging session"""
        payload = {
            "file_path": file_path,
            "breakpoints": breakpoints or []
        }
        
        response = await self.http_client.post("/debug/start", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def create_notification(self, notification_type: str, title: str, message: str, user_id: str = None):
        """Create a notification"""
        payload = {
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "user_id": user_id or USER_ID
        }
        
        response = await self.http_client.post("/notifications", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def get_notifications(self):
        """Get user notifications"""
        response = await self.http_client.get("/notifications")
        response.raise_for_status()
        return response.json()

def create_stats_table(client_stats: Dict[str, Any], server_stats: Dict[str, Any] = None) -> Table:
    """Create a statistics table"""
    table = Table(title="Real-Time Client Statistics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    # Client stats
    table.add_row("Messages Sent", str(client_stats["messages_sent"]))
    table.add_row("Messages Received", str(client_stats["messages_received"]))
    
    if client_stats["connection_time"]:
        uptime = datetime.now() - client_stats["connection_time"]
        table.add_row("Connection Uptime", str(uptime).split('.')[0])
    
    if client_stats["last_heartbeat"]:
        last_hb = client_stats["last_heartbeat"].strftime("%H:%M:%S")
        table.add_row("Last Heartbeat", last_hb)
    
    # Server stats (if available)
    if server_stats:
        table.add_row("---", "---")
        ws_stats = server_stats.get("websocket", {})
        table.add_row("Server Connections", str(ws_stats.get("total_connections", 0)))
        table.add_row("Server Users", str(len(ws_stats.get("users", []))))
    
    return table

async def demo_chat_messages(client: RealTimeClient):
    """Demonstrate chat messaging"""
    console.print("\n[bold blue]🗨️  Chat Messages Demo[/bold blue]")
    
    # Register chat message handler
    async def handle_chat(data):
        message_data = data.get("data", {})
        user = message_data.get("user", "Unknown")
        content = message_data.get("content", "")
        console.print(f"[green]💬 {user}:[/green] {content}")
    
    client.register_handler("chat_message", handle_chat)
    
    # Send some chat messages
    messages = [
        "Hello, real-time world! 👋",
        "This is a demo of live chat functionality",
        "Messages are sent via WebSocket and broadcasted to all connected clients"
    ]
    
    for message in messages:
        await client.send_message("chat_message", {
            "user": USER_ID,
            "content": message
        })
        await asyncio.sleep(1)

async def demo_collaborative_editing(client: RealTimeClient):
    """Demonstrate collaborative editing"""
    console.print("\n[bold blue]👥 Collaborative Editing Demo[/bold blue]")
    
    file_path = "demo_file.py"
    initial_content = "# Demo Python file\nprint('Hello, World!')\n"
    
    # Start collaboration
    result = await client.start_collaboration(file_path, initial_content)
    console.print(f"[green]✅ Started collaboration for {file_path}[/green]")
    
    # Apply some operations
    operations = [
        ("insert", 45, "\n# Added by collaborative editing"),
        ("insert", 45 + 30, "\nprint('Collaborative coding is awesome!')"),
        ("replace", 20, "Universe")
    ]
    
    for op_type, position, content in operations:
        result = await client.apply_code_operation(file_path, op_type, position, content)
        console.print(f"[yellow]📝 Applied {op_type} operation at position {position}[/yellow]")
        await asyncio.sleep(0.5)

async def demo_live_metrics(client: RealTimeClient):
    """Demonstrate live metrics submission"""
    console.print("\n[bold blue]📊 Live Metrics Demo[/bold blue]")
    
    metrics = [
        ("cpu_usage", 45.2, {"host": "demo-server"}),
        ("memory_usage", 67.8, {"host": "demo-server"}),
        ("response_time", 123.5, {"endpoint": "/api/chat"}),
        ("user_satisfaction", 4.7, {"feature": "collaborative_editing"})
    ]
    
    for metric_type, value, tags in metrics:
        result = await client.submit_metric(metric_type, value, tags)
        console.print(f"[green]📈 Submitted {metric_type}: {value}[/green]")
        await asyncio.sleep(0.5)

async def demo_debugging_session(client: RealTimeClient):
    """Demonstrate debugging session"""
    console.print("\n[bold blue]🐛 Debug Session Demo[/bold blue]")
    
    file_path = "debug_demo.py"
    breakpoints = [5, 10, 15]
    
    # Start debug session
    result = await client.start_debug_session(file_path, breakpoints)
    session_id = result.get("session_id")
    console.print(f"[green]🔍 Started debug session: {session_id}[/green]")
    console.print(f"[yellow]📍 Breakpoints set at lines: {breakpoints}[/yellow]")

async def demo_notifications(client: RealTimeClient):
    """Demonstrate notification system"""
    console.print("\n[bold blue]🔔 Notifications Demo[/bold blue]")
    
    # Register notification handler
    async def handle_notification(data):
        notif_data = data.get("data", {})
        title = notif_data.get("title", "")
        message = notif_data.get("message", "")
        notif_type = notif_data.get("notification_type", "info")
        
        emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(notif_type, "📢")
        console.print(f"[blue]{emoji} {title}:[/blue] {message}")
    
    client.register_handler("notification", handle_notification)
    
    # Create notifications
    notifications = [
        ("info", "Welcome", "Welcome to the real-time demo!"),
        ("success", "Task Complete", "Collaborative editing session started successfully"),
        ("warning", "Performance Alert", "High CPU usage detected on server"),
    ]
    
    for notif_type, title, message in notifications:
        result = await client.create_notification(notif_type, title, message)
        console.print(f"[green]📤 Created {notif_type} notification[/green]")
        await asyncio.sleep(1)

async def demo_feedback_submission(client: RealTimeClient):
    """Demonstrate feedback submission"""
    console.print("\n[bold blue]💬 Feedback Demo[/bold blue]")
    
    feedback_items = [
        ("feature_request", "Please add dark mode support", 5),
        ("bug_report", "Collaborative editing sometimes loses sync", 3),
        ("general", "Love the real-time features! Very responsive.", 5)
    ]
    
    for feedback_type, content, rating in feedback_items:
        result = await client.submit_feedback(feedback_type, content, rating)
        console.print(f"[green]📝 Submitted {feedback_type} feedback (rating: {rating}/5)[/green]")
        await asyncio.sleep(0.5)

async def run_live_stats_display(client: RealTimeClient):
    """Run live statistics display"""
    with Live(console=console, refresh_per_second=1) as live:
        for _ in range(30):  # Run for 30 seconds
            try:
                # Get server stats
                server_stats = await client.get_stats()
                
                # Create stats table
                table = create_stats_table(client.stats, server_stats)
                
                # Update display
                live.update(Panel(
                    table,
                    title="[bold green]Live Statistics[/bold green]",
                    border_style="green"
                ))
                
                await asyncio.sleep(1)
                
            except Exception as e:
                console.print(f"[red]Error updating stats: {e}[/red]")
                break

async def main():
    """Main demo function"""
    console.print(Panel(
        Text("🚀 Elite Coding Assistant - Real-Time Features Demo", justify="center"),
        style="bold blue"
    ))
    
    try:
        async with RealTimeClient(SERVER_URL, WEBSOCKET_URL, TOKEN) as client:
            # Check server health
            health = await client.check_health()
            console.print(f"[green]✅ Server health: {health.get('status', 'unknown')}[/green]")
            
            # Start message listener in background
            listener_task = asyncio.create_task(client.listen_for_messages())
            
            # Run demos
            await demo_chat_messages(client)
            await demo_collaborative_editing(client)
            await demo_live_metrics(client)
            await demo_debugging_session(client)
            await demo_notifications(client)
            await demo_feedback_submission(client)
            
            console.print("\n[bold yellow]📊 Starting live statistics display for 30 seconds...[/bold yellow]")
            console.print("[dim]Press Ctrl+C to stop early[/dim]\n")
            
            # Run live stats display
            try:
                await run_live_stats_display(client)
            except KeyboardInterrupt:
                console.print("\n[yellow]Live stats display stopped by user[/yellow]")
            
            # Cancel listener task
            listener_task.cancel()
            try:
                await listener_task
            except asyncio.CancelledError:
                pass
            
            console.print("\n[bold green]🎉 Demo completed successfully![/bold green]")
            
    except Exception as e:
        console.print(f"\n[red]❌ Demo failed: {e}[/red]")
        console.print("\n[yellow]💡 Make sure the real-time server is running:[/yellow]")
        console.print("   python start_realtime_server.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]")