import sys
import os
import time

# Add the app directory to sys.path to import telegram utility
sys.path.append(os.path.join(os.getcwd(), 'app'))

try:
    from app.utils.telegram import send_telegram
except ImportError:
    # Try alternate path if running from root
    sys.path.append(os.getcwd())
    from app.utils.telegram import send_telegram

def test_broadcast():
    print("Initializing Telegram Alert Matrix Test...")
    
    # 1. INITIAL RISK BUFFER HIT
    msg_1 = """
🚨 INITIAL RISK BUFFER HIT

Node: TEST_NODE
Asset: **RELIANCE**
---------------------------
💰 Buy Price: ₹2,500.00
🚀 Peak Price: ₹2,580.00
🛑 Exit Floor: ₹2,375.00
📊 Current: ₹2,370.00

❌ *Condition Met: Liquidation Advised.*
"""
    print("Sending Stage 1: Initial Risk...")
    send_telegram(msg_1)
    time.sleep(2)

    # 2. CAPITAL PROTECTION BREACH
    msg_2 = """
🛡️ CAPITAL PROTECTION BREACH

Node: TEST_NODE
Asset: **TATASTEEL**
---------------------------
💰 Buy Price: ₹150.00
🚀 Peak Price: ₹172.00
🛑 Exit Floor: ₹150.00
📊 Current: ₹148.50

❌ *Condition Met: Liquidation Advised.*
"""
    print("Sending Stage 2: Capital Protection...")
    send_telegram(msg_2)
    time.sleep(2)

    # 3. PROFIT LOCK-IN VIOLATION
    msg_3 = """
💰 PROFIT LOCK-IN VIOLATION

Node: TEST_NODE
Asset: **HDFCBANK**
---------------------------
💰 Buy Price: ₹1,400.00
🚀 Peak Price: ₹1,680.00
🛑 Exit Floor: ₹1,550.00
📊 Current: ₹1,545.00

❌ *Condition Met: Liquidation Advised.*
"""
    print("Sending Stage 3: Profit Locked...")
    send_telegram(msg_3)
    
    print("\nMatrix Test Complete. Please check your Telegram.")

if __name__ == "__main__":
    test_broadcast()
