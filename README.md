# Amazon Price Monitor

A Python application that monitors Amazon product prices and alerts you when prices drop to your target price.

## Features
- Monitor multiple Amazon products simultaneously
- Set target prices in euros (€)
- User-friendly GUI interface with dark mode
- Real-time price checking
- Automatic alerts when prices reach your target

## Download and Installation

### Option 1: Run from Source Code
1. Download these files:
   - `gui.py`
   - `price_monitor.py`
   - `amazon_checkout.py`
   - `config.py`
   - `generated-icon.svg`

2. Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)

3. Install required packages by opening a terminal/command prompt and running:
```bash
pip install beautifulsoup4 requests trafilatura selenium webdriver-manager
```

4. Run the program:
```bash
python gui.py
```

### Option 2: Download Executable (Windows only)
1. Download `AmazonPriceMonitor.exe` from the releases
2. Double-click the executable to run
3. No Python installation needed

## Usage
1. Enter the Amazon product URL
2. Set your target price in euros (€)
3. Click "Add Product" to start monitoring
4. Use "Start Monitoring" to begin price checks
5. Use "Stop Monitoring" to pause price checks
6. Use "Clear Products" to remove all monitored products
7. Toggle dark/light mode using the theme button

## Notes
- The program checks prices at regular intervals
- Price alerts will be shown in the monitoring log
- Make sure to use valid Amazon product URLs
- Prices are monitored in euros (€)

## Troubleshooting
- If the program fails to start, ensure all required packages are installed
- Make sure you're using a valid Amazon product URL
- Check your internet connection if price checks fail