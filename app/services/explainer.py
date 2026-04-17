def generate_explanation(stock):
    tests = stock.get("passed_tests", [])
    
    if not tests:
        return "⚠️ Weak technical setup. Failing major thresholds."
    
    return "📈 Passed Triggers: " + " • ".join(tests)