import feedparser
import re
import yfinance as yf
from datetime import datetime, timedelta
from app.services.strategy_oracle import analyze_macro_headlines

# 🏛️ Macro Calendar Data for 2026 (Indian Market)
MACRO_CALENDAR = [
    {"title": "RBI Monetary Policy Committee (MPC) Meeting", "date": "2026-04-03", "type": "Policy", "impact": "CRITICAL"},
    {"title": "India CPI Inflation (March Data)", "date": "2026-04-12", "type": "Macro", "impact": "HIGH"},
    {"title": "India WPI Inflation (March Data)", "date": "2026-04-14", "type": "Macro", "impact": "MED"},
    {"title": "Bank Holiday - Dr. Ambedkar Jayanti", "date": "2026-04-14", "type": "Holiday", "impact": "LOW"},
    {"title": "India Forex Reserves Update", "date": "2026-04-18", "type": "Macro", "impact": "MED"},
    {"title": "RBI Monetary policy meeting (Expected)", "date": "2026-05-05", "type": "Policy", "impact": "CRITICAL"},
]

FEEDS = [
    {"name": "Economic Times", "url": "https://economictimes.indiatimes.com/rss.cms"},
    {"name": "Livemint", "url": "https://www.livemint.com/rss/markets"},
    {"name": "BFSI News", "url": "https://bfsi.economictimes.indiatimes.com/rss/topstories"}
]

def clean_html(text):
    return re.sub('<[^<]+?>', '', text).strip()

def get_temporal_matrix(portfolio_symbols=None):
    """
    Consolidates data into Pass (Historical) and Coming (30-day Projection).
    """
    now = datetime.now()
    horizon = now + timedelta(days=30)
    
    pass_events = []
    coming_events = []

    # 1. 🗃️ PULSE: Aggregate News (Pass)
    processed_titles = set()
    for feed_info in FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:5]: # Take top 5 from each source
                if entry.title.lower() in processed_titles: continue
                
                summary = clean_html(entry.summary if hasattr(entry, 'summary') else "")
                
                # Determine Impact via simple keyword match or oracle
                impact = "MED"
                title_upper = entry.title.upper()
                if any(kw in title_upper for kw in ["CRASH", "SLUMP", "RBI", "FED", "WAR", "SURGE", "RECORD"]):
                    impact = "HIGH"
                
                news_item = {
                    "source": feed_info["name"],
                    "title": entry.title,
                    "summary": summary,
                    "date": entry.published if hasattr(entry, 'published') else now.strftime("%Y-%m-%d"),
                    "impact": impact,
                    "link": entry.link,
                    "status": "PASS"
                }
                pass_events.append(news_item)
                processed_titles.add(entry.title.lower())
        except Exception as e:
            print(f"Error fetching {feed_info['name']}: {e}")

    # 2. 🔮 PROJECTION: Upcoming Macro Events
    for event in MACRO_CALENDAR:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d")
        if now <= event_date <= horizon:
            event["status"] = "COMING"
            coming_events.append(event)
        elif event_date < now:
            # We can also include very recent past macro events in 'Pass'
            if now - event_date < timedelta(days=7):
                event["status"] = "PASS"
                event["source"] = "Macro Oracle"
                pass_events.append(event)

    # 3. 🏦 PROJECTION: Earnings Calendar (for Portfolio)
    if portfolio_symbols:
        for symbol in portfolio_symbols[:5]: # Limit to top 5 for speed
            try:
                ticker = yf.Ticker(symbol)
                cal = ticker.calendar
                if cal and 'Earnings Date' in cal and cal['Earnings Date']:
                    e_date = cal['Earnings Date'][0]
                    # Handle date vs datetime objects
                    if isinstance(e_date, datetime): e_date = e_date.date()
                    
                    event_title = f"{symbol.split('.')[0]} Quarterly Earnings Node"
                    
                    if now.date() <= e_date <= horizon.date():
                        coming_events.append({
                            "title": event_title,
                            "date": e_date.strftime("%Y-%m-%d"),
                            "type": "Earnings",
                            "impact": "HIGH",
                            "status": "COMING"
                        })
                    elif e_date < now.date() and (now.date() - e_date) < timedelta(days=14):
                        pass_events.append({
                           "title": f"{event_title} (COMPLETED)",
                           "date": e_date.strftime("%Y-%m-%d"),
                           "type": "Earnings",
                           "impact": "HIGH",
                           "source": "Corporate Matrix",
                           "status": "PASS"
                        })
            except:
                continue

    # Sort coming events by date
    coming_events = sorted(coming_events, key=lambda x: x["date"])
    # Sort pass events (approximate)
    pass_events = sorted(pass_events, key=lambda x: x.get("date", ""), reverse=True)

    return {
        "pass": pass_events[:15],
        "coming": coming_events
    }
