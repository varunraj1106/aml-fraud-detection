import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from data_loader import load_data, preprocess, split_data


def test_load_data():
    """Test that data loads and has expected columns."""
    df = load_data("data/HI-Small_Trans.csv")
    assert not df.empty, "DataFrame should not be empty"
    assert "Is Laundering" in df.columns, "Target column missing"


def test_preprocess():
    """Test that preprocessing fills missing values."""
    df = pd.DataFrame({
        "From Bank": [1, None, 3],
        "To Bank": [4, 5, None],
        "Amount Received": [100.0, None, 300.0],
        "Amount Paid": [100.0, 200.0, None],
        "Is Laundering": [0, 1, 0]
    })
    result = preprocess(df)
    assert result[["From Bank", "To Bank", "Amount Received", "Amount Paid"]].isnull().sum().sum() == 0, "No nulls after preprocess"


def test_split_data():
    """Test that split produces correct proportions."""
    df = pd.DataFrame({
        "From Bank": range(100),
        "To Bank": range(100),
        "Amount Received": range(100),
        "Amount Paid": range(100),
        "Is Laundering": [0] * 80 + [1] * 20
    })
    X_train, X_test, y_train, y_test = split_data(df)
    assert len(X_train) == 80, "Train should be 80%"
    assert len(X_test) == 20, "Test should be 20%"