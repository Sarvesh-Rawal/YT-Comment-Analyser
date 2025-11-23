import pandas as pd
import pickle

def analyze_comments(df: pd.DataFrame) -> pd.DataFrame:

    # Load model and vectorizer
    with open("backend/model/sentiment_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("backend/model/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    # Extract cleaned comments
    comments = df["cleaned_comment"].astype(str)

    # Transform comments into feature vectors
    X_features = vectorizer.transform(comments)
    # 🧾 Predict sentiments
    predictions = model.predict(X_features)

    # 🧩 Add results to DataFrame
    df["sentiment"] = predictions
    return df
