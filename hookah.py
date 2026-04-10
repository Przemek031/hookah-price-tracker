import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

def scrape_hookah_hub():
    base_url = "https://hookahhub.store/collection/tobacco"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    all_data = []
    page = 1

    print("Starting data collection...")

    while True:
        url = f"{base_url}?order=price&page={page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            products = soup.find_all('form', class_='product-preview')

            if not products:
                break

            found_on_page = 0
            for product in products:
                title_div = product.find('div', class_='product-preview__title')
                if not title_div: 
                    continue
                
                full_name = title_div.get_text(strip=True)
                link = "https://hookahhub.store" + title_div.find('a')['href']

                price = None
                price_tags = product.find_all('span', class_='product-preview__price-cur')
                for tag in price_tags:
                    val = tag.get_text(strip=True)
                    if val:
                        price_num = re.sub(r'[^\d,.]', '', val).replace(',', '.')
                        try:
                            price = float(price_num)
                            break
                        except: 
                            continue

                weight_match = re.search(r'(\d+)\s*[gг]', full_name, re.IGNORECASE)
                weight = int(weight_match.group(1)) if weight_match else None

                if weight and price:
                    price_per_gram = round(price / weight, 4)
                    all_data.append({
                        'Product Name': full_name,
                        'Price (PLN)': price,
                        'Weight (g)': weight,
                        'Price per Gram (PLN/g)': price_per_gram,
                        'URL': link
                    })
                    found_on_page += 1

            print(f"Page {page}: Processed {found_on_page} products.")
            if found_on_page == 0: 
                break
            
            page += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    if all_data:
        df = pd.DataFrame(all_data)
        df = df.sort_values(by='Price per Gram (PLN/g)')
        
        file_name = "tobacco_ranking.xlsx"
        df.to_excel(file_name, index=False)
        print(f"\nSuccess! Collected {len(df)} products in total.")
        print(f"Data saved to: {file_name}")
    else:
        print("No data collected.")

if __name__ == "__main__":
    scrape_hookah_hub()