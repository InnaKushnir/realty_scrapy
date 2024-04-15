import re
from telnetlib import EC
from time import sleep
from wsgiref import headers
import json

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument('disable-extensions')

driver = webdriver.Chrome(options=options)

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
            property_items = property_container.find_all("div", class_="thumbnail property-thumbnail-feature legacy-reset")
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
    return all_links[:60]


def parse_one_property(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    title_container = soup.select_one(
        "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 h1[itemprop='category']")
    if title_container:
        title = title_container.text.strip()
    else:
        title = "Назву не вдалося знайти"

    address_container = soup.select_one(
        "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 div.d-flex.mt-1 h2.pt-1"
    )
    address = address_container.text.strip()

    address_parts = address.split(',', maxsplit=1)

    region_parts = address_parts[1].strip().split()
    region = ' '.join(region_parts[-2:])

    price_container = soup.select_one(
        "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.price-container > div.price.text-right"
    )

    if price_container:
        price = price_container.text.strip()
        price = re.sub(r'[^\d.,]', '', price)
    else:
        price = "Ціну не вдалося знайти"

    area = soup.select_one(
        "#overview > div.grid_3 > div.col-lg-12.description > div:nth-child(6) > div:nth-child(1) > div.carac-value > span")
    area_string = area.text.strip()
    area = area_string.split()[0]

    rooms = soup.select_one("#overview > div.grid_3 > div.col-lg-12.description > div.row.teaser > div.col-lg-3.col-sm-6.cac")
    rooms_text = rooms.text.strip()
    rooms = ''.join(filter(str.isdigit, rooms_text))

    description_element = soup.find('div', class_='property-description')
    try:
        description_text = description_element.find('div', itemprop='description').get_text(strip=True)
    except AttributeError as e:
        print("Помилка при отриманні опису:", e)
        description_text = None

    # meta_tags = soup.find_all('meta')
    # print(meta_tags)
    # for tag in meta_tags:
    #     if tag.get('name') == 'last-modified':
    #         last_modified = tag.get('content')
    #         print('Дата останнього оновлення:', last_modified)
    #         break

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        driver.execute_script('''
            var carousel = document.querySelector('.carousel ul');
            if (carousel) {
                var liTags = carousel.querySelectorAll('li');
                liTags.forEach(li => {
                    li.style.display = 'block';
                });
            }
            ''')

        wait = WebDriverWait(driver, 10)
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                        "#overview > div:nth-child(3) > div.thumbnail.last-child.first-child > div > div.photo-buttons.legacy-reset > button")))

        button.click()
        sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        link_list = []
        carousel = soup.find("div", class_="carousel")
        if carousel:
            li_tags = carousel.find_all("li")
            for li in li_tags:
                img_tag = li.find("img")
                if img_tag:
                    src = img_tag.get("src")
                    link_list.append(src)

        container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              "body > main > div.photoViewer.photoViewerOnPage.show #gallery > div.footer > div > div > div:nth-child(3)"))
        )
        driver.execute_script("arguments[0].style.touchAction = 'auto';", container)
        print(container)
        next_button = container.find_element(By.CSS_SELECTOR, "span.nav-next")
        driver.execute_script("arguments[0].style.touchAction = 'auto';", next_button)
        print(next_button)
        next_button.click()



        driver.execute_script("arguments[0].style.touchAction = 'auto';", next_button)


        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        link_list_next = []
        carousel = soup.find("div", class_="carousel")
        print(carousel)
            # if carousel:
            #     li_tags = carousel.find_all("li")
            #     for li in li_tags:
            #         img_tag = li.find("img")
            #         if img_tag:
            #             src = img_tag.get("src")
            #             link_list_next.append(src)
            #
            # if len(link_list_next) == len(link_list):


            # Оновіть попередній список зображень
            # previous_link_list = link_list
        driver.quit()
        # img_element = driver.find_element(By.ID, "fullImg")
        # photo_url = img_element.get_attribute("src")
        # link_list = []
        # link_list.append(photo_url)
        #
        # next_arrow = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
        #                                                     "#gallery > div.image-wrapper > div.wrap.activateNextArrow > div.spinner-border.text-primary")))
        # next_arrow.click()
        # gallery > div.image-wrapper > div.wrap.activateNextArrow
        # wait.until(EC.visibility_of_element_located((By.ID, "fullImg")))
        #
        # full_img_element = driver.find_element(By.ID, "fullImg")
        # ActionChains(driver).double_click(full_img_element).perform()
        #
        # photo_url = full_img_element.get_attribute("src")
        # link_list.append(photo_url)


    # gallery > div.image-wrapper > div.wrap.activateNextArrow > div.logo
    except Exception as e:
        print("Помилка:", e)
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
    print(data)
    return json.dumps(data, ensure_ascii=False)


def main():
    links = get_links()
    parsed_data = [parse_one_property(url) for url in links[:1]]
    print(parsed_data)


if __name__ == '__main__':
    main()
# driver.get(url)
#
# wait = WebDriverWait(driver, 10)
# wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.thumbnail.property-thumbnail-feature.legacy-reset")))
#
# property_containers = driver.find_elements(By.CSS_SELECTOR, "div.thumbnail.property-thumbnail-feature.legacy-reset")
#
#
# for container in property_containers:
#     container.click()
#     sleep(1)
#
#     wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.thumbnail.property-thumbnail-feature.legacy-reset")))
#     property_containers = driver.find_elements(By.CSS_SELECTOR, "div.thumbnail.property-thumbnail-feature.legacy-reset")
#
# driver.quit()

# if property_container:
#     property_items = property_container.find_all("div", class_="thumbnail property-thumbnail-feature legacy-reset")
#
#     json_objects = []
#
#     for item in property_items:
#         property_link = item.find("a")["href"]
#
#         address_container = item.select_one(
#             "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 > div.d-flex.mt-1 h2.pt-1")
#         if address_container:
#             address = address_container.get_text.strip()
#         else:
#             address = "Адресу не вдалося знайти"
#
#         json_object = {
#             "link": property_link,
#             "title": "Назва оголошення",
#             "region": "Регіон",
#             "address": address,
#             "description": "Опис оголошення",
#             "images": ["https://link-to-image1.jpg", "https://link-to-image2.jpg"],
#             "publication_date": "2024-04-12",
#             "price": 1000,
#             "rooms": 3,
#             "area": 120
#         }
#
#         json_objects.append(json_object)
#
#     for obj in json_objects:
#         print(json.dumps(obj, ensure_ascii=False, indent=2))
# else:
#     print("Сталася помилка при отриманні сторінки:", response.status_code)
