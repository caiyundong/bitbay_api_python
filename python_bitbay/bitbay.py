#!/usr/bin/python
# coding:UTF-8

import time
import requests
import json
import uuid
import hashlib
import hmac

URL = "https://api.bitbay.net/rest"


class Bitbay():
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.secret_key = api_secret

    def query_private(self, method, url, req={}):
        t = int(time.time())
        if method == 'GET':
            message = self.api_key + str(t)
        else:
            if req:
                postdata = json.dumps(req)
            else:
                postdata = ""
            message = self.api_key + str(t) + postdata

        message = message.encode('utf-8')
        signature = hmac.new(self.secret_key.encode('utf-8'), message, hashlib.sha512).hexdigest()
        headers = {
            'API-Key': self.api_key,
            'API-Hash': signature,
            'operation-id': self.getUUID(),
            'Request-Timestamp': str(t),
            'Content-Type': 'application/json'
        }

        if method == 'GET':
            r = requests.request(method, url, headers=headers, params=json.dumps(req))
        else:
            r = requests.request(method, url, headers=headers, data=postdata)
        rep = r.json()
        return rep

    def getUUID(self):
        # 16 bytes
        return str(uuid.uuid4())

    """
    ### Trading
    """
    def create_order(self, symbol, amount, rate=None, price=None, offerType='buy', mode='limit', postOnly=True, fillOrKill=False, firstBalanceId=None, secondBalanceId=None):
        """
        New order
        :param symbol:          BTC-PLN
        :param amount:
        :param rate:
        :param price:
        :param offerType:       buy / sell
        :param mode:            limit / market
        :param postOnly:
        :param fillOrKill:
        :return:
        """
        if mode == 'limit':
            request = {"amount": amount, "rate": rate, "offerType": offerType, "mode": mode, "postOnly": postOnly, "filllOrKill": fillOrKill}
        else:
            request = {"amount": amount, "price": price, "offerType": offerType, "mode": mode, "postOnly": postOnly, "filllOrKill": fillOrKill}
        response = self.query_private("POST", URL + "/trading/offer/%s" % symbol, req=request)
        return response

    def get_active_orders(self, symbol=None):
        """

        :param symbol:
        :return:
        """
        if symbol:
            response = self.query_private("GET", URL + "/trading/offer/%s" % symbol)
        else:
            response = self.query_private("GET", URL + "/trading/offer")

        return response

    def cancel_order(self, symbol, offer_id, offer_type, price):
        """
        cancel an existing order
        :param symbol:
        :param offer_id:
        :param offer_type:
        :param price:
        :return:
        """
        response = self.query_private("DELETE", URL + "/trading/offer/%s/%s/%s/%s" % (symbol, offer_id, offer_type, price))
        return response

    def get_config(self, symbol):
        response = self.query_private("GET", URL + "/trading/config/%s" % symbol)
        return response

    def change_cnfig(self, symbol, first, second):
        """g
        Change wallet
        :param symbol:
        :param first:       UUID of wallet for first currency.
        :param second:      UUID of wallet for second currency.
        :return:
        """
        request = {"first": first, "second": second}
        response = self.query_private("POST", URL + "/trading/config/%s" % symbol, req=request)
        return response

    """
    # Deposit/Withdraw
    """
    def get_deposit_address(self, wallet_id):
        response = self.query_private("GET", URL+"/payments/crypto-address/%s" % wallet_id)
        return response

    def generate_deposit_address(self, wallet_id, currency="BTC"):
        request = {"currency": currency}
        response = self.query_private("POST", URL+"/payments/crypto-address/%s" % wallet_id, req=request)
        return response

    def get_address_history(self, wallet_id):
        response = self.query_private("GET", URL+"/payments/crypto-address/all/balance/%s" % wallet_id)
        return response

    def withdraw(self, wallet_id, address, amount, comment=""):
        request = {"address": address, "amount": amount, "comment": comment}
        response = self.query_private("POST", URL + "/payments/withdrawal/%s" % wallet_id, req=request)
        return response

    # FIAT
    def get_igoria_deposit(self, symbol):
        """

        :param symbol: e.g. ETC PLN
        :return:
        """
        response = self.query_private("GET", URL + "/payments/deposit/igoria_deposit/%s/customs" % symbol)
        return response

    def fiat_withdraw(self, wallet_id, symbol, address, amount, name):
        """

        :param wallet_id:
        :param symbol:
        :return:
        """
        request = {"address": address, "amount": amount, "name":name}
        response = self.query_private("GET", URL + "/payments/withdrawal/%s/igoria_withdrawal/%s/start" % (wallet_id, symbol), req=request)
        return response

    """
    ### History
    """
    def get_trade_transactions(self, markets, rateFrom, rateTo, fromTime, toTime, userAction, nextPageCursor):
        """

        :param markets:
        :param rateFrom:
        :param rateTo:
        :param fromTime:
        :param toTime:
        :param userAction: buy/sell
        :param nextPageCursor:  start
        :return:
        """
        request = {"markets": markets, "rateFrom": rateFrom, 'rateTo': rateTo, "fromTime": fromTime, "toTime": toTime, "userAction": userAction, "nextPageCursor": nextPageCursor}

        response = self.query_private("GET", URL + "/trading/history/transactions", req=request)
        return response

    def get_operation_transactions(self, balancesId, balanceCurrencies, fromTime, toTime, fromValue, toValue, balanceTypes, types, sort):
        request = {"balancesId": balancesId, "balanceCurrencies": balanceCurrencies, "fromTime": fromTime, "toTime": toTime, "fromValue": fromValue, "toValue": toValue,
                   "balanceTypes": balanceTypes, "types": types, "sort": sort}
        response = self.query_private("GET", URL + "/balances/BITBAY/history", req=request)
        return response

    """
    ### WALLET
    """
    def get_balance(self):
        response = self.query_private("GET", URL + "/balances/BITBAY/balance")
        return response

    def create_wallet(self, currency, type, name):
        """

        :param currency:
        :param type:
        :param name:
        :return:
        """
        request = {"currency": currency, "type": type, "name": name}
        response = self.query_private("POST", URL + "/balances/BITBAY/balance", req=request)
        return response

    def change_wallet_name(self, wallet_id, name):
        request = {"name": name}
        response = self.query_private("PUT", URL + "/balances/BITBAY/balance/%s" % wallet_id, req=request)
        return response

    def internal_transfer(self, source_id, destination_id, currency, funds):
        request = {"currency": currency, "funds": funds}
        response = self.query_private("POST", URL + "/balances/BITBAY/balance/transfer/%s/%s" % (source_id, destination_id), req=request)
        return response

    def fiat_cantor(self, currency1, currency2):
        """
        Currency rate
        :param currency1:
        :param currency2:
        :return:
        """
        response = self.query_private("GET", URL + "/fiat_cantor/rate/%s/%s" % (currency1, currency2))
        return response

    def fiat_exchange(self, currency1BalanceId, currency2BalanceId, currency1, currency2, amount, rate):
        request = {"currency1BalanceId": currency1BalanceId, "currency2BalanceId": currency2BalanceId, "currency1": currency1, "currency2": currency2, "amount": amount, "rate": rate}
        response = self.query_private("POST", URL + "/fiat_cantor/exchange", req=request)
        return response

    def fiat_history(self, page, limit, markets):
        """
        Return historical data of performed exchanges.
        :param page:
        :param limit:
        :param markets:
        :return:
        """
        request = {"page": page, "limit": limit, "markets": markets}
        response = self.query_private("GET", URL + "/fiat_cantor/history", req=request)
        return response

    """
    Market data API
    """

    def get_symbols(self):
        r = requests.get(URL + '/trading/ticker', verify=True, )
        rep = r.json()
        return list(rep['items'].keys())

    # symbol - BTC-PLN
    def get_orderbook(self, symbol):
        r = requests.get(URL + "/trading/orderbook/%s" % (symbol), verify=True, )
        rep = r.json()
        return rep

    def get_trades(self, symbol, limit=None, fromTime=None):
        """

        :param symbol:
        :param limit:
        :param fromTime:
        :return:
        """
        if limit and fromTime:
            r = requests.get(URL + "/trading/transactions/%s?limit=%s&fromTime=%s" % (symbol, limit, fromTime), verify=True, )
        elif limit:
            r = requests.get(URL + "/trading/transactions/%s?limit=%s" % (symbol, limit), verify=True, )
        elif fromTime:
            r = requests.get(URL + "/trading/transactions/%s?fromTime=%s" % (symbol, fromTime), verify=True, )
        else:
            r = requests.get(URL + "/trading/transactions/%s" % (symbol), verify=True, )
        rep = r.json()
        return rep

    def get_kline(self, symbol, seconds, start=None, end=None):
        """

        :param symbol:
        :param seconds:
        :param start:
        :param end:
        :return:
        """
        if start and end:
            url = URL + '/trading/candle/history/%s/%s?from=%s&to=%s' % (symbol, seconds, start, end)
        else:
            url = URL + '/trading/candle/history/%s/%s' % (symbol, seconds)

        r = requests.get(url, verify=True, )
        rep = r.json()
        return rep

    def get_stats(self, symbol=None):
        """

        :param symbol:
        :return:
        """
        if symbol:
            r = requests.get(URL + '/trading/stats/%s' % symbol, verify=True, )
            rep = r.json()
            return rep['stats']
        else:
            r = requests.get(URL + '/trading/stats', verify=True, )
            rep = r.json()
            return rep['items']

    def get_ticker(self, symbol=None):
        """
        get the ticker
        :param symbol:
        :return:
        """
        if symbol:
            r = requests.get(URL + '/trading/ticker/%s' % symbol, verify=True, )
            rep = r.json()
            print(rep)
            return rep['ticker']
        else:
            r = requests.get(URL + '/trading/ticker', verify=True, )
            rep = r.json()
            return rep['items']


if __name__ == '__main__':
    bitbay = Bitbay(api_key="xxxxx-0874-4a51-b19e-9e7d6eb6f4bf", api_secret="xxxx-73aa-4afa-975e-96c65d822630")

    # private methods
    print(bitbay.get_balance())
    # order = bitbay.create_order('BTC-USD', amount=1, rate=100, offerType='buy', mode='limit')
    # print(order)
    # result = bitbay.cancel_order('BTC-USD', '82ca35da-6eeb-4f30-91bb-165fdcf4d8b2', 'buy', 4000);
    # print(result)
    # print(bitbay.get_active_orders())
    print(bitbay.get_trade_transactions(markets=['BTC-USD'], rateFrom='10', rateTo='20', fromTime=None, toTime=None, userAction='Buy', nextPageCursor="start"))

    # Market Data
    # print(bitbay.get_symbols())
    # print(bitbay.get_ticker("BTC-PLN"))
    # print(bitbay.get_orderbook('BTC-PLN'))
    # print(bitbay.get_kline(symbol="BTC-USD", seconds=600))
    # print(bitbay.get_trades("BTC-USD"))
