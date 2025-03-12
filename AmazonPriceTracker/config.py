# Configuration settings for the Amazon Price Monitor

# Product URLs and their target prices
PRODUCTS = [
    {
        "url": "https://www.amazon.com/dp/B07ZPKBL9V",  # Updated to valid product URL - Amazon Echo Dot
        "target_price": 29.99,
        "auto_checkout": True  # Enable/disable automatic checkout for this product
    }
]

# Headers to better mimic a real browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

# Delay between checks (in seconds)
CHECK_INTERVAL = 60  # Consider increasing this to avoid rate limiting

# Max retries for failed requests
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Notification settings
NOTIFICATION_DURATION = 10  # seconds

# Checkout settings
CHECKOUT_SETTINGS = {
    "shipping_speed": "FREE",  # Options: FREE, EXPEDITED, NEXT_DAY
    "payment_method": "default",  # Use default payment method
    "shipping_address": "default"  # Use default shipping address
}