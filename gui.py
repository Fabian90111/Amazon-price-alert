import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from price_monitor import AmazonPriceMonitor
import logging
import queue
import json
import os

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

class AmazonMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Price Monitor")
        self.root.geometry("800x600")

        # Initialize theme state
        self.is_dark_mode = False
        self.load_theme_preference()

        # Configure the root window

        # Configure ttk styles
        self.setup_styles()

        # Initialize variables
        self.monitor = None
        self.monitoring_thread = None
        self.is_monitoring = False
        self.log_queue = queue.Queue()
        self.setup_logging()

        self.create_widgets()
        self.load_products()

        # Start checking the log queue
        self.check_log_queue()

    def setup_styles(self):
        """Configure custom ttk styles"""
        style = ttk.Style()
        self.update_theme(self.is_dark_mode)

    def update_theme(self, is_dark):
        """Update the application theme"""
        style = ttk.Style()
        if is_dark:
            # Dark theme colors
            bg_color = '#1e1e1e'
            fg_color = '#ffffff'
            entry_bg = '#2d2d2d'
            button_bg = '#3d3d3d'
        else:
            # Light theme colors
            bg_color = '#ffffff'
            fg_color = '#000000'
            entry_bg = '#ffffff'
            button_bg = '#f8f9fa'

        # Configure styles with current theme
        style.configure('TFrame', background=bg_color)
        style.configure('Header.TLabel', 
                       font=('Helvetica', 14, 'bold'), 
                       padding=10,
                       background=bg_color,
                       foreground=fg_color)
        style.configure('TLabel',
                       background=bg_color,
                       foreground=fg_color,
                       font=('Helvetica', 10))
        style.configure('TButton', 
                       padding=8, 
                       font=('Helvetica', 10),
                       background=button_bg)
        style.configure('Monitor.TButton', 
                       font=('Helvetica', 10, 'bold'),
                       padding=10,
                       background='#28a745',
                       foreground='white')
        style.configure('Stop.TButton',
                       font=('Helvetica', 10, 'bold'),
                       padding=10,
                       background='#dc3545',
                       foreground='white')
        style.configure('TEntry', 
                       padding=8,
                       font=('Helvetica', 10))
        style.configure('TLabelframe', 
                       background=bg_color,
                       padding=15)
        style.configure('TLabelframe.Label', 
                       font=('Helvetica', 11, 'bold'),
                       background=bg_color,
                       foreground=fg_color)

        # Update root window
        self.root.configure(bg=bg_color)

        # Update all text widgets
        if hasattr(self, 'products_text'):
            self.products_text.configure(
                background=entry_bg,
                foreground=fg_color,
                insertbackground=fg_color
            )
        if hasattr(self, 'log_text'):
            self.log_text.configure(
                background=entry_bg,
                foreground=fg_color,
                insertbackground=fg_color
            )

        # Save theme preference
        self.save_theme_preference()

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.is_dark_mode = not self.is_dark_mode
        self.update_theme(self.is_dark_mode)
        self.theme_button.configure(text="🌙 Dark Mode" if not self.is_dark_mode else "☀️ Light Mode")

    def load_theme_preference(self):
        """Load saved theme preference"""
        try:
            if os.path.exists('theme_preference.json'):
                with open('theme_preference.json', 'r') as f:
                    self.is_dark_mode = json.load(f).get('dark_mode', False)
        except Exception as e:
            logger = logging.getLogger(__name__) #Added logger instantiation
            logger.error(f"Failed to load theme preference: {str(e)}")

    def save_theme_preference(self):
        """Save current theme preference"""
        try:
            with open('theme_preference.json', 'w') as f:
                json.dump({'dark_mode': self.is_dark_mode}, f)
        except Exception as e:
            logger = logging.getLogger(__name__) #Added logger instantiation
            logger.error(f"Failed to save theme preference: {str(e)}")

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(header_frame, 
                 text="Amazon Price Monitor", 
                 style='Header.TLabel').pack()

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Add New Product", padding="15")
        input_frame.pack(fill="x", pady=(0, 20))

        # URL Entry
        url_frame = ttk.Frame(input_frame)
        url_frame.pack(fill="x", pady=5)
        ttk.Label(url_frame, 
                 text="Amazon URL:", 
                 style='TLabel').pack(side="left")
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=70)
        self.url_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)

        # Price Entry
        price_frame = ttk.Frame(input_frame)
        price_frame.pack(fill="x", pady=5)
        ttk.Label(price_frame, 
                 text="Target Price (€):", 
                 style='TLabel').pack(side="left")
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(price_frame, textvariable=self.price_var, width=15)
        self.price_entry.pack(side="left", padx=(10, 0))

        # Add Product Button
        self.add_button = ttk.Button(input_frame, 
                                   text="Add Product",
                                   command=self.add_product,
                                   style='TButton')
        self.add_button.pack(pady=10)

        # Products List
        products_frame = ttk.LabelFrame(main_frame, text="Monitored Products", padding="15")
        products_frame.pack(fill="both", expand=True, pady=(0, 20))

        self.products_text = scrolledtext.ScrolledText(
            products_frame, 
            height=5,
            font=('Helvetica', 10),
            background='white',
            relief='flat',
            padx=10,
            pady=10
        )
        self.products_text.pack(fill="both", expand=True)

        # Control Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=(0, 20))

        # Left side buttons
        left_buttons_frame = ttk.Frame(control_frame)
        left_buttons_frame.pack(side="left")

        self.start_button = ttk.Button(
            left_buttons_frame, 
            text="Start Monitoring",
            command=self.toggle_monitoring,
            style='Monitor.TButton'
        )
        self.start_button.pack(side="left", padx=5)

        self.clear_button = ttk.Button(
            left_buttons_frame,
            text="Clear Products",
            command=self.clear_products,
            style='TButton'
        )
        self.clear_button.pack(side="left", padx=5)

        # Theme toggle button (right side)
        self.theme_button = ttk.Button(
            control_frame,
            text="🌙 Dark Mode" if not self.is_dark_mode else "☀️ Light Mode",
            command=self.toggle_theme,
            style='TButton'
        )
        self.theme_button.pack(side="right", padx=5)

        # Log Output
        log_frame = ttk.LabelFrame(main_frame, text="Monitoring Log", padding="15")
        log_frame.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=('Consolas', 9),
            background='white',
            relief='flat',
            padx=10,
            pady=10
        )
        self.log_text.pack(fill="both", expand=True)

        # Apply current theme
        self.update_theme(self.is_dark_mode)

    def setup_logging(self):
        # Create queue handler and set format
        queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        queue_handler.setFormatter(formatter)

        # Get the root logger and add our handler
        root_logger = logging.getLogger()
        root_logger.addHandler(queue_handler)
        root_logger.setLevel(logging.INFO)

    def load_products(self):
        try:
            if os.path.exists('products.json'):
                with open('products.json', 'r') as f:
                    self.products = json.load(f)
            else:
                self.products = []
            self.update_products_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")
            self.products = []

    def save_products(self):
        try:
            with open('products.json', 'w') as f:
                json.dump(self.products, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save products: {str(e)}")

    def add_product(self):
        url = self.url_var.get().strip()
        price_str = self.price_var.get().strip()

        if not url or not price_str:
            messagebox.showerror("Error", "Please enter both URL and target price")
            return

        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid price format. Please enter a positive number")
            return

        self.products.append({"url": url, "target_price": price})
        self.save_products()
        self.update_products_display()

        # Clear inputs
        self.url_var.set("")
        self.price_var.set("")

    def update_products_display(self):
        self.products_text.delete('1.0', tk.END)
        for i, product in enumerate(self.products, 1):
            self.products_text.insert(tk.END, 
                f"{i}. URL: {product['url']}\n   Target Price: €{product['target_price']:.2f}\n\n")

    def clear_products(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all products?"):
            self.products = []
            self.save_products()
            self.update_products_display()

    def toggle_monitoring(self):
        if not self.is_monitoring:
            if not self.products:
                messagebox.showerror("Error", "Please add at least one product to monitor")
                return

            self.start_monitoring()
            self.start_button.config(text="Stop Monitoring", style='Stop.TButton')
            self.is_monitoring = True
        else:
            self.stop_monitoring()
            self.start_button.config(text="Start Monitoring", style='Monitor.TButton')
            self.is_monitoring = False

    def start_monitoring(self):
        self.monitor = AmazonPriceMonitor()
        self.monitor.products = self.products
        self.monitoring_thread = threading.Thread(target=self.monitor.monitor_prices)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_monitoring(self):
        if self.monitor:
            self.monitor.stop_monitoring = True
            self.monitoring_thread.join(timeout=1)
            self.monitor = None

    def check_log_queue(self):
        try:
            while True:
                record = self.log_queue.get_nowait()
                msg = self.format_log_message(record)
                self.log_text.insert(tk.END, msg + '\n')
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_log_queue)

    def format_log_message(self, record):
        return f"{record.asctime} - {record.levelname} - {record.getMessage()}"

    def on_closing(self):
        if self.is_monitoring:
            self.stop_monitoring()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AmazonMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()