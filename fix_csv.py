import pandas as pd
import os

# Step 1: Path to raw/ingested data
ingestion_path = os.path.join('artifacts', 'data_ingestion', 'phishing.csv')

# Step 2: If file doesn't exist, create it
if not os.path.exists(ingestion_path):
    os.makedirs(os.path.dirname(ingestion_path), exist_ok=True)
    # Create a dummy dataframe with expected columns
    df = pd.DataFrame(columns=['url', 'label'])
    df.to_csv(ingestion_path, index=False)
    print(f"Created new CSV at {ingestion_path}")
else:
    # Read the CSV
    df = pd.read_csv(ingestion_path)
    print(f"CSV loaded from {ingestion_path}, {len(df)} rows")

# Step 3: Fix/clean data as needed
# For example, drop empty rows
df.dropna(inplace=True)
df.to_csv(ingestion_path, index=False)
print("CSV cleaned and ready for validation")