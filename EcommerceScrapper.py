import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
from bs4 import BeautifulSoup
import csv
import os
import re
import time

class ECommerceScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Universal Web Scraper")
        master.geometry("850x680")
        master.minsize(700, 580)
        master.resizable(True, True)

        # --- Configure styles for a modern, flat look ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Define a consistent color palette
        COLOR_PRIMARY = '#007BFF'
        COLOR_ACCENT = '#28A745'
        COLOR_BACKGROUND_LIGHT = '#F8F9FA'
        COLOR_BACKGROUND_MEDIUM = '#E9ECEF'
        COLOR_TEXT_DARK = '#343A40'
        COLOR_TEXT_MUTED = '#6C757D'
        COLOR_BORDER_LIGHT = '#DEE2E6'
        COLOR_ERROR = '#DC3545'

        # Apply general background and font to all widgets
        self.style.configure('.',
                            background=COLOR_BACKGROUND_LIGHT,
                            font=('Inter', 10, 'normal'))

        # TFrame style
        self.style.configure('TFrame', background=COLOR_BACKGROUND_LIGHT)

        # TLabel style
        self.style.configure('TLabel',
                            background=COLOR_BACKGROUND_LIGHT,
                            foreground=COLOR_TEXT_DARK,
                            font=('Inter', 10, 'bold'))

        # TEntry style
        self.style.configure('TEntry',
                            fieldbackground='#FFFFFF',
                            bordercolor=COLOR_BORDER_LIGHT,
                            relief='solid',
                            borderwidth=1,
                            padding=(10, 8))
        self.style.map('TEntry',
                    fieldbackground=[('focus', COLOR_BACKGROUND_MEDIUM)],
                    bordercolor=[('focus', COLOR_PRIMARY)])

        # TButton style
        self.style.configure('TButton',
                            font=('Inter', 11, 'bold'),
                            padding=(20, 12),
                            background=COLOR_PRIMARY,
                            foreground='white',
                            relief='flat',
                            borderwidth=0,
                            focusthickness=0)
        self.style.map('TButton',
                    background=[('active', COLOR_PRIMARY), ('!disabled', COLOR_PRIMARY)],
                    foreground=[('active', 'white'), ('!disabled', 'white')],
                    bordercolor=[('active', COLOR_PRIMARY)])

        # Text widget (Log Area) style
        self.master.option_add('*Text.background', COLOR_BACKGROUND_MEDIUM)
        self.master.option_add('*Text.foreground', COLOR_TEXT_DARK)
        self.master.option_add('*Text.font', 'Inter 9')
        self.master.option_add('*Text.relief', 'flat')
        self.master.option_add('*Text.borderwidth', 1)
        self.master.option_add('*Text.highlightbackground', COLOR_BORDER_LIGHT)
        self.master.option_add('*Text.highlightcolor', COLOR_PRIMARY)
        self.master.option_add('*Text.highlightthickness', 1)

        self.url_var = tk.StringVar(value="")
        self.filename_var = tk.StringVar(value="scraped_data.csv")
        self.directory_var = tk.StringVar(value=os.getcwd())
        self.status_var = tk.StringVar(value="Enter URL, then click 'Extract Data'.")

        self._create_widgets()

    def _create_widgets(self):
        """Creates and arranges the GUI widgets."""
        main_frame = ttk.Frame(self.master, padding="30")
        main_frame.pack(pady=20, padx=20, fill='both', expand=True)

        input_frame = ttk.Frame(main_frame, padding="25", relief='flat', borderwidth=1, style='TFrame')
        input_frame.config(relief='solid', borderwidth=1)
        input_frame.pack(pady=15, padx=15, fill='x')

        ttk.Label(input_frame, text="Target URL:").grid(row=0, column=0, sticky='w', pady=10, padx=10)
        self.url_entry = ttk.Entry(input_frame, textvariable=self.url_var, width=80)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=10, padx=10)

        ttk.Label(input_frame, text="CSV Filename:").grid(row=1, column=0, sticky='w', pady=10, padx=10)
        self.filename_entry = ttk.Entry(input_frame, textvariable=self.filename_var, width=40)
        self.filename_entry.grid(row=1, column=1, sticky='ew', pady=10, padx=10)

        ttk.Label(input_frame, text="Output Directory:").grid(row=2, column=0, sticky='w', pady=10, padx=10)
        self.directory_entry = ttk.Entry(input_frame, textvariable=self.directory_var, width=40)
        self.directory_entry.grid(row=2, column=1, sticky='ew', pady=10, padx=10)
        browse_button = ttk.Button(input_frame, text="Browse", command=self._browse_directory)
        browse_button.grid(row=2, column=2, sticky='ew', pady=10, padx=10)

        input_frame.grid_columnconfigure(1, weight=1)

        extract_button = ttk.Button(main_frame, text="Extract Data", command=self.start_scraping)
        extract_button.pack(pady=20, padx=15, fill='x')

        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=700, justify='center',
                                    font=('Inter', 10, 'italic'), foreground=self.style.lookup('.', 'foreground'))
        self.status_label.pack(pady=15, padx=15, fill='x')

        ttk.Label(main_frame, text="Scraping Log:").pack(pady=(15, 8), padx=15, anchor='w')
        self.log_text = tk.Text(main_frame, height=12, width=80, state='disabled', wrap='word')
        self.log_text.pack(pady=(0, 20), padx=15, expand=True, fill='both')

    def _browse_directory(self):
        """Opens a directory chooser dialog and updates the directory_var."""
        chosen_directory = filedialog.askdirectory()
        if chosen_directory:
            self.directory_var.set(chosen_directory)

    def _update_log(self, message, is_error=False):
        """Updates the log text area with a new message."""
        self.log_text.config(state='normal')
        if is_error:
            self.log_text.insert(tk.END, message + "\n", "error")
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.log_text.tag_config("error", foreground=self.style.lookup('TButton', 'focuscolor'))

    def start_scraping(self):
        """Initiates the scraping process, validating inputs and handling errors."""
        url = self.url_var.get().strip()
        filename = self.filename_var.get().strip()
        directory = self.directory_var.get().strip()

        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

        self.status_var.set("Starting scraping...")
        self._update_log("Validation inputs...")

        if not url:
            messagebox.showerror("Input Error", "Please enter a URL.")
            self.status_var.set("Error: URL is empty.")
            self._update_log("Error: URL is empty.", is_error=True)
            return
        if not (url.startswith('http://') or url.startswith('https://')):
            messagebox.showerror("Input Error", "URL must start with http:// or https://")
            self.status_var.set("Error: Invalid URL format.")
            self._update_log("Error: Invalid URL format.", is_error=True)
            return
        if not filename:
            messagebox.showerror("Input Error", "Please enter a CSV filename.")
            self.status_var.set("Error: Filename is empty.")
            self._update_log("Error: Filename is empty.", is_error=True)
            return
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
            self.filename_var.set(filename)

        output_filepath = os.path.join(directory, filename)

        self._update_log(f"Attempting to scrape: {url}")
        self._update_log(f"Saving to: {output_filepath}")

        self.master.after(100, lambda: self._scrape_and_save(url, output_filepath))

    def _scrape_and_save(self, url, output_filepath):
        """Performs the web scraping and saves the data to a CSV file."""
        try:
            products_data = self._extract_product_info(url)
            if products_data:
                # Determine headers dynamically based on extracted data, prioritizing Name, Price, Rating
                preferred_headers = ['Name', 'Price', 'Rating']
                all_extracted_keys = set()
                for row in products_data:
                    all_extracted_keys.update(row.keys())
                
                headers = []
                for header in preferred_headers:
                    if header in all_extracted_keys:
                        headers.append(header)
                        all_extracted_keys.remove(header)
                
                remaining_headers = sorted(list(all_extracted_keys))
                headers.extend(remaining_headers)

                self._save_to_csv(products_data, output_filepath, headers)
                self.status_var.set(f"Successfully extracted {len(products_data)} entries and saved to {output_filepath}")
                self._update_log(f"SUCCESS: Data saved to {output_filepath}")
            else:
                self.status_var.set("No data found that matches common patterns. Check URL or manually inspect structure.")
                self._update_log("WARNING: No structured data (products/quotes) found matching common patterns. This might be a highly custom site or non-extractable content.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Network Error", f"Could not connect to the URL: {e}")
            self.status_var.set(f"Error: Network issue - {e}")
            self._update_log(f"ERROR: Network error - {e}", is_error=True)
        except Exception as e:
            messagebox.showerror("Scraping Error", f"An unexpected error occurred during scraping: {e}")
            self.status_var.set(f"Error: An unexpected error occurred - {e}")
            self._update_log(f"ERROR: Unexpected scraping error - {e}", is_error=True)

    def _get_site_specific_selectors(self, url):
        """Returns specific selectors for known test sites to ensure reliability."""
        if url.startswith('http://books.toscrape.com'):
            self._update_log("Applying site-specific selectors for books.toscrape.com")
            return {
                'container': ['article.product_pod'],
                'name': ['h3 a'],
                'price': ['p.price_color'],
                'rating': ['p.star-rating'],
                'quote_text': [],
                'quote_author': []
            }
        elif url.startswith('http://quotes.toscrape.com'):
            self._update_log("Applying site-specific selectors for quotes.toscrape.com")
            return {
                'container': ['div.quote'],
                'name': [],
                'price': [],
                'rating': [],
                'quote_text': ['span.text'],
                'quote_author': ['small.author']
            }
        return None

    def _extract_product_info(self, url):
        """Extracts product-like information (name, price, rating) or general data."""
        self._update_log(f"Fetching content from: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        extracted_data = []

        site_specific_selectors = self._get_site_specific_selectors(url)

        PRODUCT_CONTAINER_SELECTORS = []
        if site_specific_selectors and site_specific_selectors['container']:
            PRODUCT_CONTAINER_SELECTORS.extend(site_specific_selectors['container'])
        PRODUCT_CONTAINER_SELECTORS.extend([
            'article.product_pod',
            'div.product-grid-item',
            'li.product-item',
            'div.product-card',
            'article.product',
            'div[data-component-type="s-search-result"]',
            '.s-result-item',
            '.product-layout .product-thumb',
            '.item-row',
            '.result-item',
            '[class*="product"]',
            '[id*="product"]',
            '[data-test*="product"]',
            '.col-md-4.col-sm-6.col-xl-3'
        ])

        PRODUCT_NAME_SELECTORS = []
        if site_specific_selectors and site_specific_selectors['name']:
            PRODUCT_NAME_SELECTORS.extend(site_specific_selectors['name'])
        PRODUCT_NAME_SELECTORS.extend([
            'h3 a',
            'h2.product-title a',
            'a.product-name',
            'span.a-size-medium.a-color-base.a-text-normal',
            'a.s-link-style span.a-text-normal',
            '.caption h4 a',
            'h1[itemprop="name"]',
            'h2', 'h3', 'h4',
            'a[title]',
            '.title', '.name', '.product-name', '.item-name'
        ])

        PRODUCT_PRICE_SELECTORS = []
        if site_specific_selectors and site_specific_selectors['price']:
            PRODUCT_PRICE_SELECTORS.extend(site_specific_selectors['price'])
        PRODUCT_PRICE_SELECTORS.extend([
            'p.price_color',
            'span.product-price',
            'span.a-price-whole',
            'span.a-offscreen',
            '.price .price-new',
            '.price', '.amount', '.current-price', '.display-price', '.sale-price',
            'strong.price',
            'span[data-a-color="price"]'
        ])

        PRODUCT_RATING_SELECTORS = []
        if site_specific_selectors and site_specific_selectors['rating']:
            PRODUCT_RATING_SELECTORS.extend(site_specific_selectors['rating'])
        PRODUCT_RATING_SELECTORS.extend([
            'p.star-rating',
            'div.star-rating span.rating-value',
            'span.a-icon-alt',
            'div.rating span.fa-star.active',
            '.rating', '.stars', '[class*="rating"]', 'i[class*="star"]'
        ])

        QUOTE_CONTAINER_SELECTORS = []
        if site_specific_selectors and site_specific_selectors['container'] and url.startswith('http://quotes.toscrape.com'):
            QUOTE_CONTAINER_SELECTORS.extend(site_specific_selectors['container'])
        else:
            QUOTE_CONTAINER_SELECTORS.append('div.quote')

        QUOTE_TEXT_SELECTORS = []
        if site_specific_selectors and site_specific_selectors['quote_text']:
            QUOTE_TEXT_SELECTORS.extend(site_specific_selectors['quote_text'])
        else:
            QUOTE_TEXT_SELECTORS.extend([
                'span.text',
                'div.quote-content'
            ])

        QUOTE_AUTHOR_SELECTORS = []
        if site_specific_selectors and site_specific_selectors['quote_author']:
            QUOTE_AUTHOR_SELECTORS.extend(site_specific_selectors['quote_author'])
        else:
            QUOTE_AUTHOR_SELECTORS.extend([
                'small.author',
                '.quote-author'
            ])

        containers = []
        
        if site_specific_selectors and site_specific_selectors['container'] and not url.startswith('http://quotes.toscrape.com'):
            self._update_log(f"Attempting to find product containers using site-specific selector(s): {site_specific_selectors['container']}")
            for selector in site_specific_selectors['container']:
                try:
                    found_specific = soup.select(selector, limit=100)
                    if found_specific:
                        self._update_log(f"Successfully found containers with specific selector: '{selector}'")
                        containers.extend(found_specific)
                        break
                except Exception as e:
                    pass

        if not containers:
            self._update_log("No site-specific product containers found or not applicable. Trying general product selectors.")
            for selector in PRODUCT_CONTAINER_SELECTORS:
                try:
                    found = soup.select(selector, limit=100)
                    if found:
                        self._update_log(f"Found containers using general selector: '{selector}'")
                        containers.extend(found)
                        break
                except Exception as e:
                    pass

        seen_containers = set()
        unique_containers = []
        for container in containers:
            if hash(container) not in seen_containers:
                unique_containers.append(container)
                seen_containers.add(hash(container))
        containers = unique_containers

        if not containers:
            self._update_log("No common product containers found. Attempting to find quote containers.", is_error=False)
            for selector in QUOTE_CONTAINER_SELECTORS:
                try:
                    found = soup.select(selector, limit=100)
                    if found:
                        self._update_log(f"Found quote containers using selector: '{selector}'")
                        containers.extend(found)
                        break
                except Exception as e:
                    pass
            
            seen_containers = set()
            unique_containers = []
            for container in containers:
                if hash(container) not in seen_containers:
                    unique_containers.append(container)
                    seen_containers.add(hash(container))
            containers = unique_containers

        if not containers:
            self._update_log("No specific item containers found. Attempting to extract general page content.", is_error=False)
            body_text = soup.body.get_text(separator=' ', strip=True) if soup.body else ''
            if body_text:
                extracted_data.append({'Content': body_text[:500] + '...' if len(body_text) > 500 else body_text})
            return extracted_data

        self._update_log(f"Processing {len(containers)} detected items.")

        for i, container in enumerate(containers):
            item_data = {}
            name = "N/A"
            price = "N/A"
            rating = "N/A"
            
            is_quote_site = url.startswith('http://quotes.toscrape.com')
            is_quote_container = 'quote' in container.get('class', []) if container else False

            if is_quote_site or is_quote_container:
                quote_text_el = None
                for sel in QUOTE_TEXT_SELECTORS:
                    q_el = container.select_one(sel)
                    if q_el:
                        quote_text_el = q_el
                        break
                if quote_text_el:
                    item_data['Quote'] = quote_text_el.get_text(strip=True)

                quote_author_el = None
                for sel in QUOTE_AUTHOR_SELECTORS:
                    a_el = container.select_one(sel)
                    if a_el:
                        quote_author_el = a_el
                        break
                if quote_author_el:
                    item_data['Author'] = quote_author_el.get_text(strip=True)
                
                if 'Quote' in item_data:
                    extracted_data.append(item_data)
                    continue

            for selector in PRODUCT_NAME_SELECTORS:
                try:
                    name_element = container.select_one(selector)
                    if name_element:
                        name = name_element.get_text(strip=True)
                        if name:
                            break
                except Exception as e:
                    pass
            item_data['Name'] = name

            found_price_text = None
            for selector in PRODUCT_PRICE_SELECTORS:
                try:
                    price_element = container.select_one(selector)
                    if price_element:
                        if 'a-offscreen' in price_element.get('class', []):
                            found_price_text = price_element.get_text(strip=True)
                        elif price_element.name == 'span' and ('a-price-whole' in price_element.get('class', []) or 'price' in price_element.get('class', [])):
                            whole_part = price_element.get_text(strip=True)
                            fraction_element = container.select_one('span.a-price-fraction')
                            fraction_part = fraction_element.get_text(strip=True) if fraction_element else ''
                            found_price_text = f"{whole_part}{fraction_part}" if fraction_part else whole_part
                        else:
                            found_price_text = price_element.get_text(strip=True)
                        if found_price_text:
                            break
                except Exception as e:
                    pass

            if found_price_text and found_price_text != "N/A":
                price = re.sub(r'[^\d.,]+', '', found_price_text).strip()
                if price.count(',') > 1 and '.' in price:
                    price = price.replace(',', '')
                elif price.count('.') > 1 and ',' in price:
                    price = price.replace('.', '').replace(',', '.')
                elif price.startswith('.'):
                    price = '0' + price

            item_data['Price'] = price

            found_rating_text = None
            for selector in PRODUCT_RATING_SELECTORS:
                try:
                    rating_element = container.select_one(selector)
                    if rating_element:
                        if 'star-rating' in rating_element.get('class', []):
                            rating_classes = rating_element.get('class')
                            if len(rating_classes) > 1:
                                rating_word = rating_classes[1].lower()
                                rating_map = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5'}
                                found_rating_text = rating_map.get(rating_word, "N/A")
                        elif 'a-icon-alt' in rating_element.get('class', []):
                            found_rating_text = rating_element.get_text(strip=True)
                        elif 'rating' in rating_element.get('class', []) and rating_element.name == 'div':
                            active_stars = rating_element.find_all(class_=re.compile(r'fa-star|active|filled', re.IGNORECASE))
                            if active_stars:
                                found_rating_text = f"{len(active_stars)} stars"
                            else:
                                found_rating_text = rating_element.get_text(strip=True)
                        else:
                            found_rating_text = rating_element.get_text(strip=True)
                        if found_rating_text:
                            break
                except Exception as e:
                    pass

            if found_rating_text and found_rating_text != "N/A":
                match = re.search(r'(\d+\.?\d*)', found_rating_text)
                if match:
                    rating = match.group(1)
                else:
                    rating = found_rating_text
            item_data['Rating'] = rating

            if any(val != "N/A" for key, val in item_data.items() if key in ['Name', 'Price', 'Rating', 'Quote', 'Author']):
                extracted_data.append(item_data)
                self._update_log(f"Extracted: {item_data}")

        return extracted_data

    def _save_to_csv(self, data, filepath, headers):
        """Saves the extracted data to a CSV file."""
        if not data:
            self._update_log("No data to save.")
            return

        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            self._update_log(f"Data successfully written to {filepath}")
        except IOError as e:
            messagebox.showerror("File Error", f"Could not write to CSV file: {e}")
            self.status_var.set(f"Error: File write failed - {e}")
            self._update_log(f"ERROR: File write error - {e}", is_error=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = ECommerceScraperApp(root)
    root.mainloop()