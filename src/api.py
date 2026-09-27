from catboost import CatBoostClassifier
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from src.observability import tracer

app = FastAPI(title="AML Fraud Detection API")


class Transaction(BaseModel):
    from_bank: int
    to_bank: int
    amount_received: float
    amount_paid: float


class Prediction(BaseModel):
    is_laundering: int
    probability: float


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/predict", response_model=Prediction)
def predict(transaction: Transaction):
    with tracer.start_as_current_span("predict_transaction") as span:
        span.set_attribute("from_bank", transaction.from_bank)
        span.set_attribute("amount_received", transaction.amount_received)

        model = CatBoostClassifier()
        model.load_model("models/aml_model.cbm")

        data = pd.DataFrame([{
            "From Bank": transaction.from_bank,
            "To Bank": transaction.to_bank,
            "Amount Received": transaction.amount_received,
            "Amount Paid": transaction.amount_paid
        }])

        prediction = model.predict(data)[0]
        probability = model.predict_proba(data)[0][1]

        span.set_attribute("prediction", int(prediction))
        span.set_attribute("probability", float(probability))

        return Prediction(
            is_laundering=int(prediction),
            probability=float(probability)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)