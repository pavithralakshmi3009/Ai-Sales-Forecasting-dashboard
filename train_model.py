#!/usr/bin/env python3
"""
Offline Model Training Script
==============================
This script trains the Linear Regression model on the sales dataset
and saves the trained model to models/sales_model.pkl.

This is meant to be run LOCALLY by developers, NOT on the deployed server.

Usage:
    python train_model.py
    python train_model.py --csv path/to/custom_data.csv

The deployed Vercel backend only loads the pre-trained .pkl file.
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
# pyrefly: ignore [missing-import]
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Resolve paths relative to this script
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = BASE_DIR / "dataset" / "current_dataset.csv"
MODEL_PATH = BASE_DIR / "models" / "sales_model.pkl"


def train(csv_path: Path):
    """Train a Linear Regression model and save it to disk."""
    print(f"📂 Reading dataset from: {csv_path}")

    if not csv_path.exists():
        print(f"❌ Error: Dataset file not found at {csv_path}")
        sys.exit(1)

    data = pd.read_csv(csv_path)

    # Validate columns
    if "Month" not in data.columns or "Sales" not in data.columns:
        print("❌ Error: CSV must contain 'Month' and 'Sales' columns.")
        print(f"   Found columns: {list(data.columns)}")
        sys.exit(1)

    print(f"📊 Dataset loaded: {len(data)} rows")
    print(f"   Months: {data['Month'].min()} → {data['Month'].max()}")
    print(f"   Sales range: ₹{data['Sales'].min():,.2f} → ₹{data['Sales'].max():,.2f}")

    X = data[["Month"]]
    y = data["Sales"]

    # Train model
    print("\n🧠 Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X, y)

    # Evaluate
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    print(f"✅ Model trained successfully!")
    print(f"   R² Accuracy: {r2:.6f} ({r2 * 100:.2f}%)")
    print(f"   Coefficient: {model.coef_[0]:.4f}")
    print(f"   Intercept: {model.intercept_:.4f}")

    # Save model
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\n💾 Model saved to: {MODEL_PATH}")

    # Save model weights to JSON for lightweight prediction
    import json
    model_json_path = MODEL_PATH.with_suffix('.json')
    with open(model_json_path, 'w') as f:
        json.dump({'coef': float(model.coef_[0]), 'intercept': float(model.intercept_)}, f)
    print(f"💾 Model weights saved to: {model_json_path}")

    # Sample predictions
    print("\n📈 Sample Predictions:")
    for month in [13, 14, 15]:
        pred = model.predict([[month]])[0]
        print(f"   Month {month}: ₹{pred:,.2f}")

    # Optionally save metadata to database
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        try:
            from api._services.database import save_model_metadata
            save_model_metadata(
                accuracy=round(float(r2), 4),
                algorithm="Linear Regression",
                dataset_size=len(data)
            )
            print("\n📝 Model metadata saved to database.")
        except Exception as e:
            print(f"\n⚠️  Could not save metadata to database: {e}")
    else:
        print("\n💡 Tip: Set DATABASE_URL to also save model metadata to Supabase.")

    print("\n🎉 Training complete! Commit models/sales_model.pkl to your repository.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train the Sales Forecasting Linear Regression model offline."
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=str(DEFAULT_CSV),
        help=f"Path to the CSV dataset (default: {DEFAULT_CSV})"
    )
    args = parser.parse_args()

    train(Path(args.csv))
