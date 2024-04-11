import requests
from bs4 import BeautifulSoup

url = "https://realtylink.org/en/properties~for-rent"

response = requests.get(url)

if response.status_code == 200:

    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    listings = soup.find_all("div", class_="listing-card")
    property_items = soup.find_all("div", class_="property-thumbnail-item")
    print( property_items )

else:
    pass

