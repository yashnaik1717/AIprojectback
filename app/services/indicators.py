import numpy as np

def calculate_indicators(data_chunk):
    try:
        # Require at least 50 days of data for the 50 SMA
        if data_chunk is None or data_chunk.dropna().empty or len(data_chunk.dropna()) < 50:
            return None

        data = data_chunk.dropna()
        close = data["Close"]
        volume = data["Volume"] if "Volume" in data.columns else None

        last_price = close.iloc[-1]
        score = 0.0
        
        # We will collect successful tests for the explainer!
        passed_tests = []

        # ---------------- 1. Short-Term Trend Check (15 pts) ----------------
        ma_20 = close.rolling(window=20).mean().iloc[-1]
        if last_price > ma_20:
            score += 15
            passed_tests.append("Short-term Uptrend (>20 DMA)")

        # ---------------- 2. Long-Term Trend Check (15 pts) ----------------
        ma_50 = close.rolling(window=50).mean().iloc[-1]
        if last_price > ma_50:
            score += 15
            passed_tests.append("Long-term Uptrend (>50 DMA)")

        # ---------------- 3. Momentum Check (10 pts) ----------------
        momentum = last_price - close.iloc[-10]
        if momentum > 0:
            score += 10
            passed_tests.append("Positive 10-Day Momentum")

        # ---------------- 4. RSI Sweet-Spot Check (10 pts) ----------------
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=14).mean().iloc[-1]
        avg_loss = loss.rolling(window=14).mean().iloc[-1]
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if rs != 0 else 100
        
        # Favorable RSI is between 40 and 65 (growing, but not dangerously overbought)
        if 40 <= rsi <= 68:
            score += 10
            passed_tests.append("Favorable RSI Ratio")
            
        # ---------------- 5. MACD Bullish Crossover Check (15 pts) ----------------
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        
        if macd_line.iloc[-1] > signal_line.iloc[-1]:
            score += 15
            passed_tests.append("MACD Bullish Signal")
            
        # ---------------- 6. Volume Breakout Check (15 pts) ----------------
        if volume is not None and not volume.empty:
            avg_vol_20 = volume.rolling(window=20).mean().iloc[-1]
            if volume.iloc[-1] > avg_vol_20 * 1.2:  # 20% surge above average
                score += 15
                passed_tests.append("Volume Breakout Detected")
        
        # ---------------- 7. Recent Micro-Surge Check (10 pts) ----------------
        # Did it jump >1.5% in the last 3 days?
        percent_surge = ((last_price - close.iloc[-3]) / close.iloc[-3]) * 100
        if percent_surge > 1.5:
            score += 10
            passed_tests.append("3-Day Micro Surge")

        # ---------------- 8. Proximity to 20-DMA Bounce Check (10 pts) ----------------
        # If the price is within 2% of the MA_20, it means it's bouncing optimally, not overextended!
        distance_from_ma20 = (abs(last_price - ma_20) / ma_20) * 100
        if distance_from_ma20 <= 2.5:
            score += 10
            passed_tests.append("Optimal Moving Average Support")

        return {
            "price": round(float(last_price), 2),
            "rsi": round(float(rsi), 2),
            "score": score,
            "passed_tests": passed_tests # Exposing this to AI explainer
        }

    except Exception as e:
        print("Indicator error:", e)
        return None