import requests

from tqdm import tqdm

# get total amount of cards
def get_amount_of_cards():
    url_total_cards = 'https://api.godsunchained.com/v0/proto?page=1&perPage=0'
    total_cards_amount = requests.get(url_total_cards).json()['total']
    return total_cards_amount


# get all cards
def get_cards_list(amount):
    url_all_cards = f'https://api.godsunchained.com/v0/proto?page=1&perPage={amount}'
    cards_dict = requests.get(url_all_cards).json()['records']
    return cards_dict


# save cards to file
def save_cards_to_file(cards_list):
    card_ids = {}

    with open('cards.txt', 'w', encoding='utf-8') as f:
        for item in cards_list:
            if item['set'] != 'welcome':
                card_ids[item['id']] = item['name']
                f.write(str(item) + "\n")

    return card_ids


def get_crypto_prices():
    currencies_url = 'https://api.coingecko.com/api/v3/simple/price?ids=gods-unchained,ethereum&vs_currencies=usd'

    currencies = requests.get(currencies_url).json()

    currency_eth = currencies['ethereum']['usd']
    currency_gods = currencies['gods-unchained']['usd']

    return currency_eth, currency_gods


def get_eth_prices(card_id, eth):
    prices = []

    url = f'https://api.x.immutable.com/v1/orders?buy_token_type=ETH&direction=asc&include_fees=true&order_by=buy_quantity&page_size=200&sell_metadata=%7B%22proto%22%3A%5B%22{card_id}%22%5D%2C%22quality%22%3A%5B%22Meteorite%22%5D%7D&sell_token_address=0xacb3c6a43d15b907e8433077b6d38ae40936fe2c&status=active'
    headers = {"Accept": "*/*"}

    orders = requests.get(url, headers=headers).json()['result']

    for order in orders:
        prices.append(round(float(order['buy']['data']['quantity_with_fees']) / 10 ** 18 * eth, 2))

    return sorted(prices)


def get_gods_prices(card_id, gods):
    prices = []

    url = f'https://api.x.immutable.com/v1/orders?buy_token_address=0xccc8cb5229b0ac8069c51fd58367fd1e622afd97&direction=asc&include_fees=true&order_by=buy_quantity&page_size=200&sell_metadata=%7B%22proto%22%3A%5B%22{card_id}%22%5D%2C%22quality%22%3A%5B%22Meteorite%22%5D%7D&sell_token_address=0xacb3c6a43d15b907e8433077b6d38ae40936fe2c&status=active'
    headers = {"Accept": "*/*"}

    orders = requests.get(url, headers=headers).json()['result']

    for order in orders:
        prices.append(round(float(order['buy']['data']['quantity_with_fees']) / 10 ** 18 * gods, 2))

    return sorted(prices)


def calculate_profit(cards_dict):
    profit = []
    profit_eth = []
    profit_gods = []

    for card_id, card_name in tqdm(cards_dict.items()):

        card_prices_in_eth = get_eth_prices(card_id, eth_price)
        card_prices_in_gods = get_gods_prices(card_id, gods_price)

        if card_prices_in_eth and card_prices_in_gods:
            profit_usd = round(card_prices_in_eth[0] - card_prices_in_gods[0], 2)
        else:
            continue

        if profit_usd >= 0:
            profit_crypto = 'ETH'
            profit_rate = round(card_prices_in_eth[0] / card_prices_in_gods[0] * 100 - 100, 2)
        else:
            profit_crypto = 'GODS'
            profit_rate = round(card_prices_in_gods[0] / card_prices_in_eth[0] * 100 - 100, 2)

        profit.append([card_name, profit_crypto, abs(profit_usd), profit_rate, card_prices_in_eth[0], card_prices_in_gods[0]])
        # print(f'[{card_name}]: [Profit in {profit_crypto}: +{abs(profit_usd)}$ ({profit_rate}%)], ETH: {card_prices_in_eth[0]}$ vs GODS: {card_prices_in_gods[0]}$')

    for item in profit:
        if item[1] == 'ETH':
            profit_eth.append(item)
        elif item[1] == 'GODS':
            profit_gods.append(item)

    profit_eth_by_usd = sorted(profit_eth, key=lambda x: x[2], reverse=True)
    profit_eth_by_rate = sorted(profit_eth, key=lambda x: x[3], reverse=True)

    profit_gods_by_usd = sorted(profit_gods, key=lambda x: x[2], reverse=True)
    profit_gods_by_rate = sorted(profit_gods, key=lambda x: x[3], reverse=True)

    # profit_eth_by_usd = f'[{profit_eth_by_usd[0]}]: [Profit in {profit_eth_by_usd[1]}: +{profit_eth_by_usd[2]}$ ({profit_eth_by_usd[3]}%)], ETH: {profit_eth_by_usd[4]}$ vs GODS: {profit_eth_by_usd[5]}$'

    with open('profit_eth_by_usd.txt', 'w', encoding='utf-8') as f:
        f.write(str(profit_eth_by_usd) + '\n')

    with open('profit_eth_by_rate.txt', 'w', encoding='utf-8') as f:
        f.write(str(profit_eth_by_rate) + '\n')

    with open('profit_gods_by_usd.txt', 'w', encoding='utf-8') as f:
        f.write(str(profit_gods_by_usd) + '\n')

    with open('profit_gods_by_rate.txt', 'w', encoding='utf-8') as f:
        f.write(str(profit_gods_by_rate) + '\n')

if __name__ == '__main__':
    amount_of_cards = get_amount_of_cards()
    all_cards = get_cards_list(amount_of_cards)
    cards = save_cards_to_file(all_cards)
    eth_price, gods_price = get_crypto_prices()
    calculate_profit(cards)
    # calculate_profit({1393: 'Volcanic Watcher', 1441: "Ludia's Dedicant", 1467: 'Blood and Bone', 1468: 'Starving Sabertooth'})
