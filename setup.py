#!/usr/bin/env python3
"""
Sales Analysis Project Setup Script
Initializes the project environment and installs dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ Error in {description}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception in {description}: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False

def install_requirements():
    """Install required packages"""
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        return run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                          "Installing Python packages")
    else:
        print("❌ requirements.txt not found")
        return False

def create_directories():
    """Ensure all necessary directories exist"""
    directories = [
        "data",
        "sql", 
        "notebooks",
        "visualizations",
        "reports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Directory '{directory}' ready")
    
    return True

def download_instructions():
    """Display instructions for downloading the dataset"""
    print("\n" + "="*60)
    print("📊 DATASET DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print("\nTo complete the setup, you need to download the Walmart dataset:")
    print("\n1. Visit: https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting/data")
    print("2. Sign in to Kaggle (free account required)")
    print("3. Download the following files:")
    print("   - train.csv")
    print("   - test.csv")
    print("   - features.csv")
    print("   - stores.csv")
    print("4. Place all CSV files in the 'data/' directory")
    print("\nAlternatively, if you have Kaggle API configured:")
    print("   kaggle competitions download -c walmart-recruiting-store-sales-forecasting")
    print("\nOnce downloaded, run: python data_loader.py")

def main():
    """Main setup function"""
    print("🚀 Walmart Sales Analysis Project Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        print("\n⚠️  Package installation failed. You may need to install manually.")
        print("   Run: pip install -r requirements.txt")
    
    # Show dataset instructions
    download_instructions()
    
    print("\n" + "="*60)
    print("✅ PROJECT SETUP COMPLETED!")
    print("="*60)
    print("\nNext steps:")
    print("1. Download the dataset files (see instructions above)")
    print("2. Run: python data_loader.py")
    print("3. Open: notebooks/walmart_analysis.ipynb")
    print("4. Execute the SQL queries in sql/ directory")
    print("\nHappy analyzing! 📈")

if __name__ == "__main__":
    main()
