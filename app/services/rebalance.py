def rebalance_portfolio(old_portfolio, new_portfolio):
    old_stocks = {stock.stock_name: stock for stock in old_portfolio}
    new_stocks = {stock["name"]: stock for stock in new_portfolio}

    buy = []
    sell = []
    hold = []

    for name, stock in new_stocks.items():
        if name not in old_stocks:
            buy.append(stock)
        else:
            hold.append(stock)

    for name, stock in old_stocks.items():
        if name not in new_stocks:
            sell.append(stock)

    return {
        "buy": buy,
        "sell": sell,
        "hold": hold
    }