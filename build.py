import PyInstaller.__main__
import sys
import os

# Configure PyInstaller to create a single executable
PyInstaller.__main__.run([
    'gui.py',  # Main script
    '--onefile',  # Create a single executable
    '--windowed',  # Don't show console window
    '--name=AmazonPriceMonitor',  # Name of the executable
    '--add-data=price_monitor.py:.',  # Include price_monitor.py
    '--add-data=generated-icon.svg:.',  # Include the icon
    '--icon=generated-icon.svg',  # Set application icon
    '--clean',  # Clean PyInstaller cache
    '--hidden-import=tkinter',
    '--hidden-import=requests',
    '--hidden-import=bs4',
    '--hidden-import=trafilatura',
])