from flask import Flask, render_template, request
import os
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib
from lime.lime_tabular import LimeTabularExplainer
import matplotlib.pyplot as plt

matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)
# ===========================
# Analytics Data
# ===========================

analytics_data = {
    "total_records": 0,
    "benign_count": 0,
    "attack_count": 0,
    "attack_percentage": 0
}

# ===========================
# Upload Folder
# ===========================

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join("static", "shap_images"), exist_ok=True)

# ===========================
# Load Model Files
# ===========================

MODEL_PATH = "models/RandomForest_NIDS.pkl"
ENCODER_PATH = "models/LabelEncoder.pkl"
FEATURES_PATH = "models/Selected_Features.pkl"

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
selected_features = joblib.load(FEATURES_PATH)

# SHAP Explainer
explainer = shap.TreeExplainer(model)
lime_explainer = LimeTabularExplainer(
    training_data=np.zeros((1, len(selected_features))),
    feature_names=selected_features,
    class_names=label_encoder.classes_,
    mode="classification"
)

# ===========================
# Home Page
# ===========================

@app.route("/")
def home():
    return render_template("index.html")

# ===========================
# Prediction Page
# ===========================

@app.route("/prediction")
def prediction():
    return render_template(
        "prediction.html",
        features=selected_features
    )
@app.route("/predict", methods=["POST"])
def predict():

    try:

        # ----------------------------
        # Check CSV Upload
        # ----------------------------

        if "csv_file" not in request.files:
            return render_template(
                "prediction.html",
                error="Please upload a CSV file."
            )

        file = request.files["csv_file"]

        if file.filename == "":
            return render_template(
                "prediction.html",
                error="Please choose a CSV file."
            )

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        # ----------------------------
        # Read CSV
        # ----------------------------

        df = pd.read_csv(filepath)

        if "Label" in df.columns:
            df = df.drop(columns=["Label"])

        df = df[selected_features]

        print("CSV Loaded Successfully")
        print(df.head())

        # ----------------------------
        # Predictions
        # ----------------------------

        predictions = model.predict(df)

        probabilities = model.predict_proba(df)

        attack_names = label_encoder.inverse_transform(predictions)

        # ----------------------------
        # Analytics Statistics
        # ----------------------------

        total_records = len(attack_names)

        benign_count = sum(
            attack == "Benign"
            for attack in attack_names
        )

        attack_count = total_records - benign_count

        attack_percentage = round(
            (attack_count / total_records) * 100,
            2
        )

        analytics_data["total_records"] = total_records
        analytics_data["benign_count"] = benign_count
        analytics_data["attack_count"] = attack_count
        analytics_data["attack_percentage"] = attack_percentage

        # ----------------------------
        # Attack Counts
        # ----------------------------

        attack_counts = pd.Series(
            attack_names
        ).value_counts()

        analytics_data["most_common_attack"] = attack_counts.idxmax()

        analytics_data["most_common_count"] = int(
            attack_counts.max()
        )

        # ----------------------------
        # Pie Chart
        # ----------------------------

        plt.figure(figsize=(6,6))

        plt.pie(
            attack_counts.values,
            labels=attack_counts.index,
            autopct="%1.1f%%",
            startangle=90
        )

        plt.title("Attack Distribution")

        pie_path = os.path.join(
            app.static_folder,
            "shap_images",
            "pie_chart.png"
        )

        plt.savefig(
            pie_path,
            dpi=120,
            bbox_inches="tight"
        )

        plt.close()

        analytics_data["pie_chart"] = "shap_images/pie_chart.png"

        # ----------------------------
        # Bar Chart
        # ----------------------------

        plt.figure(figsize=(8,5))

        attack_counts.plot(
            kind="bar",
            color="steelblue"
        )

        plt.title("Attack Frequency")
        plt.xlabel("Attack Type")
        plt.ylabel("Count")

        plt.xticks(rotation=45, ha="right")

        bar_path = os.path.join(
            app.static_folder,
            "shap_images",
            "bar_chart.png"
        )

        plt.tight_layout()

        plt.savefig(
            bar_path,
            dpi=120,
            bbox_inches="tight"
        )

        plt.close()

        analytics_data["bar_chart"] = "shap_images/bar_chart.png"

        # ----------------------------
        # Confidence Histogram
        # ----------------------------

        confidence_scores = np.max(
            probabilities,
            axis=1
        ) * 100

        plt.figure(figsize=(8,5))

        plt.hist(
            confidence_scores,
            bins=10,
            color="skyblue",
            edgecolor="black"
        )

        plt.title("Prediction Confidence Distribution")
        plt.xlabel("Confidence (%)")
        plt.ylabel("Number of Predictions")

        histogram_path = os.path.join(
            app.static_folder,
            "shap_images",
            "confidence_histogram.png"
        )

        plt.tight_layout()

        plt.savefig(
            histogram_path,
            dpi=120,
            bbox_inches="tight"
        )

        plt.close()

        analytics_data["confidence_chart"] = "shap_images/confidence_histogram.png"

        print("Predictions:", attack_names)

        # ----------------------------
        # SHAP Explanation
        # ----------------------------
        # SHAP Explanation
        # ----------------------------

        sample = df.iloc[:20]
        sample = df.iloc[:20]

        shap_values = explainer(sample)

        plt.figure(figsize=(7,4))

        shap.plots.bar(
            shap_values[:, :, 0],
            max_display=10,
            show=False
        )

        shap_path = os.path.join(
            app.static_folder,
            "shap_images",
            "summary.png"
        )

        plt.savefig(
            shap_path,
            dpi=120,
            bbox_inches="tight"
        )

        plt.close()

        # ----------------------------
        # LIME Explanation
        # ----------------------------

        lime_exp = lime_explainer.explain_instance(
            sample.iloc[0].values,
            model.predict_proba,
            num_features=10
        )

        lime_path = os.path.join(
            app.static_folder,
            "shap_images",
            "lime.html"
        )

        lime_exp.save_to_file(lime_path)

        # ----------------------------
        # Results Table
        # ----------------------------

        results = []

        for i in range(len(df)):

            confidence = round(
                np.max(probabilities[i]) * 100,
                2
            )

            results.append({
                "record": i + 1,
                "prediction": attack_names[i],
                "confidence": confidence
            })

        return render_template(
            "prediction.html",
            results=results,
            filename=file.filename,
            total_records=len(df),
            shap_image="shap_images/summary.png",
            lime_file="shap_images/lime.html"
        )

    except Exception as e:

        return render_template(
            "prediction.html",
            error=str(e)
        )
# ===========================
# Analytics
# ===========================




# ===========================
# About
# ===========================

@app.route("/analytics")
def analytics():

    return render_template(
        "analytics.html",
        analytics=analytics_data
    )

# ===========================
# Run App
# ===========================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
    