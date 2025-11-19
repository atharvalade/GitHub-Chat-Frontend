#!/usr/bin/env python3
"""
Test runner script for the Backend LLM module

Usage:
    python test_runner.py                    # Run all tests
    python test_runner.py --unit            # Run unit tests only  
    python test_runner.py --coverage        # Run with coverage
    python test_runner.py --verbose         # Verbose output
    python test_runner.py --help           # Show help
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add the src directory to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))


def install_test_dependencies():
    """Install required testing dependencies"""
    print("📦 Installing test dependencies...")
    dependencies = [
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0", 
        "pytest-cov>=4.1.0",
        "google-generativeai>=0.3.0"
    ]
    
    try:
        for dep in dependencies:
            print(f"  Installing {dep}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], check=True, capture_output=True)
        
        print("✅ Test dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def run_tests(test_args=None):
    """Run the test suite"""
    if test_args is None:
        test_args = []
    
    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test directory
    cmd.append("tests/test_llm.py")
    
    # Add any additional arguments
    cmd.extend(test_args)
    
    print(f"🧪 Running tests: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=backend_dir)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ pytest not found. Installing dependencies...")
        if install_test_dependencies():
            return run_tests(test_args)
        return False


def main():
    parser = argparse.ArgumentParser(description="LLM Module Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--install", action="store_true", help="Install dependencies only")
    parser.add_argument("--quick", action="store_true", help="Quick test run (less verbose)")
    
    args = parser.parse_args()
    
    print("🚀 LLM Module Test Runner")
    print("=" * 40)
    
    # Handle install-only mode
    if args.install:
        success = install_test_dependencies()
        return 0 if success else 1
    
    # Build pytest arguments
    test_args = []
    
    if args.verbose:
        test_args.extend(["-v", "--tb=long"])
    elif args.quick:
        test_args.extend(["-q"])
    else:
        test_args.extend(["-v"])
    
    if args.unit:
        test_args.extend(["-m", "unit"])
    
    if args.coverage:
        test_args.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    
    # Add some useful defaults
    test_args.extend([
        "--color=yes",
        "--tb=short"
    ])
    
    # Run the tests
    success = run_tests(test_args)
    
    if success:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        print("💡 Try running with --verbose for more details")
    
    return 0 if success else 1


def quick_test():
    """Quick test function for basic validation"""
    print("🔍 Quick validation test...")
    
    try:
        # Test imports
        from utils.llm import KeyManager, generate_response
        print("✅ Imports successful")
        
        # Test environment setup
        os.environ['GEMINI_API_KEY'] = 'test-key'
        manager = KeyManager()
        print("✅ KeyManager initialization successful")
        
        # Test basic functionality
        assert manager.get_current_key() == 'test-key'
        print("✅ Basic functionality working")
        
        print("🎉 Quick validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Quick validation failed: {e}")
        return False
    finally:
        # Cleanup
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            # No arguments - run quick test first
            if not quick_test():
                print("\n⚠️  Quick test failed. Running full test suite...")
            
        exit_code = main()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n👋 Tests cancelled by user")
        sys.exit(130)  # Standard exit code for SIGINT