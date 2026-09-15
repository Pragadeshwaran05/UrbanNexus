import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# 1. PATHS
# ============================================================

DATASET_PATH = "dataset/urbannexus_dependency_training.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "dependency_model.pkl")


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("\n========================================")
print("       URBANNEXUS ML TRAINING")
print("========================================")

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Dataset loaded successfully.")
print(f"Total records: {len(df)}")
print(f"Total columns: {len(df.columns)}")


# ============================================================
# 3. CHECK DATA
# ============================================================

print("\nChecking dataset...")

print("\nMissing values:")
print(df.isnull().sum())

# Fill missing values
text_columns = [
    "problem_a",
    "problem_b",
    "category_a",
    "category_b",
    "description_a",
    "description_b",
    "location",
    "severity_a",
    "severity_b",
    "relationship"
]

for column in text_columns:
    if column in df.columns:
        df[column] = df[column].fillna("Unknown").astype(str)

numeric_columns = [
    "distance_km",
    "time_difference_hours",
    "nearby_frequency",
    "text_similarity"
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)


# ============================================================
# 4. CREATE COMBINED TEXT
# ============================================================

print("\nCreating text features...")

df["combined_text"] = (
    df["problem_a"] + " " +
    df["problem_b"] + " " +
    df["description_a"] + " " +
    df["description_b"]
)


# ============================================================
# 5. FEATURES AND TARGET
# ============================================================

X = df[
    [
        "combined_text",
        "category_a",
        "category_b",
        "location",
        "severity_a",
        "severity_b",
        "distance_km",
        "time_difference_hours",
        "nearby_frequency",
        "text_similarity"
    ]
]

y = df["dependency_label"]


print("\nTarget distribution:")
print(y.value_counts())


# ============================================================
# 6. TRAIN / TEST SPLIT
# ============================================================

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")


# ============================================================
# 7. PREPROCESSING
# ============================================================

text_vectorizer = TfidfVectorizer(
    max_features=3000,
    ngram_range=(1, 2),
    lowercase=True
)

categorical_features = [
    "category_a",
    "category_b",
    "location",
    "severity_a",
    "severity_b"
]

numeric_features = [
    "distance_km",
    "time_difference_hours",
    "nearby_frequency",
    "text_similarity"
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "text",
            text_vectorizer,
            "combined_text"
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "numeric",
            StandardScaler(),
            numeric_features
        )
    ]
)


# ============================================================
# 8. MACHINE LEARNING MODEL
# ============================================================

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42
)


# ============================================================
# 9. COMPLETE PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            model
        )
    ]
)


# ============================================================
# 10. TRAIN
# ============================================================

print("\n========================================")
print("Training ML model...")
print("========================================")

pipeline.fit(
    X_train,
    y_train
)

print("Model training completed!")


# ============================================================
# 11. PREDICTION
# ============================================================

print("\nGenerating predictions...")

y_pred = pipeline.predict(X_test)


# ============================================================
# 12. MODEL EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)


print("\n========================================")
print("          MODEL PERFORMANCE")
print("========================================")

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# 13. SAVE MODEL
# ============================================================

print("\nSaving model...")

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    pipeline,
    MODEL_PATH
)

print(f"\nModel saved successfully:")
print(MODEL_PATH)


# ============================================================
# 14. TEST WITH A NEW URBAN PROBLEM
# ============================================================

print("\n========================================")
print("        TESTING NEW PROBLEM")
print("========================================")

new_problem = pd.DataFrame(
    [
        {
            "combined_text":
                "blocked stormwater drain near main road "
                "causing water accumulation",
            "category_a":
                "Drainage",
            "category_b":
                "Flooding",
            "location":
                "Anna Nagar",
            "severity_a":
                "HIGH",
            "severity_b":
                "HIGH",
            "distance_km":
                0.4,
            "time_difference_hours":
                2.0,
            "nearby_frequency":
                8,
            "text_similarity":
                0.85
        }
    ]
)

prediction = pipeline.predict(
    new_problem
)

probability = pipeline.predict_proba(
    new_problem
)

print("\nInput problem:")
print(
    "Blocked stormwater drain near main road"
)

print("\nPrediction:")

if prediction[0] == 1:
    print("DEPENDENCY DETECTED")
else:
    print("NO DEPENDENCY DETECTED")

print("\nDependency probability:")

print(
    f"Probability of dependency: "
    f"{probability[0][1] * 100:.2f}%"
)

print("\n========================================")
print("       TRAINING COMPLETED")
print("========================================")