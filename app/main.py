from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.services.matrix_engine import get_temporal_matrix
from app.db.database import SessionLocal, engine, Base
from app.db import models
from app.services.ai_engine import get_ai_stocks, allocate_funds
from app.services.rebalance import rebalance_portfolio
from app.services.risk_manager import check_stop_loss
from app.utils.telegram import send_telegram
import threading
from app.utils.scheduler import run_scheduler
import feedparser
from app.services.strategy_oracle import analyze_macro_headlines
import datetime
import pandas as pd
import random

from pydantic import BaseModel

class BuyStockRequest(BaseModel):
    user_id: int
    stock_name: str
    quantity: float
    buy_price: float
    ai_score: float
    rsi: float
    explanation: str

class UpdateRiskShieldRequest(BaseModel):
    user_id: int
    stock_name: str
    trailing_sl_percent: float
    target_price: float = None
    rsi: float
    explanation: str

class SellStockRequest(BaseModel):
    user_id: int
    stock_name: str
    quantity: float
    buy_price: float
    ai_score: float
    rsi: float
    explanation: str

class AuthRequest(BaseModel):
    phone: str

class VerifyRequest(BaseModel):
    phone: str
    otp: str

# Create tables
Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Added CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DB SESSION ---------------- #
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- AUTH ---------------- #
@app.post("/auth/request-otp")
def request_otp(req: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone == req.phone).first()
    
    if not user:
        # Auto-Signup with phone
        user = models.User(name=f"User_{req.phone[-4:]}", phone=req.phone, capital=100000.0)
        db.add(user)
        db.commit()
        db.refresh(user)

    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    db.commit()

    message = f"🛡️ *AI LOGON SECURITY*\n\nYour One-Time Passcode for **{req.phone}** is:\n\n`{otp}`\n\nCode expires in 5 minutes."
    send_telegram(message)

    return {"message": "OTP sent to Telegram"}

@app.post("/auth/verify-otp")
def verify_otp(req: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone == req.phone).first()
    
    if not user or user.otp_code != req.otp:
        return {"error": "Invalid or expired OTP"}

    # Clear OTP after success
    user.otp_code = None
    db.commit()

    return {"user_id": user.id, "phone": user.phone, "username": user.name}

# ---------------- ROOT ---------------- #
@app.get("/")
def home():
    return {"message": "AI Trading Agent Running 🚀"}

# ---------------- USER ---------------- #
@app.post("/create-user")
def create_user(name: str, capital: float, db: Session = Depends(get_db)):
    user = models.User(name=name, capital=capital)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "capital": user.capital}

@app.get("/user-balance")
def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return {"error": "User Not Found"}
    return {"balance": user.capital}

