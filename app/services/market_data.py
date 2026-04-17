import yfinance as yf

def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")

        if data.empty:
            return None

        return round(data["Close"].iloc[-1], 2)

    except Exception as e:
        print("Error fetching price:", e)
        return None