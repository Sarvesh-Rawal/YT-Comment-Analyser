import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import pickle

#  Loading dataset 
df = pd.read_excel("training data.xlsx")
X = df['cleaned_comments']
y = df['sentiment']

#  Spliting data 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#  extracting features using TF-IDF 
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2)) 
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

#  Training the model 
model = MultinomialNB()
model.fit(X_train_vec, y_train)

#  Evaluating model results 
y_pred = model.predict(X_test_vec)
print('\n',X_test.head(),y_pred)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

#  Saving model and vectorizer for future use
with open("models/sentiment_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
