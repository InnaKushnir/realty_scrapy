import json
import re
from wsgiref import headers
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()

url = "https://realtylink.org/en/properties~for-rent"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}


def get_links():
    all_links = []
    driver.get(url)
    count = 0
    while count < 60:
        response = driver.page_source
        soup = BeautifulSoup(response, "html.parser")
        property_container = soup.find("div", id="property-result")
        if property_container:
            property_items = property_container.find_all("div",
                                                         class_="thumbnail property-thumbnail-feature legacy-reset")
            urls = [f"https://realtylink.org{item.find('a')['href']}" for item in property_items]
            all_links.extend(urls)
            count += len(urls)
        pager_container = driver.find_element(By.ID, "divWrapperPager")
        next_button = pager_container.find_element(By.CLASS_NAME, "next")
        if next_button:
            next_button.click()
        else:
            break
    driver.quit()
    return all_links


def parse_one_property(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    title_container = soup.select_one(
        "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 h1[itemprop='category']")
    if title_container:
        title = title_container.text.strip()
    else:
        title = None

    address_container = soup.select_one(
        "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 div.d-flex.mt-1 h2.pt-1"
    )
    if address_container:
        address = address_container.text.strip()

        address_parts = address.split(',', maxsplit=1)

        region_parts = address_parts[1].strip().split()
        region = ' '.join(region_parts[-2:])
    else:
        address = None
        region = None

    price_container = soup.select_one(
        "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.price-container > div.price.text-right"
    )

    if price_container:
        price = price_container.text.strip()
        price = re.sub(r'[^\d.,]', '', price)
    else:
        price = None

    area = soup.select_one(
        "#overview > div.grid_3 > div.col-lg-12.description > div:nth-child(6) > div:nth-child(1) > div.carac-value > span")
    if area:
        area_string = area.text.strip()
        area = area_string.split()[0]
    else:
        area = None

    rooms = soup.select_one(
        "#overview > div.grid_3 > div.col-lg-12.description > div.row.teaser > div.col-lg-3.col-sm-6.cac")
    if rooms:
        rooms_text = rooms.text.strip()
        rooms = ''.join(filter(str.isdigit, rooms_text))
    else:
        rooms = None

    description_element = soup.find('div', class_='property-description')
    if description_element:
        try:
            description_text = description_element.find('div', itemprop='description').get_text(strip=True)
        except Exception as e:
            print("Помилка:", e)
            description_text = None

    else:
        description_text = None

    script_element = soup.select_one(
        "#overview > div:nth-child(3) > div.thumbnail.last-child.first-child > script")
    if script_element:
        script_content = script_element.string.strip()
        url_pattern = re.compile(r'"(https?://.*?)"')
        link_list = url_pattern.findall(script_content)
    else:
        link_list = []
    data = {
        "link": url,
        "title": title,
        "address": address,
        "region": region,
        "price": price,
        "area": area,
        "rooms": rooms,
        "description": description_text,
        "images": link_list

    }

    return json.dumps(data, ensure_ascii=False)


def main():
    links = get_links()
    parsed_data = [parse_one_property(url) for url in links]
    file_path = "data.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, ensure_ascii=False, indent=4)

    print("Дані успішно записані у файл:", file_path)


if __name__ == '__main__':
    main()
