import re
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

COUNTRY_DICT = {
    'au': '.com.au',
    'at': '.at',
    'be': '.be',
    'ca': '.ca',
    'ch': '.ch',
    'de': '.de',
    'es': '.es',
    'fr': '.fr',
    'hk': '.com.hk',
    'ie': '.ie',
    'it': '.it',
    'my': '.com.my',
    'nl': '.nl',
    'nz': '.co.nz',
    'ph': '.ph',
    'pl': '.pl',
    'sg': '.com.sg',
    'uk': '.co.uk',
    'us': '.com',
}

CONDITION_DICT = {
    'all': '',
    'new': '&LH_ItemCondition=1000',
    'opened': '&LH_ItemCondition=1500',
    'refurbished': '&LH_ItemCondition=2500',
    'used': '&LH_ItemCondition=3000'
}

def get_item_info():
    """
    Get price, shipping price, and total for a given item and condition entered by the user.

    Returns:
        dict: A dictionary containing price, shipping price, and total.
    """
    # Get input from the user
    item_name = input("Enter the item name: ")
    condition = input("Enter the condition type (all/new/opened/refurbished/used): ").lower()
    country = 'us'  # Default country is 'us', you can modify this if needed

    if condition not in CONDITION_DICT:
        raise ValueError('Condition not supported, please use one of the following: ' + ', '.join(CONDITION_DICT.keys()))

    # Construct the URL for eBay search
    url = _construct_url(item_name, country, condition)
    # Get the HTML content from the URL
    soup = _get_html(url)

    # Parse prices from the HTML content
    data = _parse_prices(soup)

    # Compute average price and shipping
    avg_price = round(_average(data['price_list']), 2)
    avg_shipping = round(_average(data['shipping_list']), 2)

    # Return dictionary with price, shipping, and total
    return {'price': avg_price, 'shipping': avg_shipping, 'total': round(avg_price + avg_shipping, 2)}

def _construct_url(query, country, condition=''):
    """
    Construct the eBay search URL.

    Args:
        query (str): The search query.
        country (str): The country code.
        condition (str, optional): The condition of the item. Defaults to ''.

    Returns:
        str: The constructed URL.
    """
    base_url = f'https://www.ebay{COUNTRY_DICT[country]}/sch/i.html?_from=R40&_nkw='
    parsed_query = urllib.parse.quote(query).replace('%20', '+')
    return base_url + parsed_query + CONDITION_DICT[condition]

def _get_html(url):
    """
    Get HTML content from the provided URL.

    Args:
        url (str): The URL to fetch HTML content from.

    Returns:
        BeautifulSoup: Parsed HTML content.
    """
    request = urllib.request.urlopen(url)
    return BeautifulSoup(request.read(), 'html.parser')

def _parse_prices(soup):
    """
    Parse prices and shipping prices from HTML content.

    Args:
        soup (BeautifulSoup): Parsed HTML content.

    Returns:
        dict: A dictionary containing price list and shipping list.
    """
    raw_price_list = [price.get_text(strip=True) for price in soup.find_all(class_="s-item__price")]
    raw_shipping_list = [item.get_text(strip=True) for item in soup.find_all(class_="s-item__shipping s-item__logisticsCost")]

    price_list = [_parse_raw_price(raw_price) for raw_price in raw_price_list if raw_price]
    shipping_list = [_parse_raw_price(raw_shipping) if raw_shipping else 0 for raw_shipping in raw_shipping_list]

    return {'price_list': price_list, 'shipping_list': shipping_list}

def _parse_raw_price(string):
    """
    Parse raw price string into float.

    Args:
        string (str): Raw price string.

    Returns:
        float: Parsed price.
    """
    parsed_price = re.search(r'(\d+(\.\d+)?)', string.replace(',', '.'))
    return float(parsed_price.group()) if parsed_price else None

def _average(number_list):
    """
    Compute the average of a list of numbers.

    Args:
        number_list (list): List of numbers.

    Returns:
        float: Average of the numbers.
    """
    if number_list:
        # Filter out None values
        valid_numbers = [num for num in number_list if num is not None]
        if valid_numbers:
            return sum(valid_numbers) / len(valid_numbers)
    return 0

if __name__ == "__main__":
    item_info = get_item_info()
    print(item_info)