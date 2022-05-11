import requests
import pprint


# get total amount of cards
def get_amount_of_cards():
    url_total_cards = 'https://api.godsunchained.com/v0/proto?page=1&perPage=0'
    total_cards_amount = requests.get(url_total_cards).json()['total']
    return total_cards_amount


# get all cards
def get_cards_list(amount):
    url_all_cards = f'https://api.godsunchained.com/v0/proto?page=1&perPage={amount}'
    all_cards = requests.get(url_all_cards).json()['records']
    return all_cards


# save cards to file
def save_cards_to_file(cards_list):
    with open('cards.txt', 'w', encoding='utf-8') as f:
        for item in cards_list:
            if item['set'] != 'welcome':
                f.write(str(item) + "\n")


def get_crypto_prices():
    CURRENCIES_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=gods-unchained,ethereum&vs_currencies=usd'

    currencies = requests.get(CURRENCIES_URL).json()

    currency_eth = currencies['ethereum']['usd']
    currency_gods = currencies['gods-unchained']['usd']

    return currency_eth, currency_gods


def get_eth_prices():
    prices = []

    url = 'https://api.x.immutable.com/v1/orders?buy_token_type=ETH&direction=asc&include_fees=true&order_by=buy_quantity&page_size=200&sell_metadata=%7B%22proto%22%3A%5B%221122%22%5D%2C%22quality%22%3A%5B%22Meteorite%22%5D%7D&sell_token_address=0xacb3c6a43d15b907e8433077b6d38ae40936fe2c&status=active'
    headers = {"Accept": "*/*"}

    orders = requests.get(url, headers=headers).json()['result']

    for order in orders:
        prices.append(float(order['buy']['data']['quantity_with_fees']) / 10 ** 18)
        # price = float(i['buy']['data']['quantity_with_fees']) / 10 ** 18
        # print(f'{price * currency_eth:.2f}$ USD, {price:.6f} ETH')

    return sorted(prices)


if __name__ == '__main__':
    amount_of_cards = get_amount_of_cards()
    all_cards = get_cards_list(amount_of_cards)
    save_cards_to_file(all_cards)
    prices = get_eth_prices()
    print(prices)