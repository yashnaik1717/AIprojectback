from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, unique=True, index=True)
    capital = Column(Float)
    otp_code = Column(String, nullable=True)


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_name = Column(String)
    quantity = Column(Float)
    buy_price = Column(Float)
    ai_score = Column(Float)
    rsi = Column(Float)
    explanation = Column(String)
    highest_price = Column(Float, default=0.0)
    trailing_sl_percent = Column(Float, default=5.0)
    target_price = Column(Float, nullable=True)


class FundHistory(Base):
    __tablename__ = "fund_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)
    type = Column(String)


class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_name = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    timestamp = Column(String) # Stored as IST formatted string
    type = Column(String) # 'BUY' or 'SELL'