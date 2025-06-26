#!/usr/bin/env python3
"""
Elite Coding Assistant - Command Line Interface
==============================================

This module provides a command-line interface for interacting with the
elite coding assistant system, including interactive chat, batch processing,
and system management commands.

Author: Manus AI
Version: 1.0
Date: June 23, 2025
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Optional
import logging

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from main.coding_director import CodingDirector
from main.model_manager import ModelManager
from main.config_manager import ConfigManager


class EliteCodingAssistantCLI:
    """Command-line interface for the Elite Coding Assistant."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.director: Optional[CodingDirector] = None
        self.model_manager: Optional[ModelManager] = None
        self.config_manager: Optional[ConfigManager] = None
        self.logger = logging.getLogger(__name__)
    
    def _initialize_components(self):
        """Initialize the assistant components."""
        if not self.config_manager:
            self.config_manager = ConfigManager()
        
        if not self.model_manager:
            self.model_manager = ModelManager()
        
        if not self.director:
            self.director = CodingDirector()
    
    def interactive_mode(self):
        """Start interactive chat mode."""
        print("Elite Coding Assistant - Interactive Mode")
        print("=" * 50)
        print("Type 'exit' to quit, 'help' for commands, 'clear' to clear screen")
        print()
        
        self._initialize_components()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self._show_interactive_help()
                    continue
                
                if user_input.lower() == 'clear':
                    import os
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                if user_input.lower() == 'metrics':
                    self._show_metrics()
                    continue
                
                if user_input.lower() == 'status':
                    self._show_status()
                    continue
                
                # Process the coding request
                print("\nAssistant: ", end="", flush=True)
                start_time = time.time()
                
                response = self.director.get_assistance(user_input)
                
                response_time = time.time() - start_time
                print(response)
                print(f"\n[Response time: {response_time:.2f}s]")
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print()
    
    def _show_interactive_help(self):
        """Show help for interactive mode."""
        help_text = """
Available Commands:
  help     - Show this help message
  exit     - Exit the assistant
  clear    - Clear the screen
  metrics  - Show performance metrics
  status   - Show system status
  
For coding assistance, simply type your question or request.

Examples:
  - Write a Python function to sort a list
  - Explain the quicksort algorithm
  - Create a REST API with Flask
  - Calculate the derivative of x^2 + 3x
"""
        print(help_text)
    
    def _show_metrics(self):
        """Show performance metrics."""
        if self.director:
            metrics = self.director.get_metrics_summary()
            print("\nPerformance Metrics:")
            print("-" * 20)
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"{key}: {value:.2f}")
                else:
                    print(f"{key}: {value}")
            print()
        else:
            print("No metrics available (assistant not initialized)")
    
    def _show_status(self):
        """Show system status."""
        if self.model_manager:
            health = self.model_manager.health_check()
            print(f"\nSystem Status: {health['overall_status'].upper()}")
            print("-" * 20)
            
            print("Models:")
            for model, available in health['model_availability'].items():
                status = "✓" if available else "✗"
                print(f"  {status} {model}")
            
            resources = health['system_resources']
            print(f"\nResources:")
            print(f"  CPU: {resources['cpu_percent']:.1f}%")
            print(f"  Memory: {resources['memory_percent']:.1f}%")
            print(f"  Disk: {resources['disk_usage']:.1f}%")
            
            if health['warnings']:
                print("\nWarnings:")
                for warning in health['warnings']:
                    print(f"  ⚠ {warning}")
            
            if health['errors']:
                print("\nErrors:")
                for error in health['errors']:
                    print(f"  ✗ {error}")
            
            print()
        else:
            print("Status unavailable (model manager not initialized)")
    
    def batch_mode(self, input_file: str, output_file: Optional[str] = None):
        """Process requests from a file."""
        print(f"Processing batch file: {input_file}")
        
        self._initialize_components()
        
        try:
            with open(input_file, 'r') as f:
                requests = [line.strip() for line in f if line.strip()]
            
            results = []
            
            for i, request in enumerate(requests, 1):
                print(f"Processing request {i}/{len(requests)}: {request[:50]}...")
                
                start_time = time.time()
                response = self.director.get_assistance(request)
                response_time = time.time() - start_time
                
                result = {
                    'request': request,
                    'response': response,
                    'response_time': response_time,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(result)
            
            # Save results
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"Results saved to: {output_file}")
            else:
                # Print results to stdout
                for result in results:
                    print(f"\nRequest: {result['request']}")
                    print(f"Response: {result['response']}")
                    print(f"Time: {result['response_time']:.2f}s")
                    print("-" * 50)
            
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found")
        except Exception as e:
            print(f"Error processing batch file: {e}")
    
    def install_models(self, force: bool = False):
        """Install required models."""
        print("Installing required models...")
        
        if not self.model_manager:
            self.model_manager = ModelManager()
        
        results = self.model_manager.install_missing_models(force_reinstall=force)
        
        print("\nInstallation Results:")
        for model, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {model}")
        
        # Run health check after installation
        print("\nRunning health check...")
        health = self.model_manager.health_check()
        print(f"System status: {health['overall_status']}")
    
    def system_report(self, output_file: Optional[str] = None):
        """Generate system report."""
        if not self.model_manager:
            self.model_manager = ModelManager()
        
        report = self.model_manager.generate_report()
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Report saved to: {output_file}")
        else:
            print(report)
    
    def benchmark_models(self, output_file: Optional[str] = None):
        """Benchmark all models."""
        print("Running model benchmarks...")
        
        if not self.model_manager:
            self.model_manager = ModelManager()
        
        results = self.model_manager.benchmark_models()
        
        # Format results
        print("\nBenchmark Results:")
        print("-" * 50)
        
        for model, metrics in results.items():
            print(f"\n{model}:")
            print(f"  Average response time: {metrics['average_time']:.2f}s")
            print(f"  Successful responses: {metrics['successful_responses']}")
            print(f"  Failed responses: {metrics['failed_responses']}")
            
            if metrics['successful_responses'] > 0:
                success_rate = (metrics['successful_responses'] / 
                              (metrics['successful_responses'] + metrics['failed_responses'])) * 100
                print(f"  Success rate: {success_rate:.1f}%")
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nDetailed results saved to: {output_file}")
    
    def config_export(self, output_file: str):
        """Export configuration."""
        if not self.config_manager:
            self.config_manager = ConfigManager()
        
        if self.config_manager.export_configuration(output_file):
            print(f"Configuration exported to: {output_file}")
        else:
            print("Failed to export configuration")
    
    def config_import(self, input_file: str):
        """Import configuration."""
        if not self.config_manager:
            self.config_manager = ConfigManager()
        
        if self.config_manager.import_configuration(input_file):
            print(f"Configuration imported from: {input_file}")
        else:
            print("Failed to import configuration")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Elite Coding Assistant - AI-powered coding assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start interactive mode
  %(prog)s --batch requests.txt     # Process batch file
  %(prog)s --install                # Install required models
  %(prog)s --report                 # Generate system report
  %(prog)s --benchmark              # Benchmark models
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Start interactive chat mode (default)'
    )
    mode_group.add_argument(
        '--batch', '-b',
        metavar='INPUT_FILE',
        help='Process requests from file'
    )
    mode_group.add_argument(
        '--install',
        action='store_true',
        help='Install required models'
    )
    mode_group.add_argument(
        '--report',
        action='store_true',
        help='Generate system report'
    )
    mode_group.add_argument(
        '--benchmark',
        action='store_true',
        help='Benchmark all models'
    )
    mode_group.add_argument(
        '--config-export',
        metavar='OUTPUT_FILE',
        help='Export configuration to file'
    )
    mode_group.add_argument(
        '--config-import',
        metavar='INPUT_FILE',
        help='Import configuration from file'
    )
    
    # Options
    parser.add_argument(
        '--output', '-o',
        metavar='OUTPUT_FILE',
        help='Output file for results'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reinstall of models'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-essential output'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    if args.quiet:
        log_level = logging.WARNING
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize CLI
    cli = EliteCodingAssistantCLI()
    
    try:
        # Execute based on arguments
        if args.batch:
            cli.batch_mode(args.batch, args.output)
        elif args.install:
            cli.install_models(args.force)
        elif args.report:
            cli.system_report(args.output)
        elif args.benchmark:
            cli.benchmark_models(args.output)
        elif args.config_export:
            cli.config_export(args.config_export)
        elif args.config_import:
            cli.config_import(args.config_import)
        else:
            # Default to interactive mode
            cli.interactive_mode()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

