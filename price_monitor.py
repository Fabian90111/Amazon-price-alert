import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import sys
import logging

# Set up logging with more detailed configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('price_alerts.log')
    ]
)
logger = logging.getLogger(__name__)

class AmazonPriceMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
        self.products = []  # Will be set by GUI
        self.stop_monitoring = False  # Flag to stop monitoring

    def setup_headers(self):
        """Setup headers to better mimic a real browser request"""
        self.session.headers.update({
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
        })

    def extract_price(self, html_content):
        """Extract price from Amazon product page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        logger.debug("Attempting to extract price from page...")

        # Try multiple price selectors that Amazon commonly uses
        price_selectors = [
            '.a-price .a-offscreen',
            '#priceblock_ourprice',
            '#priceblock_dealprice',
            '.a-price .a-price-whole',
            '#corePrice_feature_div .a-price-whole',
            '#price_inside_buybox',
            '.a-size-medium.a-color-price',
            '.price3P',
            '#sns-base-price'
        ]

        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text().strip()
                logger.debug(f"Found price element with selector '{selector}': {price_text}")
                # Extract number from price text (e.g., "€299.99" or "299,99 €" -> 299.99)
                price_text = price_text.replace(',', '.')  # Convert European decimal separator
                price_match = re.search(r'\d+[.,]?\d*', price_text)
                if price_match:
                    try:
                        return float(price_match.group())
                    except ValueError as e:
                        logger.debug(f"Failed to convert price text '{price_text}' to float: {e}")
                        continue

        logger.debug("Standard price selectors failed, attempting trafilatura extraction...")
        # If we couldn't find the price with any selector, try using trafilatura
        try:
            import trafilatura
            downloaded = trafilatura.fetch_url(self.products[0]['url'])
            text = trafilatura.extract(downloaded)
            if text:
                # Look for price patterns in the extracted text (both € and EUR formats)
                price_pattern = r'(?:€\s*(\d+(?:[.,]\d{2})?)|(\d+(?:[.,]\d{2})?)\s*€)'
                matches = re.findall(price_pattern, text)
                if matches:
                    # Take the first non-empty group from the matches
                    price_str = next(p for match in matches for p in match if p)
                    logger.debug(f"Found price using trafilatura: €{price_str}")
                    return float(price_str.replace(',', '.'))
        except Exception as e:
            logger.debug(f"Trafilatura extraction failed: {e}")

        raise ValueError("Could not find price element on the page after trying multiple methods")

    def check_stock(self, html_content):
        """Check if the product is in stock"""
        soup = BeautifulSoup(html_content, 'html.parser')
        logger.debug("Checking stock status...")

        # Multiple stock status selectors
        stock_selectors = [
            '#availability',
            '#outOfStock',
            '#availability-string',
            '#buybox-availability'
        ]

        for selector in stock_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip().lower()
                logger.debug(f"Found stock information with selector '{selector}': {text}")
                if 'in stock' in text:
                    return True
                if any(phrase in text for phrase in ['out of stock', 'currently unavailable', 'not available']):
                    return False

        # Check "Add to Cart" button presence as fallback
        add_to_cart = soup.select_one('#add-to-cart-button')
        is_in_stock = add_to_cart is not None
        logger.debug(f"Stock status determined by 'Add to Cart' button presence: {is_in_stock}")
        return is_in_stock

    def send_alert(self, title, message):
        """Send alert through logging"""
        alert_message = f"\n{'='*50}\n{title}\n{message}\n{'='*50}"
        logger.info(alert_message)

    def check_price(self, product):
        """Check price for a single product"""
        retry_count = 0
        max_retries = 3
        retry_delay = 5  # seconds

        while retry_count < max_retries and not self.stop_monitoring:
            try:
                response = self.session.get(product['url'], timeout=10)
                response.raise_for_status()

                if response.status_code == 200:
                    current_price = self.extract_price(response.text)
                    in_stock = self.check_stock(response.text)

                    logger.info(f"Current price: €{current_price:.2f}, Target: €{product['target_price']:.2f}")

                    if in_stock and current_price <= product['target_price']:
                        self.send_alert(
                            "Price Alert!",
                            f"Product is available at €{current_price:.2f}\nTarget price: €{product['target_price']:.2f}\nURL: {product['url']}"
                        )
                        return True
                    break  # Success, exit retry loop

            except requests.exceptions.RequestException as e:
                logger.error(f"Network error (attempt {retry_count + 1}/{max_retries}): {e}")
                if retry_count + 1 < max_retries:
                    time.sleep(retry_delay)
            except ValueError as e:
                logger.error(f"Parsing error: {e}")
                break  # Don't retry parsing errors
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break

            retry_count += 1

        return False

    def monitor_prices(self):
        """Main monitoring loop"""
        logger.info("Starting Amazon Price Monitor...")
        logger.info(f"Monitoring {len(self.products)} products")

        check_interval = 60  # seconds between checks

        while not self.stop_monitoring:
            logger.info(f"\nChecking prices at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            for product in self.products:
                if self.stop_monitoring:
                    break
                try:
                    self.check_price(product)
                except Exception as e:
                    logger.error(f"Error checking product {product['url']}: {e}")

            if not self.stop_monitoring:
                logger.info(f"Waiting {check_interval} seconds before next check...")
                time.sleep(check_interval)

        logger.info("Price monitoring stopped")

if __name__ == "__main__":
    try:
        monitor = AmazonPriceMonitor()
        monitor.monitor_prices()
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)