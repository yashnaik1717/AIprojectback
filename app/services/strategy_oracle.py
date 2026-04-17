def analyze_macro_headlines(articles):
    """
    Analyzes a list of news headlines and generates 'If/Then' scenarios 
    based on sectoral sensitivity to macro-economic drivers.
    """
    scenarios = []
    
    # 🏛️ Sectoral Sensitivity Map
    # Mapping keywords to specific sector impacts
    MARKET_RULES = [
        {
            "keywords": ["RBI", "Interest Rate", "Repo Rate", "Inflation"],
            "drivers": ["RBI Policy / Inflation"],
            "impacts": [
                "IF RBI Hikes: Banking (Nifty Bank) may see margin pressure; Realty/Auto demand might cool.",
                "IF RBI Pauses: Stability in rate-sensitives (HDFC, ICICI, SBI) expected."
            ]
        },
        {
            "keywords": ["Crude", "Oil", "Brent"],
            "drivers": ["Global Energy Prices"],
            "impacts": [
                "IF Crude Surges: Input costs for Paints, Tire, and Aviation stocks will spike (+Inflation).",
                "IF Crude Slumps: Margin expansion expected for OMCs and logistics players."
            ]
        },
        {
            "keywords": ["FED", "US Inflation", "NASDAQ", "US Yield"],
            "drivers": ["US Federal Policy"],
            "impacts": [
                "IF FED Hikes: Capital outflow from EM (India) likely; Dollar strengthens; IT stocks (TCS/INFY) may see volatility.",
                "IF FED Pauses: Improvement in global risk sentiment; FII inflows into Indian large-caps expected."
            ]
        },
        {
            "keywords": ["War", "Conflict", "Geopolitical"],
            "drivers": ["Geopolitical Risk"],
            "impacts": [
                "IF Tensions Escalate: Safe-haven assets (Gold/USD) will rally; Market volatility (VIX) will spike.",
                "IF Diplomacy Prevails: Relief rally in equity benchmarks likely."
            ]
        }
    ]

    detected_drivers = set()

    for article in articles:
        title = article.get("title", "").upper()
        for rule in MARKET_RULES:
            if any(kw in title for kw in rule["keywords"]):
                detected_drivers.add(rule["drivers"][0])
                scenarios.extend(rule["impacts"])

    # Final result construction
    if not scenarios:
        return {
            "hypothesis": "No major macro-volatility drivers detected in current stream.",
            "strategy": "Continue tracking individual sector breakouts."
        }
    
    # Deduplicate scenarios
    unique_scenarios = list(set(scenarios))
    
    return {
        "hypothesis": f"Macro analysis of {', '.join(list(detected_drivers))} detected.",
        "scenarios": unique_scenarios[:3] # Show top 3 most relevant
    }