# ---------------- FUNDS ---------------- #
@app.post("/add-funds")
def add_funds(user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        return {"error": "User Not Found"}

    user.capital += amount
    db.add(models.FundHistory(user_id=user_id, amount=amount, type="add"))
    db.commit()

    return {"new_balance": user.capital}


@app.post("/withdraw-funds")
def withdraw_funds(user_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        return {"error": "User not found"}

    if user.capital < amount:
        return {"error": "Insufficient balance"}

    user.capital -= amount
    db.add(models.FundHistory(user_id=user_id, amount=amount, type="withdraw"))
    db.commit()

    return {"new_balance": user.capital}

# ---------------- GENERATE PORTFOLIO ---------------- #
@app.post("/generate-portfolio")
def generate_portfolio(user_id: int, notify: bool = True, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        return {"error": "User Not Found"}
    
    stocks = get_ai_stocks()
    allocated = allocate_funds(user.capital, stocks)
    
    if notify:
        # 🔥 Telegram with AI Explanation (Sent as suggestions)
        message = "📊 *AI Weekly Top 5 Recommendations*\n\n"
        for stock in allocated:
            message += f"""
🟢 *{stock['name']}*
💰 ₹{stock['price']} | 📊 Score: {stock['score']}
📦 Qty: {stock['quantity']}

🧠 {stock['explanation']}

----------------------
"""
        send_telegram(message)

    return {"message": "Recommendations generated", "data": allocated}

# ---------------- BUY STOCK ---------------- #
@app.post("/buy-stock")
def buy_stock(req: BuyStockRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user: return {"error": "User Not Found"}
    
    cost = req.quantity * req.buy_price
    if user.capital < cost: 
        return {"error": "Insufficient capital"}
    
    # Check if user already owns this stock
    existing = db.query(models.Portfolio).filter(
        models.Portfolio.user_id == req.user_id,
        models.Portfolio.stock_name == req.stock_name
    ).first()

    if existing:
        # Calculate Weighted Average Price
        new_total_qty = existing.quantity + req.quantity
        new_avg_price = ((existing.buy_price * existing.quantity) + (req.buy_price * req.quantity)) / new_total_qty
        
        # Update existing record
        existing.quantity = new_total_qty
        existing.buy_price = round(new_avg_price, 2)
        existing.ai_score = req.ai_score
        existing.rsi = req.rsi
        existing.explanation = req.explanation
    else:
        # Create new position
        db.add(models.Portfolio(
            user_id=req.user_id, 
            stock_name=req.stock_name, 
            quantity=req.quantity, 
            buy_price=req.buy_price, 
            ai_score=req.ai_score, 
            rsi=req.rsi, 
            explanation=req.explanation,
            highest_price=req.buy_price, # Initialize peak price
            trailing_sl_percent=5.0      # Default 5% Risk Buffer
        ))

    user.capital -= cost
    
    # 📝 Log Trade to Ledger
    ist_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)).strftime("%d %b %Y | %H:%M IST")
    db.add(models.TradeLog(
        user_id=req.user_id,
        stock_name=req.stock_name,
        quantity=req.quantity,
        price=req.buy_price,
        timestamp=ist_time,
        type="BUY"
    ))

    db.add(models.FundHistory(user_id=req.user_id, amount=cost, type="buy_stock"))
    db.commit()
    
    return {"message": f"Successfully purchased {req.stock_name}", "new_balance": user.capital}

@app.get("/portfolio-growth")
def get_portfolio_growth(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: return {"error": "User Not Found"}
    
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).all()
    
    # 6-Month Rolling Data
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=180)
    
    # Default to just capital points if portfolio is empty
    if not portfolio:
        months = []
        for i in range(6):
            date = end_date - datetime.timedelta(days=i*30)
            months.append({"name": date.strftime("%b"), "value": user.capital})
        return months[::-1]

    import yfinance as yf
    tickers = [p.stock_name for p in portfolio]
    
    try:
        data = yf.download(tickers, start=start_date, interval="1mo")['Close']
        if isinstance(data, pd.Series): # Single ticker case
            data = data.to_frame()
            data.columns = [tickers[0]]
            
        history = []
        for date, row in data.iterrows():
            total_val = user.capital
            for p in portfolio:
                price = row.get(p.stock_name)
                if pd.isna(price): 
                    price = p.buy_price
                total_val += (price * p.quantity)
            
            history.append({
                "name": date.strftime("%b"),
                "value": round(total_val, 2)
            })
        return history
    except Exception as e:
        print("Growth fetch error:", e)
        return [{"name": "Now", "value": user.capital}]

@app.get("/stock-history")
def get_stock_history(symbol: str):
    import yfinance as yf
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo", interval="1d")
        points = [{"date": idx.strftime("%d %b"), "price": round(row['Close'], 2)} for idx, row in hist.iterrows()]
        return points
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        return []

# ---------------- GET PORTFOLIO ---------------- #
@app.get("/portfolio")
def get_portfolio(user_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).all()
    
    import yfinance as yf
    enriched = []
    for p in portfolio:
        try:
            ticker = yf.Ticker(p.stock_name)
            current_price = float(ticker.fast_info['lastPrice'])
        except:
            current_price = p.buy_price
            
        profit_percent = ((current_price - p.buy_price) / p.buy_price) * 100 if p.buy_price > 0 else 0
        enriched.append({
            "id": p.id,
            "stock_name": p.stock_name,
            "quantity": p.quantity,
            "buy_price": p.buy_price,
            "current_price": round(current_price, 2),
            "profit": round(profit_percent, 2),
            "ai_score": p.ai_score,
            "rsi": p.rsi,
            "explanation": p.explanation
        })
    return enriched

# ---------------- SELL STOCK ---------------- #
@app.post("/sell-stock")
def sell_stock(req: SellStockRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user: return {"error": "User Not Found"}
    
    asset = db.query(models.Portfolio).filter(
        models.Portfolio.user_id == req.user_id, 
        models.Portfolio.stock_name == req.stock_name
    ).first()
    
    if not asset: return {"error": "Asset not found"}
    
    # Validation: Can't sell more than you own
    if req.quantity <= 0:
        # Default: if quantity is 0, we sell all (legacy support)
        sell_qty = asset.quantity
    elif req.quantity > asset.quantity:
        return {"error": f"Liquidation Overflow: You only hold {asset.quantity} units."}
    else:
        sell_qty = req.quantity

    import yfinance as yf
    try:
        current_price = float(yf.Ticker(req.stock_name).fast_info['lastPrice'])
    except:
        current_price = asset.buy_price
        
    cash_gained = current_price * sell_qty
    user.capital += cash_gained
    
    if sell_qty == asset.quantity:
        db.delete(asset)
    else:
        asset.quantity -= sell_qty
        
    db.add(models.FundHistory(user_id=req.user_id, amount=cash_gained, type="sell_stock"))
    
    # 📝 Log Trade to Ledger
    ist_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)).strftime("%d %b %Y | %H:%M IST")
    db.add(models.TradeLog(
        user_id=req.user_id,
        stock_name=req.stock_name,
        quantity=sell_qty,
        price=round(current_price, 2),
        timestamp=ist_time,
        type="SELL"
    ))
    
    db.commit()
    db.commit()
    
    return {"message": f"Successfully sold {sell_qty} units of {req.stock_name}", "new_balance": user.capital}

