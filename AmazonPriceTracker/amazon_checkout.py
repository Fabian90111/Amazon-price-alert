import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

class AmazonCheckout:
    def __init__(self, email=None, password=None):
        """Initialize the AmazonCheckout class with optional credentials"""
        self.email = email
        self.password = password
        self.setup_driver()

    def setup_driver(self):
        """Set up Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        """Login to Amazon account"""
        try:
            self.driver.get('https://www.amazon.com/signin')
            
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, 'ap_email'))
            )
            email_field.send_keys(self.email)
            self.driver.find_element(By.ID, 'continue').click()
            
            # Enter password
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, 'ap_password'))
            )
            password_field.send_keys(self.password)
            self.driver.find_element(By.ID, 'signInSubmit').click()
            
            logger.info("Successfully logged in to Amazon")
            return True
        except Exception as e:
            logger.error(f"Failed to login: {str(e)}")
            return False

    def add_to_cart(self, product_url):
        """Add product to cart"""
        try:
            self.driver.get(product_url)
            add_to_cart_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'add-to-cart-button'))
            )
            add_to_cart_button.click()
            logger.info("Successfully added item to cart")
            return True
        except Exception as e:
            logger.error(f"Failed to add item to cart: {str(e)}")
            return False

    def proceed_to_checkout(self):
        """Proceed to checkout"""
        try:
            # Go to cart
            self.driver.get('https://www.amazon.com/gp/cart/view.html')
            
            # Click proceed to checkout
            checkout_button = self.wait.until(
                EC.element_to_be_clickable((By.NAME, 'proceedToRetailCheckout'))
            )
            checkout_button.click()
            
            # Wait for shipping address page
            self.wait.until(
                EC.presence_of_element_located((By.ID, 'shipToThisAddressButton'))
            )
            
            logger.info("Successfully proceeded to checkout")
            return True
        except Exception as e:
            logger.error(f"Failed to proceed to checkout: {str(e)}")
            return False

    def place_order(self):
        """Complete the checkout process"""
        try:
            # Select shipping address (assuming default)
            ship_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'shipToThisAddressButton'))
            )
            ship_button.click()
            
            # Wait for payment method page and select default
            self.wait.until(
                EC.presence_of_element_located((By.ID, 'pp-xQoqkn-84'))
            )
            
            # Place the order
            place_order_button = self.wait.until(
                EC.element_to_be_clickable((By.NAME, 'placeYourOrder1'))
            )
            place_order_button.click()
            
            logger.info("Successfully placed order")
            return True
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            return False

    def auto_checkout(self, product_url):
        """Perform complete checkout process"""
        if not self.email or not self.password:
            logger.error("Amazon credentials not provided")
            return False
            
        try:
            if not self.login():
                return False
                
            if not self.add_to_cart(product_url):
                return False
                
            if not self.proceed_to_checkout():
                return False
                
            if not self.place_order():
                return False
                
            logger.info("Auto-checkout completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Auto-checkout failed: {str(e)}")
            return False
        finally:
            self.driver.quit()
