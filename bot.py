import requests
from environs import Env
from bottle import (
    run,
    post,
    request as bottle_req,
    response as bottle_res,
)


def send_message(params):
    """ Send answer to user via telegram API """

    message_url = f"https://api.telegram.org/bot{env('TOKEN')}/sendMessage"
    requests.post(message_url, json=params)


def get_live_price(crypto):
    """ Get live price of crypto via Coingecko API """

    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": crypto,
        "vs_currencies": 'usd',
        "include_market_cap": 'true',
        "include_24hr_vol": 'true',
        "include_24hr_change": 'true',
    }

    headers = {
        'accept': 'application/json',
    }

    return requests.get(url, params=params, headers=headers).json()


def prepare_data_for_answer(user_message):
    """ Check user message and prepare answer to it """

    if user_message.lower() == '/start':
        return """
Welcome to @livepriceofcryptobot\n
You can see live price of any crypto you want\n
Please send me a name of crypto you want know about\n
For example Litecoin, The sandbox, Binancecoin, and etc...
"""

    crypto = user_message.replace(" ", "-").lower()
    data = get_live_price(crypto)

    if data:
        return f"""        
{user_message.capitalize()}💰\n
        price:  {data[crypto]['usd']}
        market_cap:  {data[crypto]['usd_market_cap']}
        volume(24h):  {data[crypto]['usd_24h_vol']}
        change(24h):  {data[crypto]['usd_24h_change']}\n
@livepriceofcryptobot
        """

    return f"{user_message} is invalid crypto"


@post('/')
def get_message():
    """ Get http post requests from telegram webhook and response it """

    data = bottle_req.json

    params = {
        "text": prepare_data_for_answer(data['message']['text']),
        "chat_id": data['message']['chat']['id'],
    }

    send_message(params)
    return bottle_res


if __name__ == '__main__':
    # This code won't run if this file is imported

    # Environment Variable
    env = Env()
    env.read_env()

    run(host='localhost', port=8080)
