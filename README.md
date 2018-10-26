# BitBay REST API for Python3

See full description at https://docs.bitbay.net/v3.2.0/reference

## Installation

```bash
  pip install python-bitbay
```

## Usage

The BBA constructor receive public and private key using to authentication.
```python
from python_bitbay import bitbay

bitbay_client = bitbay.Bitbay(api_key='32345f6f-1b1d-1234-a923-a10b1bdba1a1', api_secret='48539fe0-e3b0-4e4e-8c86-70b36aa93d4f');
```

## Public endpoints

```python

bitbay_client.ticker('BTC-EUR');

// Get orderbook from LSK-PLN market
bitbay_client.orderbook('LSK-PLN');

// Get last 10 transactions on BTC-USD market from last 3 minutes
bitbay_client.transactions('BTC-USD', { limit: 10, fromTime: 1531407461 } );

// Get 30 minutes candles from last 4 hours
bitbay_client.candles('BTC-PLN', 1800, { fromTime: 1544158620, toTime: 1544173061 } );
```

## Private endpoints
### Trading

```python

// We want to buy 1 Bitcoin for 4000$ on BTC-USD market and offer will be hidden
bitbay_client.create_order('BTC-USD', { amount: 1, rate: 1, offerType: 'buy', mode: 'limit', hidden: true } );

// Let's get active offers from every market
bitbay_client.getActiveOrders();

// Remove an offer
bitbay_client.cancel_order('BTC-USD', '82ca35da-6eeb-4f30-91bb-165fdcf4d8b2', 'buy', 4000);

// Get our trading fees on BTC-PLN market (default)
bitbay_client.getConfig();

// Change default wallets to trade on BTC-USD
bitbay_client.changeConfig('BTC-USD', { first: '455b3f25-8d3a-409f-9fe6-8cc40f1ce533', second: '455b3f25-8d3a-509f-9fe6-8cc40f1ce542' } );
```

### Deposit and withdrawal
```python
// Get our address to deposit cryptocurrency on specified wallet
bitbay_client.getCryptoAddress('455b3f25-8d3a-409f-9fe6-8cc40f1ce533');

// Generate new cryptocurrency address on specified wallet
bitbay_client.getNewAddress('455b3f25-8d3a-409f-9fe6-8cc40f1ce533', { currency: 'PLN' } );

// Get all historical addresses from specified wallet
bitbay_client.getHistoricalAddresses('455b3f25-8d3a-409f-9fe6-8cc40f1ce533');

// Let's send some Bitcoins
bitbay_client.withdrawCrypto('455b3f25-8d3a-409f-9fe6-8cc40f1ce533', { address: '3Qck3sNnAe5YVLe9WDzMp3aK2cgsU7F5Wv', amount: 0.5, comment: 'test' } );

// Get address to deposit USD
bitbay_client.getFiatAddress('USD');

// Time for withdraw our USD
bitbay_client.withdrawFiat('455b3f25-8d3a-409f-9fe6-8cc40f1ce655', 'USD', { bank_account_number: 'PL82154012872216000073790002', address: '111A/109, 02-707 Warszawa', name: 'Igoria Trade S.A.', title: 'VVVe94d7e43536fVVV', swift: 'EBOSPLPWXXX' } );
```

### History
```python
// Get transactions history for buy transactions from BTC-PLN where rate is from 23000 to 25000
bitbay_client.getTransactionsHistory( { markets: ['BTC-PLN'], rateFrom:23000, rateTo: 25000, userAction: 'buy', nextPageCursor: 'start' } );

// Get 20 last historical operations on XMR wallets and sort descending by time
bitbay_client.getOperationsHistory( { "balanceCurrencies":["XMR"], "limit":"20", "sort":[{"order":"DESC","by":"time"}], "nextPageCursor":"start"});
```

### Manage wallets
```python
// Get list of all wallets
bitbay_client.getWallets();

// Create a new wallet for Bitcoin
bitbay_client.newWallet( { currency: 'BTC', type: 'crypto', name: 'trading' } );

// I think that was a bad name, let's change it
bitbay_client.changeWalletName('455b3f25-8d3a-409f-9fe6-8cc40f1ce533', { name: 'arbitration' } );

// Send some cryptocurrency over our wallets
bitbay_client.internalTransfer('455b3f25-8d3a-409f-9fe6-8cc40f1ce533', '455b3f25-8d3a-409f-9fe6-8cc40f1ce534', { currency: 'BTC', funds: 0.4 } );
```

## Donate
If this library helped you out feel free to donate.

ETH: 0xAbBeE2d8355310Bf61531DD94C086636194A4a54