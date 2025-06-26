#!/usr/bin/env python3
"""
Elite Coding Assistant - Real-Time Features Deployment Script

This script provides comprehensive deployment and management capabilities
for the real-time features infrastructure including:
- Docker container orchestration
- Health monitoring
- Configuration validation
- Service management
- Performance testing

Usage:
    python deploy_realtime.py [command] [options]
    
Commands:
    deploy      - Deploy all services
    start       - Start existing services
    stop        - Stop all services
    restart     - Restart all services
    status      - Check service status
    logs        - View service logs
    test        - Run integration tests
    cleanup     - Clean up resources
    monitor     - Start monitoring dashboard
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import click
import docker
import requests
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

# Initialize Rich console for beautiful output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealTimeDeployer:
    """Manages deployment and operations of real-time features."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docker_dir = project_root / "docker"
        self.docker_client = docker.from_env()
        self.compose_file = self.docker_dir / "docker-compose.realtime.yml"
        
        # Service configuration
        self.services = {
            "redis": {"port": 6379, "health_endpoint": None},
            "realtime-server": {"port": 8001, "health_endpoint": "/health"},
            "nginx": {"port": 80, "health_endpoint": "/nginx-health"},
            "prometheus": {"port": 9090, "health_endpoint": "/-/healthy"},
            "grafana": {"port": 3000, "health_endpoint": "/api/health"},
            "redis-commander": {"port": 8081, "health_endpoint": "/"},
        }
    
    def validate_environment(self) -> bool:
        """Validate deployment environment and prerequisites."""
        console.print("[bold blue]Validating deployment environment...[/bold blue]")
        
        checks = [
            ("Docker daemon", self._check_docker),
            ("Docker Compose", self._check_docker_compose),
            ("Required files", self._check_required_files),
            ("Port availability", self._check_ports),
            ("System resources", self._check_system_resources),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅ PASS" if result else "❌ FAIL"
                console.print(f"  {check_name}: {status}")
                if not result:
                    all_passed = False
            except Exception as e:
                console.print(f"  {check_name}: ❌ ERROR - {e}")
                all_passed = False
        
        return all_passed
    
    def _check_docker(self) -> bool:
        """Check if Docker daemon is running."""
        try:
            self.docker_client.ping()
            return True
        except Exception:
            return False
    
    def _check_docker_compose(self) -> bool:
        """Check if Docker Compose is available."""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_required_files(self) -> bool:
        """Check if all required configuration files exist."""
        required_files = [
            self.compose_file,
            self.docker_dir / "Dockerfile.realtime",
            self.docker_dir / "redis.conf",
            self.docker_dir / "nginx.conf",
            self.docker_dir / "prometheus.yml",
            self.project_root / "requirements_realtime.txt",
        ]
        
        return all(file.exists() for file in required_files)
    
    def _check_ports(self) -> bool:
        """Check if required ports are available."""
        import socket
        
        ports_to_check = [6379, 8001, 80, 9090, 3000, 8081]
        
        for port in ports_to_check:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('localhost', port))
                if result == 0:  # Port is in use
                    console.print(f"    Port {port} is already in use")
                    return False
        
        return True
    
    def _check_system_resources(self) -> bool:
        """Check if system has sufficient resources."""
        import psutil
        
        # Check available memory (minimum 2GB)
        available_memory = psutil.virtual_memory().available / (1024**3)
        if available_memory < 2:
            console.print(f"    Insufficient memory: {available_memory:.1f}GB available, 2GB required")
            return False
        
        # Check available disk space (minimum 5GB)
        available_disk = psutil.disk_usage('/').free / (1024**3)
        if available_disk < 5:
            console.print(f"    Insufficient disk space: {available_disk:.1f}GB available, 5GB required")
            return False
        
        return True
    
    def deploy(self, rebuild: bool = False) -> bool:
        """Deploy all real-time services."""
        console.print("[bold green]Deploying Elite Coding Assistant Real-Time Features[/bold green]")
        
        if not self.validate_environment():
            console.print("[bold red]Environment validation failed. Please fix issues before deploying.[/bold red]")
            return False
        
        try:
            # Build and start services
            cmd = ["docker-compose", "-f", str(self.compose_file), "up", "-d"]
            if rebuild:
                cmd.append("--build")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Deploying services...", total=None)
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    console.print(f"[bold red]Deployment failed:[/bold red]\n{result.stderr}")
                    return False
            
            # Wait for services to be healthy
            self._wait_for_services()
            
            # Display deployment summary
            self._display_deployment_summary()
            
            console.print("[bold green]✅ Deployment completed successfully![/bold green]")
            return True
            
        except Exception as e:
            console.print(f"[bold red]Deployment error: {e}[/bold red]")
            return False
    
    def _wait_for_services(self, timeout: int = 120) -> None:
        """Wait for all services to become healthy."""
        console.print("[bold blue]Waiting for services to become healthy...[/bold blue]")
        
        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for service_name, config in self.services.items():
                task = progress.add_task(f"Checking {service_name}...", total=None)
                
                while time.time() - start_time < timeout:
                    if self._check_service_health(service_name, config):
                        progress.update(task, description=f"✅ {service_name} healthy")
                        break
                    time.sleep(2)
                else:
                    progress.update(task, description=f"⚠️ {service_name} timeout")
    
    def _check_service_health(self, service_name: str, config: Dict) -> bool:
        """Check if a specific service is healthy."""
        try:
            if config["health_endpoint"]:
                response = requests.get(
                    f"http://localhost:{config['port']}{config['health_endpoint']}",
                    timeout=5
                )
                return response.status_code == 200
            else:
                # For services without health endpoints (like Redis)
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(5)
                    result = sock.connect_ex(('localhost', config['port']))
                    return result == 0
        except Exception:
            return False
    
    def _display_deployment_summary(self) -> None:
        """Display deployment summary with service URLs."""
        table = Table(title="Service Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("URL", style="blue")
        table.add_column("Description")
        
        service_info = [
            ("Real-Time API", "http://localhost:8001", "Main API server with WebSocket support"),
            ("WebSocket", "ws://localhost:8001/ws", "Real-time communication endpoint"),
            ("Nginx Proxy", "http://localhost:80", "Load balancer and reverse proxy"),
            ("Grafana", "http://localhost:3000", "Monitoring dashboard (admin/admin)"),
            ("Prometheus", "http://localhost:9090", "Metrics collection and alerting"),
            ("Redis Commander", "http://localhost:8081", "Redis database management"),
        ]
        
        for service, url, description in service_info:
            status = "🟢 Running" if self._check_service_health(
                service.lower().replace(" ", "-").replace("real-time-api", "realtime-server"),
                self.services.get(service.lower().replace(" ", "-").replace("real-time-api", "realtime-server"), {"port": 8001, "health_endpoint": "/health"})
            ) else "🔴 Down"
            
            table.add_row(service, status, url, description)
        
        console.print(table)
        
        # Display quick start commands
        panel_content = Text()
        panel_content.append("Quick Start Commands:\n\n", style="bold")
        panel_content.append("• Test WebSocket: ", style="cyan")
        panel_content.append("python examples/realtime_client_example.py\n")
        panel_content.append("• View logs: ", style="cyan")
        panel_content.append("python deploy_realtime.py logs\n")
        panel_content.append("• Run tests: ", style="cyan")
        panel_content.append("python deploy_realtime.py test\n")
        panel_content.append("• Monitor services: ", style="cyan")
        panel_content.append("python deploy_realtime.py monitor\n")
        
        console.print(Panel(panel_content, title="Next Steps", border_style="green"))
    
    def stop(self) -> bool:
        """Stop all services."""
        console.print("[bold yellow]Stopping real-time services...[/bold yellow]")
        
        try:
            result = subprocess.run(
                ["docker-compose", "-f", str(self.compose_file), "down"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("[bold green]✅ Services stopped successfully[/bold green]")
                return True
            else:
                console.print(f"[bold red]Failed to stop services:[/bold red]\n{result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"[bold red]Error stopping services: {e}[/bold red]")
            return False
    
    def restart(self) -> bool:
        """Restart all services."""
        console.print("[bold blue]Restarting real-time services...[/bold blue]")
        return self.stop() and self.deploy()
    
    def status(self) -> None:
        """Display current status of all services."""
        console.print("[bold blue]Real-Time Services Status[/bold blue]")
        
        table = Table()
        table.add_column("Service", style="cyan")
        table.add_column("Container", style="blue")
        table.add_column("Status", style="green")
        table.add_column("Health", style="yellow")
        table.add_column("Uptime")
        
        try:
            containers = self.docker_client.containers.list(all=True)
            
            for service_name in self.services.keys():
                container = next(
                    (c for c in containers if service_name in c.name),
                    None
                )
                
                if container:
                    status = container.status
                    health = "🟢 Healthy" if self._check_service_health(
                        service_name, self.services[service_name]
                    ) else "🔴 Unhealthy"
                    
                    # Calculate uptime
                    created = container.attrs['Created']
                    uptime = "N/A"  # Simplified for this example
                    
                    table.add_row(
                        service_name,
                        container.name,
                        status,
                        health,
                        uptime
                    )
                else:
                    table.add_row(
                        service_name,
                        "Not found",
                        "🔴 Down",
                        "🔴 Unhealthy",
                        "N/A"
                    )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[bold red]Error getting status: {e}[/bold red]")
    
    def logs(self, service: Optional[str] = None, follow: bool = False) -> None:
        """Display service logs."""
        cmd = ["docker-compose", "-f", str(self.compose_file), "logs"]
        
        if follow:
            cmd.append("-f")
        
        if service:
            cmd.append(service)
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            console.print("\n[yellow]Log viewing interrupted[/yellow]")
    
    def cleanup(self, volumes: bool = False) -> bool:
        """Clean up deployment resources."""
        console.print("[bold yellow]Cleaning up real-time deployment...[/bold yellow]")
        
        try:
            cmd = ["docker-compose", "-f", str(self.compose_file), "down"]
            if volumes:
                cmd.extend(["--volumes", "--remove-orphans"])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("[bold green]✅ Cleanup completed[/bold green]")
                return True
            else:
                console.print(f"[bold red]Cleanup failed:[/bold red]\n{result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"[bold red]Cleanup error: {e}[/bold red]")
            return False


# CLI Commands
@click.group()
@click.option('--project-root', default='.', help='Project root directory')
@click.pass_context
def cli(ctx, project_root):
    """Elite Coding Assistant Real-Time Features Deployment Tool"""
    ctx.ensure_object(dict)
    ctx.obj['deployer'] = RealTimeDeployer(Path(project_root).resolve())


@cli.command()
@click.option('--rebuild', is_flag=True, help='Rebuild Docker images')
@click.pass_context
def deploy(ctx, rebuild):
    """Deploy all real-time services"""
    success = ctx.obj['deployer'].deploy(rebuild=rebuild)
    sys.exit(0 if success else 1)


@cli.command()
@click.pass_context
def start(ctx):
    """Start existing services"""
    success = ctx.obj['deployer'].deploy(rebuild=False)
    sys.exit(0 if success else 1)


@cli.command()
@click.pass_context
def stop(ctx):
    """Stop all services"""
    success = ctx.obj['deployer'].stop()
    sys.exit(0 if success else 1)


@cli.command()
@click.pass_context
def restart(ctx):
    """Restart all services"""
    success = ctx.obj['deployer'].restart()
    sys.exit(0 if success else 1)


@cli.command()
@click.pass_context
def status(ctx):
    """Check service status"""
    ctx.obj['deployer'].status()


@cli.command()
@click.option('--service', help='Specific service to show logs for')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.pass_context
def logs(ctx, service, follow):
    """View service logs"""
    ctx.obj['deployer'].logs(service=service, follow=follow)


@cli.command()
@click.option('--volumes', is_flag=True, help='Also remove volumes')
@click.pass_context
def cleanup(ctx, volumes):
    """Clean up deployment resources"""
    success = ctx.obj['deployer'].cleanup(volumes=volumes)
    sys.exit(0 if success else 1)


@cli.command()
@click.pass_context
def test(ctx):
    """Run integration tests"""
    console.print("[bold blue]Running integration tests...[/bold blue]")
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/test_realtime_features.py", "-v"],
            cwd=ctx.obj['deployer'].project_root
        )
        sys.exit(result.returncode)
    except Exception as e:
        console.print(f"[bold red]Test execution failed: {e}[/bold red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def monitor(ctx):
    """Open monitoring dashboard"""
    import webbrowser
    
    console.print("[bold blue]Opening monitoring dashboard...[/bold blue]")
    
    urls = [
        ("Grafana Dashboard", "http://localhost:3000"),
        ("Prometheus Metrics", "http://localhost:9090"),
        ("API Documentation", "http://localhost:8001/docs"),
    ]
    
    for name, url in urls:
        console.print(f"Opening {name}: {url}")
        webbrowser.open(url)
    
    console.print("[bold green]✅ Monitoring dashboards opened in browser[/bold green]")


if __name__ == '__main__':
    cli()