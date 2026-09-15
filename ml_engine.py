import os
import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "dependency_model.pkl"
)

_model = None


def load_model():
    global _model

    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Dependency model not found: {MODEL_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

    return _model


def predict_dependency(
    problem_a,
    problem_b,
    category_a="General",
    category_b="General",
    description_a="",
    description_b="",
    location="Unknown",
    distance_km=1.0,
    time_difference_hours=0.0,
    severity_a="MEDIUM",
    severity_b="MEDIUM",
    nearby_frequency=1,
    text_similarity=0.0
):

    model = load_model()

    # Recreate the same combined text used during training
    combined_text = " ".join([
        str(problem_a),
        str(problem_b),
        str(description_a),
        str(description_b)
    ])

    data = pd.DataFrame([{
        "combined_text": combined_text,
        "category_a": category_a,
        "category_b": category_b,
        "location": location,
        "severity_a": severity_a,
        "severity_b": severity_b,
        "distance_km": distance_km,
        "time_difference_hours": time_difference_hours,
        "nearby_frequency": nearby_frequency,
        "text_similarity": text_similarity
    }])

    prediction = model.predict(data)[0]

    probability = 0.0

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(data)[0]
        classes = model.classes_

        if 1 in classes:
            dependency_index = list(classes).index(1)
            probability = float(probabilities[dependency_index])
        else:
            probability = float(max(probabilities))

    return {
        "prediction": int(prediction),
        "dependency_detected": bool(prediction == 1),
        "probability": round(probability * 100, 2)
    }