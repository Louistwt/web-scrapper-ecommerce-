# scrapers/laptopsdirect.py
import requests
from bs4 import BeautifulSoup
import csv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

def scrape_laptopsdirect(csv_path):
    base_url = "https://www.laptopsdirect.co.uk/ct/laptops-and-netbooks/laptops/gaming"
    product_data = []
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    for page_number in range(1, 6):
        url = f"{base_url}?pageNumber={page_number}"
        response = session.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            product_elements = soup.find_all('div', class_='OfferBox')
            for product in product_elements:
                try:
                    product_title = product.find('a', class_='offerboxtitle')['title']
                    product_price = product.find('span', class_='offerprice').text.strip()
                    product_link = product.find('a', class_='offerboxtitle')['href']
                    if not product_link.startswith('http'):
                        product_link = f"https://www.laptopsdirect.co.uk{product_link}"

                    product_page_response = session.get(product_link)
                    time.sleep(2)

                    if product_page_response.status_code == 200:
                        product_page_soup = BeautifulSoup(product_page_response.text, 'html.parser')
                        screen_size = product_page_soup.find('span', string='Screen size')
                        screen_size = screen_size.find_next('span', class_='BodyText').text.strip() if screen_size else 'N/A'
                        ram = product_page_soup.find('span', string='Installed Size')
                        ram = ram.find_next('span', class_='BodyText').text.strip() if ram else 'N/A'
                        ssd_capacity = product_page_soup.find('span', string='SSD Capacity')
                        ssd_capacity = ssd_capacity.find_next('span', class_='BodyText').text.strip() if ssd_capacity else 'N/A'
                        gpu = product_page_soup.find('span', string='Graphics card')
                        gpu = gpu.find_next('span', class_='BodyText').text.strip() if gpu else 'N/A'

                        product_data.append({
                            'Product Title': product_title,
                            'Product Price': product_price,
                            'Product Link': product_link,
                            'Screen Size': screen_size,
                            'RAM': ram,
                            'SSD Capacity': ssd_capacity,
                            'Graphics card': gpu,
                        })
                    else:
                        print(f"Failed to fetch details for {product_title}: {product_page_response.status_code}")
                except AttributeError as e:
                    print(f"Error parsing product on page {page_number}: {e}")
        else:
            print(f"Failed to fetch page {url}: {response.status_code}")

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Product Title', 'Product Price', 'Product Link', 'Screen Size', 'RAM', 'SSD Capacity', 'Graphics card']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(product_data)
    print(f"Data saved to {csv_path}")

if __name__ == '__main__':
    scrape_laptopsdirect('../data/test_laptopsdirect.csv')  # Path relative to scrapers/