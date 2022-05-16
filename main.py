import time
import requests
import concurrent.futures

from tqdm import tqdm
from datetime import datetime


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


def get_eth_prices(card_id, eth):
    prices = []

    url = f'https://api.x.immutable.com/v1/orders?buy_token_type=ETH&direction=asc&include_fees=true&order_by=buy_quantity&page_size=200&sell_metadata=%7B%22proto%22%3A%5B%22{card_id}%22%5D%2C%22quality%22%3A%5B%22Meteorite%22%5D%7D&sell_token_address=0xacb3c6a43d15b907e8433077b6d38ae40936fe2c&status=active'
    headers = {"Accept": "*/*"}

    complete = False

    while complete is False:

        orders = requests.get(url, headers=headers)

        if orders.reason == 'OK':
            orders = orders.json()
            complete = True

            if orders['result']:
                orders = orders['result']
            elif orders['remaining'] == 0:
                return
            elif orders['remaining'] != 0:
                print(orders)

            for order in orders:
                prices.append(round(float(order['buy']['data']['quantity_with_fees']) / 10 ** 18 * eth, 2))

            return sorted(prices)
        elif orders.reason == 'Too Many Requests':
            time.sleep(60)
        else:
            print(orders.reason)
            return


def get_gods_prices(card_id, gods):
    prices = []

    url = f'https://api.x.immutable.com/v1/orders?buy_token_address=0xccc8cb5229b0ac8069c51fd58367fd1e622afd97&direction=asc&include_fees=true&order_by=buy_quantity&page_size=200&sell_metadata=%7B%22proto%22%3A%5B%22{card_id}%22%5D%2C%22quality%22%3A%5B%22Meteorite%22%5D%7D&sell_token_address=0xacb3c6a43d15b907e8433077b6d38ae40936fe2c&status=active'
    headers = {"Accept": "*/*"}

    complete = False

    while complete is False:

        orders = requests.get(url, headers=headers)

        if orders.reason == 'OK':
            orders = orders.json()
            complete = True

            if orders['result']:
                orders = orders['result']
            elif orders['remaining'] == 0:
                return
            elif orders['remaining'] != 0:
                print(orders)

            for order in orders:
                prices.append(round(float(order['buy']['data']['quantity_with_fees']) / 10 ** 18 * gods, 2))

            return sorted(prices)
        elif orders.reason == 'Too Many Requests':
            time.sleep(60)
        else:
            print(orders.reason)
            return


def calculate_profit(card_id, card_name):

    card_prices_in_eth = get_eth_prices(card_id, eth_price)
    card_prices_in_gods = get_gods_prices(card_id, gods_price)

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

    # print(f'[{card_name}]: [Profit in {profit_crypto}: +{abs(profit_usd)}$ ({profit_rate}%)], ETH: {card_prices_in_eth[0]}$ vs GODS: {card_prices_in_gods[0]}$')

    return [card_name, profit_crypto, abs(profit_usd), profit_rate, card_prices_in_eth[0], card_prices_in_gods[0]]


def get_top_profit(list_of_prices):
    # if list_of_prices is None:
    #     return

    profit_eth = []
    profit_gods = []

    for item in list_of_prices:
        if item is not None:
            if item[1] == 'ETH':
                profit_eth.append(item)
            elif item[1] == 'GODS':
                profit_gods.append(item)
        else:
            continue

    profit_eth_by_usd = []
    profit_eth_by_rate = []

    profit_gods_by_usd = []
    profit_gods_by_rate = []

    for card in sorted(profit_eth, key=lambda x: x[2], reverse=True)[:10]:
        profit_eth_by_usd.append(f'[{card[0].ljust(20)}]: [Profit in {card[1]}: +{card[2]}$ ({card[3]}%)], [ETH: {card[4]}$ vs GODS: {card[5]}$]')
    for card in sorted(profit_eth, key=lambda x: x[3], reverse=True)[:10]:
        profit_eth_by_rate.append(f'[{card[0].ljust(20)}]: [Profit in {card[1]}: +{card[3]}% ({card[2]}$)], [ETH: {card[4]}$ vs GODS: {card[5]}$]')

    for card in sorted(profit_gods, key=lambda x: x[2], reverse=True)[:10]:
        profit_gods_by_usd.append(f'[{card[0].ljust(20)}]: [Profit in {card[1]}: +{card[2]}$ ({card[3]}%)], [GODS: {card[5]}$ vs ETH: {card[4]}$]')
    for card in sorted(profit_gods, key=lambda x: x[3], reverse=True)[:10]:
        profit_gods_by_rate.append(f'[{card[0].ljust(20)}]:' + f'[Profit in {card[1]}: +{card[3]}% ({card[2]}$)], [GODS: {card[5]}$ vs ETH: {card[4]}$]')

    with open('profit_eth_by_usd.txt', 'w', encoding='utf-8') as f:
        for item in profit_eth_by_usd:
            f.write(str(item) + '\n')

    with open('profit_eth_by_rate.txt', 'w', encoding='utf-8') as f:
        for item in profit_eth_by_rate:
            f.write(str(item) + '\n')

    with open('profit_gods_by_usd.txt', 'w', encoding='utf-8') as f:
        for item in profit_gods_by_usd:
            f.write(str(item) + '\n')

    with open('profit_gods_by_rate.txt', 'w', encoding='utf-8') as f:
        for item in profit_gods_by_rate:
            f.write(str(item) + '\n')


if __name__ == '__main__':
    start_time = datetime.now()
    print('Start time:', start_time)
    amount_of_cards = get_amount_of_cards()
    all_cards = get_cards_list(amount_of_cards)
    cards = save_cards_to_file(all_cards)
    eth_price, gods_price = get_crypto_prices()

    profit = []

    chunks = [{k: cards[k]} for k in cards.keys()]

    def calculate_top_profit(card_dict):
        time.sleep(2)
        for card_id, card_name in card_dict.items():
            card_profit = calculate_profit(card_id, card_name)

            if card_profit:
                return card_profit


    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as e:
        fut = [e.submit(calculate_top_profit, card) for card in chunks]
        for r in tqdm(concurrent.futures.as_completed(fut), total=len(chunks)):
            profit.append(r.result())

    get_top_profit(profit)
    print('End time:', datetime.now())
    print('Total time:', datetime.now() - start_time)
