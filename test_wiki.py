import pandas as pd

try:
    url = "https://en.wikipedia.org/wiki/NIFTY_500"
    tables = pd.read_html(url)
    print("Found tables on Wikipedia!")
    for i, t in enumerate(tables):
        print(f"Table {i} rows: {len(t)}")
        if 'Symbol' in t.columns:
            print("Symbols:", t['Symbol'].head())
except Exception as e:
    print(f"Wikipedia fetch error: {e}")
