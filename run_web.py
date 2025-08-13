#!/usr/bin/env python3
"""
Walmart Sales Analysis - Web Application Launcher
Simple script to launch the Streamlit web application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_streamlit():
    """Install Streamlit if not available"""
    print("📦 Installing Streamlit...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "plotly"], check=True)
        print("✅ Streamlit installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Streamlit")
        return False

def main():
    """Main function to launch the web application"""
    print("🚀 Walmart Sales Analysis - Web Application")
    print("=" * 50)
    
    # Check if Streamlit is installed
    if not check_streamlit():
        print("⚠️ Streamlit not found. Installing...")
        if not install_streamlit():
            print("❌ Cannot proceed without Streamlit")
            sys.exit(1)
    
    # Check if app.py exists
    app_path = Path("app.py")
    if not app_path.exists():
        print("❌ app.py not found in current directory")
        sys.exit(1)
    
    print("🌐 Starting web application...")
    print("📊 Dashboard will open in your default browser")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Tips:")
    print("   - Use the sidebar to navigate between sections")
    print("   - Upload your CSV files in the 'Data Upload' section")
    print("   - Try the SQL Query Interface for custom analysis")
    print("   - Press Ctrl+C to stop the server")
    print("\n" + "=" * 50)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    main()
