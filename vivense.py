import math
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

link_list = []

base_url ="https://www.vivense.com"

product_list_ccount = 415
product_one_page_count = 60
range_count =  math.ceil(product_list_ccount/product_one_page_count)

for i in range(1,range_count+1):
    time.sleep(2)
    url = f"https://www.vivense.com/arama?page={i}&q=UV3"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.select('.category_page_container > #product-list-wrapper .product-list .product_images_area a')
        for a_tag in a_tags:
            product_link = base_url + a_tag['href']
            link_list.append(product_link)
    else:
        print(f"Hata kodu: {response.status_code}")



time.sleep(2)
# İlgili kısımların güncellenmiş hali
df_list = []

for link in link_list:
    time.sleep(1)
    print("Link: ", link)
    product_response = requests.get(link)
    if product_response.status_code == 200:
        soup = BeautifulSoup(product_response.text, 'html.parser')
        try:
            product_category = soup.select_one('ol#breadcrumb-ol li:nth-child(2)').text.strip()
            

            title = soup.select_one('.product-title').text.strip()
            sku = soup.select_one('h1 span.product-sku').text.strip()
            
            try:
                price = soup.select_one('span.price.new-price').text.strip()
            except AttributeError:
                price = "0"  

            try:
                old_price = soup.select_one('span.old-price del').text.strip()
            except AttributeError:
                old_price = "0"  
            
            try:
                basket_price = soup.select_one('div.sticky_column div.product-campaigns__card div.product-campaigns__amount.super').text.strip()
            except AttributeError:
                basket_price = "0"  


            img_list = soup.select('div.ws_thumbs img')
            print("title",title)
            file_name = title
            folder_name = "Vivense"
            # if not os.path.exists(os.path.join(folder_name, file_name)):
            #     os.makedirs(os.path.join(folder_name, file_name))

            # img_counter = 1
            # for img in img_list:
            #     img_url = img.get("src")  
            #     time.sleep(2)
            #     img_response = requests.get(img_url)
            #     if img_response.status_code == 200:
            #         file_path = os.path.join(folder_name, file_name, f"{title}_{img_counter}.jpg")
            #         with open(file_path, 'wb') as img_file:
            #             img_file.write(img_response.content)

            #     else:
            #         print(f"Hata: {img_url} adresine erişilemedi.")

            #     img_counter += 1

            desc_table = soup.find('tbody', id='producttables')
            if desc_table:
                rows = desc_table.find_all('tr')
                desc_list = []
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        title = cells[0].text.strip()
                        description = cells[1].text.strip()
                        desc_list.append(f"{title}: {description}")
            desc_text = '\n'.join(desc_list)
            

            df_list.append(pd.DataFrame({
                        'Product Link': [link],
                        'Title': [file_name],
                        'Sku': [sku],
                        'Price': [price],
                        "Old Price": [old_price],
                        'Basket Price': [basket_price],
                        'Desc.': [desc_text] ,
                        'Category':[product_category] 
                    }))
        except Exception as e:
            print(e)
    else:
        print(f"Hata kodu: {product_response.status_code}")


df = pd.concat(df_list, ignore_index=True)
df.to_excel(os.path.join(folder_name,'output.xlsx'), index=False)

