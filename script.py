import requests
from bs4 import BeautifulSoup
import csv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

# Define the base URL
base_url = "https://www.laptopsdirect.co.uk/ct/laptops-and-netbooks/laptops/gaming"

# Initialize a list to store data
product_data = []

# Create a session with retry settings
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount('https://', adapter)

# Loop through the pages
for page_number in range(1, 6):  # There are 5 pages
    # Construct the URL for each page
    url = f"{base_url}?pageNumber={page_number}"

    # Send an HTTP GET request to the URL
    response = session.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the product elements on the page
        product_elements = soup.find_all('div', class_='OfferBox')

        # Extract data from each product element
        for product in product_elements:
            product_title = product.find('a', class_='offerboxtitle')['title']
            product_price = product.find('span', class_='offerprice').text.strip()

            # Extract product link
            product_link = product.find('a', class_='offerboxtitle')['href']

            # Check if the product_link has a valid scheme (http/https)
            if not product_link.startswith('http'):
                product_link = f"https://www.laptopsdirect.co.uk{product_link}"

            # Send a request to the individual product page with retries
            product_page_response = session.get(product_link)

            # Add a 2-second delay to avoid overloading the server
            time.sleep(2)

            if product_page_response.status_code == 200:
                product_page_soup = BeautifulSoup(product_page_response.text, 'html.parser')

                # Extract additional product information
                screen_size = product_page_soup.find('span', string='Screen size')
                series = product_page_soup.find('span', string='Series')
                number = product_page_soup.find('span', string='Number')
                ram = product_page_soup.find('span', string='Installed Size')
                ssd_capacity = product_page_soup.find('span', string='SSD Capacity')
                gpu = product_page_soup.find('span', string='Graphics card')

                # Check if the elements are found before calling find_next
                screen_size = screen_size.find_next('span', class_='BodyText').text.strip() if screen_size else None
                series = series.find_next('span', class_='BodyText').text.strip() if series else None
                number = number.find_next('span', class_='BodyText').text.strip() if number else None
                ram = ram.find_next('span', class_='BodyText').text.strip() if ram else None
                ssd_capacity = ssd_capacity.find_next('span', class_='BodyText').text.strip() if ssd_capacity else None
                gpu = gpu.find_next('span', class_='BodyText').text.strip() if gpu else None

                # Extract product code
                product_code_element = product_page_soup.find('span', class_='sku text-grey margin-right-15')
                product_code = product_code_element.text.strip() if product_code_element else None

                # Extract Quickfind Code, Resolution, Refresh Rate, and Screen Type
                quickfind_code = product_page_soup.find('span', {'id': 'prodPage_QuickFind'}).text.strip() if product_page_soup.find('span', {'id': 'prodPage_QuickFind'}) else None
                resolution = product_page_soup.find('span', {'class': 'BodyText'}, string='2560 x 1600').find_next('span', class_='BodyText').text.strip() if product_page_soup.find('span', {'class': 'BodyText'}, string='2560 x 1600') else None
                refresh_rate = product_page_soup.find('span', {'class': 'BodyText'}, string='240Hz').find_next('span', class_='BodyText').text.strip() if product_page_soup.find('span', {'class': 'BodyText'}, string='240Hz') else None
                screen_type = product_page_soup.find('span', {'class': 'BodyText'}, string='LED').find_next('span', class_='BodyText').text.strip() if product_page_soup.find('span', {'class': 'BodyText'}, string='LED') else None

                # Create a dictionary for the product and append it to the list
                product_data.append({
                    'Product Title': product_title,
                    'Product Price': product_price,
                    'Product Code': product_code,
                    'Product Link': product_link,
                    'Screen Size': screen_size,
                    'Series': series,
                    'Number': number,
                    'RAM': ram,
                    'SSD Capacity': ssd_capacity,
                    'Graphics card': gpu,
                    'Quickfind Code': quickfind_code,
                    'Resolution': resolution,
                    'Refresh Rate': refresh_rate,
                    'Screen Type': screen_type,
                })
            else:
                print(f"Failed to fetch product details for: {product_title}")
    else:
        print(f"Failed to fetch page: {url}")

# Define the CSV file path
csv_file_path = 'gaming.csv'

# Save the data to a CSV file
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Product Title', 'Product Price', 'Product Code', 'Product Link', 'Screen Size', 'Series', 'Number', 'RAM', 'SSD Capacity', 'Graphics card', 'Quickfind Code', 'Resolution', 'Refresh Rate', 'Screen Type']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header row
    writer.writeheader()

    # Write the data
    for item in product_data:
        writer.writerow(item)

print(f"Data saved to {csv_file_path}")
