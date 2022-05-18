import time
import requests
import concurrent.futures

from tqdm import tqdm


def get_amount_of_cards():

    url_total_cards = 'https://api.godsunchained.com/v0/proto?page=1&perPage=0'
    total_cards_amount = requests.get(url_total_cards).json()['total']
    return total_cards_amount


def get_cards_list(amount):

    url_all_cards = f'https://api.godsunchained.com/v0/proto?page=1&perPage={amount}'
    cards_dict = requests.get(url_all_cards).json()['records']
    return cards_dict


def save_cards_to_file(cards_list):

    card_ids = {}

    with open('tradeable_cards.txt', 'w', encoding='utf-8') as f:
        for item in cards_list:
            if item['set'] != 'welcome' and item['collectable'] is not False:
                card_ids[item['id']] = item['name']
                f.write(str(item) + "\n")

    return card_ids


def get_crypto_prices():

    currencies_url = 'https://api.coingecko.com/api/v3/simple/price?ids=gods-unchained,ethereum&vs_currencies=usd'

    currencies = requests.get(currencies_url).json()

    currency_eth = currencies['ethereum']['usd']
    currency_gods = currencies['gods-unchained']['usd']

    return currency_eth, currency_gods


def get_cards_prices(card_id, eth, gods):

    prices_eth = []
    prices_gods = []

    urls = {
        'eth': f'https://api.x.immutable.com/v1/orders?buy_token_type=ETH&direction=asc&include_fees=true&order_by=buy_quantity&page_size=200&sell_metadata=%7B%22proto%22%3A%5B%22{card_id}%22%5D%2C%22quality%22%3A%5B%22Meteorite%22%5D%7D&sell_token_address=0xacb3c6a43d15b907e8433077b6d38ae40936fe2c&status=active',
        'gods': f'https://api.x.immutable.com/v1/orders?buy_token_address=0xccc8cb5229b0ac8069c51fd58367fd1e622afd97&direction=asc&include_fees=true&order_by=buy_quantity&page_size=200&sell_metadata=%7B%22proto%22%3A%5B%22{card_id}%22%5D%2C%22quality%22%3A%5B%22Meteorite%22%5D%7D&sell_token_address=0xacb3c6a43d15b907e8433077b6d38ae40936fe2c&status=active'
    }

    headers = {"Accept": "*/*"}

    for k, v in urls.items():
        complete = False

        while complete is False:

            orders = requests.get(v, headers=headers)

            if orders.reason == 'OK':
                orders = orders.json()
                complete = True

                if orders['result']:
                    orders = orders['result']
                elif orders['remaining'] == 0:
                    return None, None

                for order in orders:
                    if k == 'eth':
                        prices_eth.append(round(float(order['buy']['data']['quantity_with_fees']) / 10 ** 18 * eth, 2))
                    elif k == 'gods':
                        prices_gods.append(round(float(order['buy']['data']['quantity_with_fees']) / 10 ** 18 * gods, 2))

            elif orders.reason == 'Too Many Requests':
                time.sleep(60)
            else:
                print(orders.reason)
                return None, None

    return sorted(prices_eth), sorted(prices_gods)


def split_cards_to_chunks(dict_of_cards):

    return [{k: dict_of_cards[k]} for k in dict_of_cards.keys()]


def calculate_profit(card_id, card_name):

    card_prices_in_eth, card_prices_in_gods = get_cards_prices(card_id, eth_price, gods_price)

    if card_prices_in_eth and card_prices_in_gods:
        profit_usd = round(card_prices_in_eth[0] - card_prices_in_gods[0], 2)
    else:
        return

    if profit_usd >= 0:
        profit_crypto = 'ETH'
        profit_rate = round(card_prices_in_eth[0] / card_prices_in_gods[0] * 100 - 100, 2)
    else:
        profit_crypto = 'GODS'
        profit_rate = round(card_prices_in_gods[0] / card_prices_in_eth[0] * 100 - 100, 2)

    return [card_name, profit_crypto, abs(profit_usd), profit_rate, card_prices_in_eth[0], card_prices_in_gods[0]]


def calculate_top_profit(card_dict):

    for card_id, card_name in card_dict.items():
        card_profit = calculate_profit(card_id, card_name)

        if card_profit:
            return card_profit


def run_multiple_requests(chunks_list):

    profit_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e:
        fut = [e.submit(calculate_top_profit, card) for card in chunks_list]
        for r in tqdm(concurrent.futures.as_completed(fut), total=len(chunks_list)):
            profit_list.append(r.result())

    return profit_list


def get_top_profit(list_of_prices):

    profit_eth = []
    profit_gods = []

    for item in list_of_prices:
        if item:
            if item[1] == 'ETH':
                profit_eth.append(item)
            elif item[1] == 'GODS':
                profit_gods.append(item)
        else:
            continue

    profit_eth_by_rate = []
    profit_gods_by_rate = []

    for card in sorted(profit_eth, key=lambda x: x[3], reverse=True):
        profit_eth_by_rate.append(f'[{card[0]}]: [Profit in {card[1]}: +{card[3]}% ({card[2]}$)], [ETH: {card[4]}$ vs GODS: {card[5]}$]')

    for card in sorted(profit_gods, key=lambda x: x[3], reverse=True):
        profit_gods_by_rate.append(f'[{card[0]}]: [Profit in {card[1]}: +{card[3]}% ({card[2]}$)], [GODS: {card[5]}$ vs ETH: {card[4]}$]')

    return profit_eth_by_rate, profit_gods_by_rate


def write_profit_to_file(eth, gods):

    with open('profit_eth_by_rate.txt', 'w', encoding='utf-8') as f:
        for item in eth:
            f.write(str(item) + '\n')

    with open('profit_gods_by_rate.txt', 'w', encoding='utf-8') as f:
        for item in gods:
            f.write(str(item) + '\n')


if __name__ == '__main__':

    amount_of_cards = get_amount_of_cards()

    all_cards = get_cards_list(amount_of_cards)

    tradeable_cards = save_cards_to_file(all_cards)

    eth_price, gods_price = get_crypto_prices()

    chunks = split_cards_to_chunks(tradeable_cards)

    profit = run_multiple_requests(chunks)

    eth_profit, gods_profit = get_top_profit(profit)

    write_profit_to_file(eth_profit, gods_profit)
