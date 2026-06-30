import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
data = pd.read_csv("phishing.csv",sep="\t")
print(data.columns)

# Features
X = data.drop("label", axis=1)

# Target
y = data["label"]

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained successfully!")