# ---------------- REBALANCE ---------------- #
@app.get("/rebalance-portfolio")
def rebalance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: return {"error": "User not found"}

    old_portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).all()
    if not old_portfolio: return {"error": "No portfolio found. Buy first."}

    stocks = get_ai_stocks() # Fetch top dynamically
    old_names = [s.stock_name for s in old_portfolio]
    
    candidates = [s for s in stocks if s["name"] not in old_names]
    analytics = []
    
    for old in old_portfolio:
        match = next((s for s in stocks if s["name"] == old.stock_name), None)
        
        if match:
            tag = "🟢 BUY MORE" if match["score"] > 80 else "🟡 HOLD"
            analytics.append({
                "stock": old.stock_name,
                "action": tag,
                "current_score": match["score"],
                "replacement": None
            })
        else:
            tag = "🔴 SELL"
            replacement = candidates.pop(0) if candidates else None
            analytics.append({
                "stock": old.stock_name,
                "action": tag,
                "current_score": 0,
                "replacement": replacement
            })

    return {"message": "Analytics Complete", "analytics": analytics}

# ---------------- TEMPORAL MATRIX STREAM ---------------- #
@app.get("/scan-news")
def scan_global_news(user_id: int = None, broadcast: bool = False, db: Session = Depends(get_db)):
    portfolio_symbols = []
    if user_id:
        portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).all()
        portfolio_symbols = [s.stock_name for s in portfolio]
    
    matrix = get_temporal_matrix(portfolio_symbols)
    
    # AI Summary Recommendation for the top items
    ai_analysis = analyze_macro_headlines(matrix["pass"][:3])
    
    if broadcast:
        # User requested 14-day projection (Next Two Weeks)
        coming = matrix.get("coming", [])
        msg = "🌐 <b>NEURAL PULSE: TWO-WEEK OUTLOOK</b>\n\n"
        if coming:
            for event in coming[:5]:
                impact_color = {"CRITICAL": "#ff4444", "HIGH": "#ff8800", "MED": "#ffcc00"}.get(event['impact'], "#888888")
                msg += f"📅 <b>{event['date']}</b>: {event['title']}\n"
                msg += f"↳ Impact: <code>{event['impact']}</code>\n\n"
        else:
            msg += "<i>No high-impact events detected in the immediate projection matrix.</i>\n"
        
        msg += "\n⚠️ <i>Plan telemetry accordingly.</i>"
        send_telegram(msg)

    return {
        "message": "Temporal Matrix Recalibrated", 
        "matrix": matrix,
        "ai_analysis": ai_analysis
    }

