#!/usr/bin/env python3
"""
Elite Coding Assistant - Usage Examples
======================================

This script demonstrates various ways to use the Elite Coding Assistant
for different coding tasks and scenarios.

Author: Manus AI
Version: 1.0
Date: June 23, 2025
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main.coding_director import CodingDirector
import time


def example_basic_usage():
    """Demonstrate basic usage of the coding assistant."""
    print("Example 1: Basic Usage")
    print("=" * 30)
    
    # Initialize the director
    director = CodingDirector()
    
    # Simple coding request
    prompt = "Write a Python function to calculate the factorial of a number"
    print(f"Request: {prompt}")
    print("\nResponse:")
    
    response = director.get_assistance(prompt)
    print(response)
    print("\n" + "=" * 50 + "\n")


def example_mathematical_tasks():
    """Demonstrate mathematical and algorithmic tasks."""
    print("Example 2: Mathematical Tasks")
    print("=" * 30)
    
    director = CodingDirector()
    
    math_prompts = [
        "Calculate the derivative of f(x) = x^3 + 2x^2 - 5x + 1",
        "Implement the quicksort algorithm and analyze its time complexity",
        "Write a function to find the greatest common divisor using Euclidean algorithm"
    ]
    
    for prompt in math_prompts:
        print(f"Request: {prompt}")
        print("Response:")
        
        start_time = time.time()
        response = director.get_assistance(prompt)
        response_time = time.time() - start_time
        
        # Show first 200 characters of response
        print(response[:200] + "..." if len(response) > 200 else response)
        print(f"[Response time: {response_time:.2f}s]")
        print("-" * 40)
    
    print("=" * 50 + "\n")


def example_web_development():
    """Demonstrate web development tasks."""
    print("Example 3: Web Development")
    print("=" * 30)
    
    director = CodingDirector()
    
    web_prompts = [
        "Create a Flask REST API endpoint for user registration",
        "Write a JavaScript function to validate email addresses",
        "Design a responsive CSS layout for a blog homepage"
    ]
    
    for prompt in web_prompts:
        print(f"Request: {prompt}")
        print("Response:")
        
        response = director.get_assistance(prompt)
        print(response[:300] + "..." if len(response) > 300 else response)
        print("-" * 40)
    
    print("=" * 50 + "\n")


def example_complex_architecture():
    """Demonstrate complex architectural tasks."""
    print("Example 4: Complex Architecture")
    print("=" * 30)
    
    director = CodingDirector()
    
    complex_prompt = """
    Design a microservices architecture for an e-commerce platform with the following requirements:
    - User authentication and authorization
    - Product catalog management
    - Shopping cart functionality
    - Order processing and payment
    - Inventory management
    - Notification system
    
    Include service boundaries, communication patterns, and data storage considerations.
    """
    
    print("Request: Complex e-commerce microservices architecture")
    print("Response:")
    
    start_time = time.time()
    response = director.get_assistance(complex_prompt)
    response_time = time.time() - start_time
    
    print(response)
    print(f"\n[Response time: {response_time:.2f}s]")
    print("=" * 50 + "\n")


def example_code_review():
    """Demonstrate code review and optimization."""
    print("Example 5: Code Review and Optimization")
    print("=" * 30)
    
    director = CodingDirector()
    
    code_to_review = '''
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates
'''
    
    prompt = f"""
    Review this Python code and suggest optimizations:
    
    {code_to_review}
    
    Please provide:
    1. Analysis of current time complexity
    2. Potential issues or bugs
    3. Optimized version with better performance
    4. Explanation of improvements
    """
    
    print("Request: Code review and optimization")
    print("Response:")
    
    response = director.get_assistance(prompt)
    print(response)
    print("=" * 50 + "\n")


def example_debugging_help():
    """Demonstrate debugging assistance."""
    print("Example 6: Debugging Help")
    print("=" * 30)
    
    director = CodingDirector()
    
    buggy_code = '''
def binary_search(arr, target):
    left = 0
    right = len(arr)
    
    while left < right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid
        else:
            right = mid
    
    return -1

# Test
arr = [1, 3, 5, 7, 9, 11, 13]
print(binary_search(arr, 7))  # Should return 3, but causes infinite loop
'''
    
    prompt = f"""
    This binary search implementation has a bug that causes an infinite loop. 
    Can you identify the issue and provide a corrected version?
    
    {buggy_code}
    """
    
    print("Request: Debug binary search infinite loop")
    print("Response:")
    
    response = director.get_assistance(prompt)
    print(response)
    print("=" * 50 + "\n")


def example_performance_metrics():
    """Show performance metrics after running examples."""
    print("Example 7: Performance Metrics")
    print("=" * 30)
    
    director = CodingDirector()
    
    # Run a few quick requests to generate metrics
    test_prompts = [
        "Write a hello world function",
        "Calculate 10 factorial",
        "Explain bubble sort"
    ]
    
    for prompt in test_prompts:
        director.get_assistance(prompt)
    
    # Show metrics
    metrics = director.get_metrics_summary()
    print("Performance Summary:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        elif isinstance(value, list):
            print(f"  {key}: {', '.join(value)}")
        else:
            print(f"  {key}: {value}")
    
    print("=" * 50 + "\n")


def main():
    """Run all examples."""
    print("Elite Coding Assistant - Usage Examples")
    print("=" * 50)
    print("This script demonstrates various capabilities of the Elite Coding Assistant")
    print("=" * 50)
    print()
    
    try:
        example_basic_usage()
        example_mathematical_tasks()
        example_web_development()
        example_complex_architecture()
        example_code_review()
        example_debugging_help()
        example_performance_metrics()
        
        print("All examples completed successfully!")
        print("\nTo run the assistant interactively:")
        print("  python src/cli.py --interactive")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("\nMake sure you have:")
        print("1. Installed all required models")
        print("2. Started the Ollama service")
        print("3. Installed Python dependencies")
        print("\nRun the setup script if you haven't already:")
        print("  ./scripts/setup.sh")


if __name__ == "__main__":
    main()

