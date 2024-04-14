from telnetlib import EC
from time import sleep
from wsgiref import headers

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


def get_links() -> list:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        property_container = soup.find("div", id="property-result")

        if property_container:
            property_items = property_container.find_all("div",
                                                         class_="thumbnail property-thumbnail-feature legacy-reset")

            urls = []

            for item in property_items:
                property_url = item.find("a")["href"]
                full_url = f"https://realtylink.org{property_url}"
                print(full_url)
                urls.append(full_url)

            return urls


def parse_page(urls):
    for url in urls:
        parse_one_property(url)


def parse_one_property(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    title_container = soup.select_one(
        "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 h1[itemprop='category']")
    if title_container:
        title = title_container.text.strip()
    else:
        title = "Назву не вдалося знайти"
    print(title)
    address_container = soup.select_one(
        "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.col.text-left.pl-0 div.d-flex.mt-1 h2.pt-1"
    )
    address = address_container.text.strip()

    address_parts = address.split(',', maxsplit=1)

    region_parts = address_parts[1].strip().split()
    region = ' '.join(region_parts[-2:])
    print(address)
    print(region)
    price_container = soup.select_one(
        "#overview > div.row.property-tagline > div.d-none.d-sm-block.house-info > div > div.price-container > div.price.text-right"
    )

    if price_container:
        price = price_container.text.strip()
    else:
        price = "Ціну не вдалося знайти"

    print(price)

    description_element = soup.find('div', class_='property-description')

    description_text = description_element.find('div', itemprop='description').get_text(strip=True)

    print(description_text)


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
        print(link_list)
        while True:
            container = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "#gallery > div.footer > div > div > div:nth-child(3)"))
            )

            driver.execute_script("arguments[0].style.display = 'block';", container)

            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#gallery > div.footer > div > div > div:nth-child(3) .nav-next"))
            )
            print(next_button)
            next_button.click()

            sleep(1)

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
            break

            # Оновіть попередній список зображень
            previous_link_list = link_list
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
    finally:
        driver.quit()

    return (response.status_code)


def main():
    links = get_links()
    parse_page(links)


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