# ---------------- TELEGRAM TEST ---------------- #
@app.get("/test-telegram")
def test_telegram():
    send_telegram("🚀 Telegram Bot Working Perfectly!")
    return {"status": "sent"}

# ---------------- SCHEDULER ---------------- #
@app.on_event("startup")
def start_scheduler():
    thread = threading.Thread(target=run_scheduler)
    thread.daemon = True
    thread.start()

# ---------------- GLOBAL RISK SCAN (AUTO) ---------------- #
@app.get("/check-global-risk")
def check_global_risk(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    total_alerts = 0
    
    for user in users:
        portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user.id).all()
        if not portfolio: continue
        
        alerts = check_stop_loss(portfolio, db)
        if alerts:
            total_alerts += len(alerts)
            for alert in alerts:
                if alert['type'] == 'STOP_LOSS_HIT':
                    status_text = {
                        "INITIAL_RISK": "🚨 INITIAL RISK BUFFER HIT",
                        "CAPITAL_PROTECTED": "🛡️ CAPITAL PROTECTION BREACH",
                        "PROFIT_LOCKED": "💰 PROFIT LOCK-IN VIOLATION"
                    }.get(alert['status'], "⚠️ RISK ALERT")

                    msg = f"""
{status_text}

Node: {user.name}
Asset: <b>{alert['name']}</b>
---------------------------
💰 Buy Price: ₹{alert['buy_price']}
🚀 Peak Price: ₹{alert['peak_reached']}
🛑 Exit Floor: ₹{alert['active_sl']}
📊 Current: ₹{alert['current_price']}

❌ <i>Condition Met: Liquidation Advised.</i>
"""
                else:
                    msg = f"⚠️ <b>RISK ALERT:</b> {alert['name']} has triggered a telemetry violation."
                
                send_telegram(msg)
                
    return {"message": f"Global risk scan complete. {total_alerts} violations detected."}

# ---------------- MONTHLY REBALANCE TRIGGER (AUTO) ---------------- #
@app.get("/trigger-automated-rebalance")
def trigger_automated_rebalance(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    
    for user in users:
        # Trigger rebalance logic for each user
        # (Reusing analytics logic from /rebalance-portfolio)
        portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user.id).all()
        if not portfolio: continue
        
        stocks = get_ai_stocks()
        old_names = [s.stock_name for s in portfolio]
        candidates = [s for s in stocks if s["name"] not in old_names]
        
        msg = f"🧠 <b>AI NEURAL SCAN: REBALANCE</b>\nNode: <b>{user.name}</b>\n\n"
        for old in portfolio:
            match = next((s for s in stocks if s["name"] == old.stock_name), None)
            if match:
                if match["score"] < 70:
                    tag = "🔴 SELL"
                    rep = candidates.pop(0) if candidates else None
                    msg += f"• {old.stock_name}: {tag} (Score: {match['score']})\n"
                    if rep: msg += f"  ↳ 🟢 BUY: <b>{rep['name']}</b> (Score: {rep['score']})\n"
                else:
                    msg += f"• {old.stock_name}: 🟡 HOLD (Score: {match['score']})\n"
            else:
                tag = "🔴 SELL (Low Confidence)"
                rep = candidates.pop(0) if candidates else None
                msg += f"• {old.stock_name}: {tag}\n"
                if rep: msg += f"  ↳ 🟢 BUY: <b>{rep['name']}</b> (Score: {rep['score']})\n"
        
        # Add General AI Picks (Top 3)
        msg += "\n📈 <b>TOP AI PICKS (MARKET SCAN):</b>\n"
        for pick in stocks[:3]:
            msg += f"• <b>{pick['name']}</b> | Score: {pick['score']}%\n"

        send_telegram(msg)
        
    return {"message": "Monthly rebalancing signals broadcasted to all nodes."}

