import yfinance as yf
from decimal import Decimal
from django.core.cache import cache

def get_stock_data(symbol):
    """
    Fetches live stock data from yfinance with a 5-minute cache.
    """
    cache_key = f"stock_data_{symbol}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        last_price = info.last_price
        
        long_name = getattr(ticker, 'info', {}).get('longName', symbol)
        
        history = ticker.history(period="1d")
        if not history.empty:
            open_price = history['Open'].iloc[0]
            change = Decimal(str(last_price - open_price))
            change_percent = Decimal(str((last_price - open_price) / open_price * 100))
        else:
            change = Decimal('0.00')
            change_percent = Decimal('0.00')

        data = {
            'symbol': symbol,
            'name': long_name,
            'price': Decimal(str(round(last_price, 2))),
            'change': change.quantize(Decimal('0.01')),
            'change_percent': change_percent.quantize(Decimal('0.01')),
        }
        
        # Cache the result for 5 minutes (300 seconds)
        cache.set(cache_key, data, 300)
        return data
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return None

def get_multiple_stocks(symbols):
    """
    Fetch multiple stocks efficiently using individual cache checks.
    """
    results = {}
    for sym in symbols:
        data = get_stock_data(sym)
        if data:
            results[sym] = data
    return results
