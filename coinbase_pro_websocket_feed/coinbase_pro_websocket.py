#  Drakkar-Software OctoBot-Tentacles
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import octobot_trading.exchanges as exchanges
from octobot_trading.enums import WebsocketFeeds as Feeds
import tentacles.Trading.Exchange.coinbase_pro.coinbase_pro_exchange as coinbase_pro_exchange


class CoinbaseProCCXTWebsocketConnector(exchanges.CCXTWebsocketConnector):
    EXCHANGE_FEEDS = {
        Feeds.TRADES: True,
        Feeds.KLINE: Feeds.UNSUPPORTED.value,
        Feeds.TICKER: True,
        Feeds.CANDLE: Feeds.UNSUPPORTED.value,
    }

    @classmethod
    def get_name(cls):
        return coinbase_pro_exchange.CoinbasePro.get_name()

    def get_adapter_class(self, adapter_class):
        return coinbase_pro_exchange.CoinbaseProCCXTAdapter

import hashlib
import hmac
import time

import websocket # find an asyncio websocket client
import json


def add_signature_ws(message:dict, secret:str):
    nonce = int(time.time())
    to_sign = f"{nonce}{message['channel']}{','.join(message['product_ids'])}"
    print(to_sign)
    signature = hmac.new(secret.encode('utf-8'), to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    message['signature'] = signature
    message['timestamp'] = str(nonce)

    return message

async def yield_prices(sym:str):

    product_ids = [f"{sym}-USD"]
    ticker_batch = {
        "type": "subscribe",
        "product_ids": product_ids,
        "channel": "ticker_batch",
        'api_key' : SecretManager.get('COINBASE_API_KEY')
    }
    message = add_signature_ws(ticker_batch, SecretManager.get('COINBASE_API_SECRET'))

    ws = await websocket.connect("wss://advanced-trade-ws.coinbase.com")
    await ws.send(json.dumps(message))

    while True:
        response = await ws.recv()
        data = json.loads(response)
        yield data