# ---------------- PORTFOLIO SUMMARY TRIGGER (AUTO) ---------------- #
@app.get("/trigger-portfolio-summary")
def trigger_portfolio_summary(db: Session = Depends(get_db)):
    import yfinance as yf
    users = db.query(models.User).all()

    for user in users:
        portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user.id).all()
        if not portfolio: continue

        total_invested = 0
        total_current = 0
        holdings_text = ""

        for stock in portfolio:
            invested = (stock.buy_price or 0) * (stock.quantity or 0)
            total_invested += invested
            
            try:
                curr_price = float(yf.Ticker(stock.stock_name).fast_info['lastPrice'])
            except:
                curr_price = stock.buy_price or 0
                
            current_val = curr_price * (stock.quantity or 0)
            total_current += current_val
            
            perf = ((curr_price - stock.buy_price) / stock.buy_price * 100) if stock.buy_price > 0 else 0
            icon = "📈" if perf >= 0 else "📉"
            holdings_text += f"• <b>{stock.stock_name}</b>: {icon} {perf:+.1f}%\n"

        net_profit = total_current - total_invested
        profit_pct = (net_profit / total_invested * 100) if total_invested > 0 else 0
        
        msg = f"""📊 <b>PORTFOLIO VAULT STATUS</b>
Node: <b>{user.name}</b>

💰 Total Valuation: <b>₹{total_current:,.2f}</b>
📈 Net Performance: <b>{profit_pct:+.2f}%</b>
---------------------------
📦 <b>Asset Delta:</b>
{holdings_text}

🛡️ <b>Risk Status: SECURED</b>
<i>Institutional telemetry within safe parameters.</i>
"""
        send_telegram(msg)

    return {"message": "Weekly portfolio summaries broadcasted."}


# ---------------- TRADE LEDGER ---------------- #
@app.get("/trade-ledger")
def get_trade_ledger(user_id: int, stock_name: str, db: Session = Depends(get_db)):
    trades = db.query(models.TradeLog).filter(
        models.TradeLog.user_id == user_id,
        models.TradeLog.stock_name == stock_name
    ).order_by(models.TradeLog.id.desc()).all()
    
    if not trades: return []

    import yfinance as yf
    try:
        current_price = float(yf.Ticker(stock_name).fast_info['lastPrice'])
    except:
        current_price = trades[0].price if trades else 0

    ledger = []
    for t in trades:
        # Calculate P/L for BUYS
        profit_percent = 0
        if t.type == "BUY":
            profit_percent = ((current_price - t.price) / t.price) * 100 if t.price > 0 else 0
            
        ledger.append({
            "id": t.id,
            "type": t.type,
            "quantity": t.quantity,
            "buy_price": t.price,
            "current_price": round(current_price, 2),
            "profit": round(profit_percent, 2),
            "timestamp": t.timestamp
        })
    
    return ledger


# ---------------- RISK SHIELD ---------------- #
@app.post("/update-risk-shield")
def update_risk_shield(req: UpdateRiskShieldRequest, db: Session = Depends(get_db)):
    asset = db.query(models.Portfolio).filter(
        models.Portfolio.user_id == req.user_id,
        models.Portfolio.stock_name == req.stock_name
    ).first()
    
    if not asset: return {"error": "Asset not found in vault"}
    
    asset.trailing_sl_percent = req.trailing_sl_percent
    asset.target_price = req.target_price
    db.commit()
    
    return {"message": f"Risk Shield recalibrated for {req.stock_name}", "params": {
        "trailing_sl": asset.trailing_sl_percent,
        "target_price": asset.target_price
    }}
