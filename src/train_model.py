import mlflow
import mlflow.catboost
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from data_loader import load_data, preprocess, split_data


def train(X_train, y_train, params: dict) -> CatBoostClassifier:
    """Train CatBoost model with given parameters."""
    model = CatBoostClassifier(**params, verbose=0)
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test) -> dict:
    """Evaluate model and return metrics."""
    predictions = model.predict(X_test)
    return {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions),
        "recall": recall_score(y_test, predictions),
        "f1": f1_score(y_test, predictions)
    }


def train_with_tracking(data_path: str, params: dict):
    """Train model with MLflow experiment tracking."""
    # Load and prepare data
    df = load_data(data_path)
    df = preprocess(df)
    X_train, X_test, y_train, y_test = split_data(df)

    # Start MLflow tracking
    mlflow.set_experiment("aml-fraud-detection")

    with mlflow.start_run():
        # Log parameters
        mlflow.log_params(params)
        mlflow.log_param("data_path", data_path)
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))

        # Train
        model = train(X_train, y_train, params)

        # Evaluate and log metrics
        metrics = evaluate(model, X_test, y_test)
        mlflow.log_metrics(metrics)

        # Log model
        mlflow.catboost.log_model(model, "model")

        # Log feature importance
        importance = dict(zip(X_train.columns, model.feature_importances_))
        for feat, imp in importance.items():
            mlflow.log_metric(f"importance_{feat}", imp)

        print(f"Metrics: {metrics}")
        return model, metrics


if __name__ == "__main__":
    params = {
        "iterations": 500,
        "depth": 8,
        "learning_rate": 0.05,
        "random_seed": 42,
        "auto_class_weights": "Balanced",
        "l2_leaf_reg": 3
    }
    train_with_tracking("data/HI-Small_Trans.csv", params)