from alpaca_trade_api.polygon import REST
import pytest
import requests_mock


@pytest.fixture
def reqmock():
    with requests_mock.Mocker() as m:
        yield m


def endpoint(path):
    return 'https://api.polygon.io/v1{}?apiKey=key-id'.format(path)


def test_polygon(reqmock):
    cli = REST('key-id')

    # Exchanges
    reqmock.get(endpoint('/meta/exchanges'), text='''
    [{"id":0,"type":"TRF","market":"equities","mic":"TFF","name":"Multiple","tape":"-"}]
''')

    exchanges = cli.exchanges()
    assert exchanges[0].id == 0
    assert 'Exchange(' in str(exchanges[0])

    # Symbol Type Map
    reqmock.get(endpoint('/meta/symbol-types'), text='''
{
  "cs": "Common Stock",
  "adr": "American Depository Receipt",
  "cef": "Closed-End Fund",
  "etp": "Exchange Traded Product",
  "reit": "Real Estate Investment Trust",
  "mlp": "Master Limited Partnership",
  "wrt": "Equity WRT",
  "pub": "Public",
  "nyrs": "New York Registry Shares",
  "unit": "Unit",
  "right": "Right",
  "trak": "Tracking stock or targeted stock",
  "ltdp": "Limited Partnership",
  "rylt": "Royalty Trust",
  "mf": "Mutual Fund",
  "pfd": "Preferred Stoc"
}
''')

    tmap = cli.symbol_type_map()
    assert tmap.cs == 'Common Stock'

    # Historic Trades
    reqmock.get(
        endpoint('/historic/trades/AAPL/2018-2-2') +
        '&limit=100&offset=1000',
        text='''
{
  "day": "2018-2-2",
  "map": {
    "c1": "condition1",
    "c2": "condition2",
    "c3": "condition3",
    "c4": "condition4",
    "e": "exchange",
    "p": "price",
    "s": "size",
    "t": "timestamp"
  },
  "msLatency": 8,
  "status": "success",
  "symbol": "AAPL",
  "ticks": [
    {
      "c1": 14,
      "c2": 12,
      "c3": 0,
      "c4": 0,
      "e": 12,
      "p": 172.17,
      "s": 50,
      "t": 1517529601006
    }
  ]
}''')

    trades = cli.historic_trades('AAPL', '2018-2-2',
                                 limit=100, offset=1000)
    assert trades[0].price == 172.17
    assert trades[0].timestamp.month == 2
    assert len(trades) == 1
    assert trades.df.iloc[0].price == 172.17

    # Historic Quotes
    reqmock.get(
        endpoint('/historic/quotes/AAPL/2018-2-2') +
        '&limit=100&offset=1000',
        text='''
{
  "day": "2018-2-2",
  "map": {
    "aE": "askexchange",
    "aP": "askprice",
    "aS": "asksize",
    "bE": "bidexchange",
    "bP": "bidprice",
    "bS": "bidsize",
    "c": "condition",
    "t": "timestamp"
  },
  "msLatency": 3,
  "status": "success",
  "symbol": "AAPL",
  "ticks": [
    {
      "c": 0,
      "bE": 11,
      "aE": 12,
      "aP": 173.15,
      "bP": 173.13,
      "bS": 25,
      "aS": 55,
      "t": 1517529601006
    }
  ]
}''')

    quotes = cli.historic_quotes('AAPL', '2018-2-2',
                                 limit=100, offset=1000)
    assert quotes[0].askprice == 173.15
    assert quotes[0].timestamp.month == 2
    assert len(quotes) == 1
    assert quotes.df.iloc[0].bidprice == 173.13

    # Historic Aggregates
    reqmock.get(
        endpoint('/historic/agg/minute/AAPL') +
        '&from=2018-2-2&to=2018-2-5&limit=100',
        text='''
{
  "map": {
    "a": "average",
    "c": "close",
    "h": "high",
    "l": "low",
    "o": "open",
    "d": "timestamp",
    "v": "volume"
  },
  "status": "success",
  "aggType": "minute",
  "symbol": "AAPL",
  "ticks": [
    {
      "o": 173.15,
      "c": 173.2,
      "l": 173.15,
      "h": 173.21,
      "v": 1800,
      "d": 1517529605000
    }
  ]
}''')

    aggs = cli.historic_agg('minute', 'AAPL',
                            _from='2018-2-2',
                            to='2018-2-5',
                            limit=100)
    assert aggs[0].open == 173.15
    assert aggs[0].timestamp.day == 1
    assert len(aggs) == 1
    assert aggs.df.iloc[0].high == 173.21

    # Last Trade
    reqmock.get(
        endpoint('/last/stocks/AAPL'),
        text='''
{
  "status": "success",
  "symbol": "AAPL",
  "last": {
    "price": 159.59,
    "size": 20,
    "exchange": 11,
    "cond1": 14,
    "cond2": 16,
    "cond3": 0,
    "cond4": 0,
    "timestamp": 1518086464720
  }
}''')

    trade = cli.last_trade('AAPL')
    assert trade.price == 159.59
    assert trade.timestamp.day == 8

    # Last Quote
    reqmock.get(
        endpoint('/last_quote/stocks/AAPL'),
        text='''
{
  "status": "success",
  "symbol": "AAPL",
  "last": {
    "askprice": 159.59,
    "asksize": 2,
    "askexchange": 11,
    "bidprice": 159.45,
    "bidsize": 20,
    "bidexchange": 12,
    "timestamp": 1518086601843
  }
}''')

    quote = cli.last_quote('AAPL')
    assert quote.askprice == 159.59
    assert quote.timestamp.day == 8

    # Condition Map
    reqmock.get(
        endpoint('/meta/conditions/trades'),
        text='''
{
  "1": "Regular",
  "2": "Acquisition",
  "3": "AveragePrice",
  "4": "AutomaticExecution"
}''')

    cmap = cli.condition_map()
    assert cmap._raw['1'] == 'Regular'
