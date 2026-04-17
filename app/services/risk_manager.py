import yfinance as yf

def check_stop_loss(portfolio, db=None):
    alerts = []

    for stock in portfolio:
        try:
            ticker = yf.Ticker(stock.stock_name)
            current_price = float(ticker.fast_info['lastPrice'])
        except Exception:
            continue 

        # 1. Update High-Water Mark (Peak price since purchase)
        if current_price > stock.highest_price:
            stock.highest_price = current_price
            if db:
                db.commit()
        
        # 2. Step-Up Protection Logic
        # Case A: Initial Protection (Before Target hit)
        active_sl = stock.buy_price * 0.95 # Phase 1: 5% Risk
        protection_status = "INITIAL_RISK"

        # Case B: Capital Protection & Profit Locking (If Target hit)
        if stock.target_price and stock.target_price > stock.buy_price:
            interval = stock.target_price - stock.buy_price
            
            if stock.highest_price >= stock.target_price:
                # Milestone reached! 
                # Formula: SL = BuyPrice + (Steps * Interval)
                # Steps = number of intervals peaked above target
                steps = int((stock.highest_price - stock.target_price) // interval)
                active_sl = stock.buy_price + (steps * interval)
                
                if steps == 0:
                    protection_status = "CAPITAL_PROTECTED"
                else:
                    protection_status = "PROFIT_LOCKED"
        
        # 3. Check for Violation
        if current_price < active_sl:
            alerts.append({
                "name": stock.stock_name,
                "type": "STOP_LOSS_HIT",
                "status": protection_status,
                "buy_price": round(stock.buy_price, 2),
                "active_sl": round(active_sl, 2),
                "current_price": round(current_price, 2),
                "peak_reached": round(stock.highest_price, 2)
            })

    return alerts