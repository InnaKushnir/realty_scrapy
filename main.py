import requests
from bs4 import BeautifulSoup
import json

url = "https://realtylink.org/en/properties~for-rent"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    property_container = soup.find("div", id="property-result")

    if property_container:
        property_items = property_container.find_all("div", class_="thumbnail property-thumbnail-feature legacy-reset")

        json_objects = []

        for item in property_items:
            property_link = item.find("a")["href"]

            address_container = item.select_one(
                "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 > div.d-flex.mt-1 h2.pt-1")
            if address_container:
                address = address_container.get_text.strip()
            else:
                address = "Адресу не вдалося знайти"

            json_object = {
                "link": property_link,
                "title": "Назва оголошення",
                "region": "Регіон",
                "address": address,
                "description": "Опис оголошення",
                "images": ["https://link-to-image1.jpg", "https://link-to-image2.jpg"],
                "publication_date": "2024-04-12",
                "price": 1000,
                "rooms": 3,
                "area": 120
            }

            json_objects.append(json_object)

        for obj in json_objects:
            print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        print("Сталася помилка при отриманні сторінки:", response.status_code)
