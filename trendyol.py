import math
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from urllib.parse import urlparse, parse_qs



link_list = []

base_url ="https://www.trendyol.com"

product_list_ccount = 68
product_one_page_count = 24
range_count =  math.ceil(product_list_ccount/product_one_page_count)


for i in range(1,range_count+1):
    time.sleep(2)
    url = f"https://www.trendyol.com/sr?mid=106601&os=1&pi={i}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.select('.p-card-wrppr.with-campaign-view a')
        for a_tag in a_tags:
            product_link = base_url + a_tag['href']
            link_list.append(product_link)
    else:
        print(f"Hata kodu: {response.status_code}")



time.sleep(2)
df_list = []

other_product_list=[]

for link in link_list:
    time.sleep(1)
    product_response = requests.get(link)
    if product_response.status_code == 200:
        soup = BeautifulSoup(product_response.text, 'html.parser')
        # with open("parsed_html.txt", "w", encoding="utf-8") as file:
        #     file.write(str(soup))
        try:
            product_category = soup.select_one('div#marketing-product-detail-breadcrumb-without-gender .product-detail-breadcrumb a:last-child').text.strip()
            title = soup.select_one('h1.pr-new-br').text.strip()
            sku = link.split("-p-")[1].split("?")[0]
            try:
                price = soup.select_one('.product-price-container span.prc-dsc').text.strip()
            except AttributeError:
                price = "0"  

            try:
                old_price = soup.select_one('.product-price-container span.prc-org').text.strip()
            except AttributeError:
                old_price = "0"  
            
            img_list = soup.select('.gallery-modal.hidden img')
            file_name = title
            folder_name = "Trendyol"
            if not os.path.exists(os.path.join(folder_name, file_name)):
                os.makedirs(os.path.join(folder_name, file_name))

            img_counter = 1
            for img in img_list:
                img_url = img.get("src")  
                time.sleep(2)
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    file_path = os.path.join(folder_name, file_name, f"{title}_{img_counter}.jpg")
                    with open(file_path, 'wb') as img_file:
                        img_file.write(img_response.content)

                else:
                    print(f"Hata: {img_url} adresine erişilemedi.")

                img_counter += 1

            desc_list = []

            desc_table = soup.select("div.detail-border div.info-wrapper .detail-desc-list li")
            for desc in desc_table:
                desc_list.append(desc.get_text(strip=True))

            joined_desc = '\n'.join(desc_list)

            df_list.append(pd.DataFrame({
                        'Product Link': [link],
                        'Sku':[sku],
                        'Title': [file_name],
                        'Price': [price],
                        "Old Price": [old_price],
                        'Desc.': [joined_desc] ,
                        'Category':[product_category] 
                    }))
        except Exception as e:
            print(e)
    else:
        print(f"Hata kodu: {product_response.status_code}")


df = pd.concat(df_list, ignore_index=True)
df.to_excel(os.path.join(folder_name,'output.xlsx'), index=False)

print(other_product_list)
