import pandas as pd
import yfinance as yf
from app.services.indicators import calculate_indicators
from app.services.explainer import generate_explanation

def get_ai_stocks():
    print("Initiating Nifty 500 Market Scan...")
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    try:
        df = pd.read_csv(url)
        symbols = (df['Symbol'] + ".NS").tolist()
    except Exception as e:
        print("Failed to fetch NSE CSV, falling back to top 5 default.", e)
        symbols = [
            "RELIANCE.NS",
            "TCS.NS",
            "HDFCBANK.NS",
            "ITC.NS",
            "INFOSYS.NS"
        ]

    print(f"Downloading {len(symbols)} tickers dynamically...")
    # Bulk fetch
    bulk_data = yf.download(symbols, period="3mo", group_by='ticker', threads=True)

    stocks = []

    for symbol in symbols:
        try:
            # Handle yfinance single symbol vs multi-symbol structural difference
            if len(symbols) == 1:
                stock_history = bulk_data
            else:
                if symbol not in bulk_data.columns.levels[0]:
                    continue
                stock_history = bulk_data[symbol]
                
            data = calculate_indicators(stock_history)
            
            if not data:
                continue

            stock_data = {
                "name": symbol,
                "price": float(data["price"]),
                "score": float(data["score"]),
                "rsi": float(data["rsi"]),
                "passed_tests": data.get("passed_tests", [])
            }

            stock_data["explanation"] = generate_explanation(stock_data)

            stocks.append(stock_data)
            
        except Exception as e:
            continue

    # 🔥 Sort by best score (important)
    stocks = sorted(stocks, key=lambda x: x["score"], reverse=True)

    # Return top 20 candidates from the 500 scan for portfolio allocation filtering
    return stocks[:20]


def allocate_funds(total_capital, stocks):
    total_score = sum(stock["score"] for stock in stocks if stock["score"] > 0)

    allocated_stocks = []

    for stock in stocks:
        if stock["score"] <= 0:
            continue  # ❌ skip weak stocks

        weight = stock["score"] / total_score
        investment = weight * total_capital

        # ✅ Buy whole shares only (Floor to stay under budget)
        quantity = int(investment // stock["price"])
        
        stock["investment"] = float(round(quantity * stock["price"], 2))
        stock["quantity"] = quantity
        stock["price"] = float(stock["price"])
        stock["score"] = float(stock["score"])
        stock["rsi"] = float(stock["rsi"])

        if quantity > 0:
            allocated_stocks.append(stock)

    return allocated_stocks