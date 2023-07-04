import yfinance as yf
import pandas as pd
import pyfolio as pf

def get_top5_performers(stocks, start_date, end_date):
    data = yf.download(stocks, start=start_date, end=end_date)
    returns = data['Adj Close'].pct_change(52)  # Adjusted Close prices for weekly returns
    returns = returns.iloc[-1]  # Get the latest (most recent) 52-week returns
    sorted_returns = returns.sort_values(ascending=False)
    top5_performers = sorted_returns.head(5)
    return top5_performers

def calculate_atr(data, period=14):
    high_low = data['High'] - data['Low']
    high_close_prev = abs(data['High'] - data['Close'].shift())
    low_close_prev = abs(data['Low'] - data['Close'].shift())
    true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr

def rebalance_portfolio(top5, start_date, end_date):
    stop_loss_multiplier = 2
    portfolio = {}

    for symbol in top5.index:
        stock_data = yf.download(symbol, start=start_date, end=end_date)
        atr = calculate_atr(stock_data)
        entry_price = stock_data['Close'].iloc[-1]
        stop_loss_price = entry_price - (stop_loss_multiplier * atr.iloc[-1])
        portfolio[symbol] = stop_loss_price
    return portfolio

def main():
    stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'JPM']
    start_date = '2020-01-01'
    end_date = '2023-01-01'
    top5 = get_top5_performers(stock_symbols, start_date, end_date)
    print("Top 5 Performers based on 52-week rolling returns:")
    print(top5)
    weekly_dates = pd.date_range(start=start_date, end=end_date, freq='W')
    portfolio_performance = pd.DataFrame(index=weekly_dates)

    for i in range(len(weekly_dates)-1):
        portfolio = rebalance_portfolio(top5, start_date, weekly_dates[i])

  
    portfolio_performance['Returns'] = portfolio_performance['Portfolio Value'].pct_change()
    returns = portfolio_performance['Returns']
    positions = pd.DataFrame()  # Placeholder for positions
    transactions = pd.DataFrame()  # Placeholder for transactions
    portfolio_obj = pf.create_returns(returns, positions=positions, transactions=transactions)
    pf.create_full_tear_sheet(portfolio_obj)

if _name_ == "_main_":
    main()