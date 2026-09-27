import pandas as pd
from sklearn.model_selection import train_test_split


def load_data(path: str) -> pd.DataFrame:
    """Load transaction dataset from CSV."""
    df = pd.read_csv(path)
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare features for the model."""
    feature_cols = [
        "From Bank", "To Bank", "Amount Received",
        "Amount Paid"
    ]
    df = df.copy()
    df[feature_cols] = df[feature_cols].fillna(0)
    return df


def split_data(df: pd.DataFrame, target: str = "Is Laundering", test_size: float = 0.2):
    """Split into train/test sets."""
    feature_cols = ["From Bank", "To Bank", "Amount Received", "Amount Paid"]
    X = df[feature_cols]
    y = df[target]
    return train_test_split(X, y, test_size=test_size, random_state=42)


if __name__ == "__main__":
    df = load_data("data/HI-Small_Trans.csv")
    df = preprocess(df)
    X_train, X_test, y_train, y_test = split_data(df)
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    print(f"Fraud rate: {y_train.mean():.2%}")