import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import math
import os
link_list = []



base_url = {
    "1": {
        "product_count": 31,
        "category": "Oda Seti",
        "url": "https://milvaki.com/urun-kategori/oda-seti/"
    },
    "2": {
        "product_count": 30,
        "category": "Tv Ünitesi",
        "url": "https://milvaki.com/urun-kategori/tv-unitesi/"
    },
    "3": {
        "product_count": 27,
        "category": "Kitaplıklar & Sehhbalar",
        "url": "https://milvaki.com/urun-kategori/kitapliklar-sehpalar/"
    },
    "4": {
        "product_count": 9,
        "category": "Gardıroplar",
        "url": "https://milvaki.com/urun-kategori/gardiroplar/"
    },
    "5": {
        "product_count": 6,
        "category": "Komidin, Şifonyer ve Puflar",
        "url": "https://milvaki.com/urun-kategori/komidin-sifonyer-puf/"
    },
    "6": {
        "product_count": 10,
        "category": "Yatak Odası Setleri",
        "url": "https://milvaki.com/urun-kategori/oda-seti/yatak-odasi-setleri/"
    }
}


product_list_urls = []


def get_products_list(url,product_count,category):
    range_count =  math.ceil(product_count/12)
    print("Product count:",product_count)
    print("Range count:",range_count)

    for i in range(1, range_count+1):  # İlk sayfa zaten alındığından 1'den başlayın
        time.sleep(2)
        page_url = f"{url}page/{i}"
        print("Got url:", page_url)
        response = requests.get(page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            a_tags = soup.select('ul.main-products li h2.woocommerce-loop-product__title a')
            for a_tag in a_tags:
                product_link = a_tag['href']
                product_list_urls.append(product_link)
            else:
                print(f"Hata kodu: {response.status_code}")

    if not os.path.exists(category):
        os.makedirs(category)

    df_list = []
    for link in product_list_urls:
        time.sleep(2)
        product_response = requests.get(link)

        if product_response.status_code == 200:
            product_soup = BeautifulSoup(product_response.text, 'html.parser')
            try:
                title = product_soup.select_one('.product_title.entry-title').text.strip() .replace("/"," ")
            except:
                title = "Başlık bullunamdı"
                pass
            try:
                sku = product_soup.select_one('.sku').text.strip()
            except:
                sku = "sku bulunamadı"
                pass
            try:
                price = product_soup.select_one('div.summary.entry-summary .woocs_price_code').text.strip().replace("₺","")
            except:
                price = "price bulunnamadı"
                pass
            try:
                description = product_soup.select_one('div.woocommerce-tabs.wc-tabs-wrapper .woocommerce-Tabs-panel--description').text.strip() 
            except:
                description = "Açıklama Bulunnamadı"
                pass

            df_list.append(pd.DataFrame({
                'Product Link': [link],
                'Title': [title],
                'Sku': [sku],
                'Price': [price],
                'Desc':[description]
            }))


            img_list = product_soup.select("div.woocommerce-product-gallery.woocommerce-product-gallery--with-images.woocommerce-product-gallery--columns-4.images.lightbox-support.zoom-support div img")
            

            # Başlık içindeki özel karakterleri kaldırarak dosya adı oluşturma
            file_name = title
            
            # Başlığa göre dosya oluşturma
            if not os.path.exists(os.path.join(category, file_name)):
                os.makedirs(os.path.join(category, file_name))

            img_counter = 1
            for img in img_list:
                img_url = img.get("data-large_image")  
                time.sleep(2)
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    # Dosya adını oluştur
                    file_path = os.path.join(category, file_name, f"{title}_{img_counter}.jpg")


                    # Görüntüyü kaydet
                    with open(file_path, 'wb') as img_file:
                        img_file.write(img_response.content)

                else:
                    print(f"Hata: {img_url} adresine erişilemedi.")

                img_counter += 1


    df = pd.concat(df_list, ignore_index=True)
    df.to_excel(f'{category}/output.xlsx', index=False)
    df_list.clear()
    product_list_urls.clear()



if __name__ == '__main__':

    json_data = json.dumps(base_url, indent=4)

    for key, value in base_url.items():
        if isinstance(value, dict): 
            url = value["url"]
            print("URL--------",url)
            product_count = value["product_count"]
            category = value["category"]
            get_products_list(url,product_count,category)
        else:  
            url = value





