# -*- coding: utf-8 -*-
# #!/usr/bin/python

import json
import websocket
import time
import ssl
import hmac
import hashlib
import uuid
from datetime import datetime
from sortedcontainers import SortedDict

url = 'wss://api.bitbay.net/websocket/'


class Bitbay(object):
    def __init__(self, ws_type=['ob'], api_key=None, api_secret=None):
        self.name = 'bitbay'
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws = None
        self.ticker = {}
        self.asset_mapping = {}
        self.tag_mapping = {}
        self.ws_type = ws_type
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.ob_depth = 10
        self.seqNo = 0

    def on_message(self, ws, message):
        msg = json.loads(message)
        snd_ts = datetime.utcnow()

        action = msg['action']
        if action == 'proxy-response':
            # ob snapshot or ticker snapshot
            self.seqNo = int(msg['body']['seqNo'])

            if 'sell' in msg['body']:
                # ob snapshot
                for item in msg['body']['buy']:
                    price = item['ra']
                    size = item['ca']
                    self.bids[float(price)] = float(size)
                for item in msg['body']['sell']:
                    price = item['ra']
                    size = item['ca']
                    self.asks[float(price)] = float(size)
                # print(self.bids, self.asks)
                bids = [{'price': price, 'size': self.bids[price]} for price in list(reversed(self.bids))[:self.ob_depth]]
                asks = [{'price': price, 'size': self.asks[price]} for price in list(self.asks)[:self.ob_depth]]
                ob_objs = {'bids': bids, 'asks': asks, 'snd_ts': snd_ts, 'api_ts': snd_ts, 'exchange': self.name, 'pair': 'BTC-PLN'}
                print(ob_objs)
            else:
                # ticker snapshot
                pass
        elif action == 'push':
            seqNo = msg['seqNo']
            if 'trading/orderbook-limited' in msg['topic']:
                if seqNo == self.seqNo + 1:
                    changes = msg['message']['changes']
                    for change in changes:
                        entryType = change['entryType']
                        action = change['action']
                        rate = change['rate']

                        if entryType == 'Buy':
                            target = self.bids
                        else:
                            target = self.asks

                        if action == 'remove':
                            target.pop(float(rate), None)
                        else:   # update
                            new_size = change['state']['ca']
                            target[float(rate)] = float(new_size)

                    # print(self.bids, self.asks)
                    bids = [{'price': price, 'size': self.bids[price]} for price in list(reversed(self.bids))[:self.ob_depth]]
                    asks = [{'price': price, 'size': self.asks[price]} for price in list(self.asks)[:self.ob_depth]]
                    ob_objs = {'bids': bids, 'asks': asks, 'snd_ts': snd_ts, 'api_ts': snd_ts, 'exchange': self.name, 'pair': 'BTC-PLN'}
                    print(ob_objs)
                    self.seqNo = seqNo
                else:
                    print("======== Invalid SeqNo ")
                    print("======== Trigger to fetch the new snapshot ")
                    ws.send(json.dumps({"requestId": str(uuid.uuid4()), "action": "proxy", "module": "trading", "path": "orderbook-limited/btc-pln/10"}))
            elif action == 'push':
                seqNo = msg['seqNo']
                if 'trading/orderbook-limited' in msg['topic']:
                    if seqNo == self.seqNo + 1:
                        changes = msg['message']['changes']
                        for change in changes:
                            entryType = change['entryType']
                            action = change['action']
                            rate = change['rate']

                            if entryType == 'Buy':
                                target = self.bids
                            else:
                                target = self.asks

                            if action == 'remove':
                                target.pop(float(rate), None)
                            else:  # update
                                new_size = change['state']['ca']
                                target[float(rate)] = float(new_size)

                        # print(self.bids, self.asks)
                        bids = [{'price': price, 'size': self.bids[price]} for price in list(reversed(self.bids))[:self.ob_depth]]
                        asks = [{'price': price, 'size': self.asks[price]} for price in list(self.asks)[:self.ob_depth]]
                        ob_objs = {'bids': bids, 'asks': asks, 'snd_ts': snd_ts, 'api_ts': snd_ts, 'exchange': self.name, 'pair': 'BTC-PLN'}
                        print(ob_objs)
                        self.seqNo = seqNo
                    else:
                        print("======== Invalid SeqNo ")
                        print("======== Trigger to fetch the new snapshot ")
                        ws.send(json.dumps({"requestId": str(uuid.uuid4()), "action": "proxy", "module": "trading", "path": "orderbook-limited/btc-pln/10"}))
                elif 'balances/balance' in msg['topic']:
                    print(msg['message'])
                    availableFunds = msg['message']['availableFunds']
                    totalFunds = msg['message']['totalFunds']
                    lockedFunds = msg['message']['lockedFunds']
                    print(availableFunds, totalFunds, lockedFunds)

    def on_error(self, ws, error):
        print("Got an error=================")
        print(self.name, ws, error)
        time.sleep(10)
        ws.sock.close()
        ws.sock = None
        ws.run_forever()

    def send(self):
        print(self.name, "send")

    def on_close(self, ws):
        print(self.name, ws, "### closed ###")

    def on_open(self, ws):
        print(self.name, "socket open")
        if 'ob' in self.ws_type:
            # fetch the snapshot of the ob
            ws.send(json.dumps({"requestId": str(uuid.uuid4()), "action": "proxy", "module": "trading", "path": "orderbook-limited/btc-pln/10"}))
            ws.send(json.dumps({"action": "subscribe-public", "module": "trading", "path": "orderbook-limited/btc-pln/10"}))
        if 'ticker' in self.ws_type:
            ws.send(json.dumps({"requestId": str(uuid.uuid4()), "action": "proxy", "module": "trading", "path": "ticker/btc-pln"}))
            ws.send(json.dumps({"action": "subscribe-public", "module": "trading", "path": "ticker/btc-pln"}))
        if 'trade' in self.ws_type:
            # active orders
            signature, t = self.create_signature()
            ws.send(json.dumps({
                "action": "subscribe-private",
                "module": "trading",
                "path": "offers/btc-pln",
                "hashSignature": signature,
                "publicKey": self.api_key,
                "requestTimestamp": t
            }
            )
            )
        if 'balance' in self.ws_type:
            # Available funds
            signature, t = self.create_signature()
            ws.send(json.dumps({
                "action": "subscribe-private",
                "module": "balances",
                "path": "balance/bitbay/updatefunds",
                "hashSignature": signature,
                "publicKey": self.api_key,
                "requestTimestamp": t
            }
            )
            )

    def create_signature(self):
        t = int(time.time())
        message = self.api_key + str(t)
        message = message.encode('utf-8')
        signature = hmac.new(self.api_secret.encode('utf-8'), message, hashlib.sha512).hexdigest()
        return signature, t

    def start(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://api.bitbay.net/websocket/",
                                         on_message=lambda ws, msg: self.on_message(ws, msg),
                                         on_error=lambda ws, msg: self.on_error(ws, msg),
                                         on_close=lambda ws: self.on_close(ws),
                                         on_open=lambda ws: self.on_open(ws)
                                         )

        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    bitbay = Bitbay(ws_type=['ob'])
    bitbay.start()
