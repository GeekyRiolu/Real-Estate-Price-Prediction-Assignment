Real Estate Price Prediction and System Design

## Introduction

Welcome to our machine learning internship assignment! This project is designed to assess your skills in building a complete, end-to-end machine learning pipeline. You will work with a real-world dataset of property listings scraped from real estate auction websites, facing challenges like messy data, heterogeneous sources, and unstructured text.

Your goal is to build a robust price prediction model and design a system capable of serving predictions in a production setting.

**A Note on Our Philosophy**: We don't expect you to be an expert in every tool mentioned. This assignment is a challenge to see how you approach complex problems, how you learn, and the progress you make. We value your ability to implement solutions and learn on the fly. Focus on what you can do best first, and demonstrate your problem-solving process.

## The Dataset

You will be working with property data from two different sources, provided in two formats:

1.  A single JSON file: `baanknet_property_details.json`
2.  A directory containing thousands of individual JSON files: `property_details/`

These sources have **very different structures**. This is a deliberate choice to simulate a real-world data integration problem.

**Source 1: `baanknet_property_details.json`**
This file contains a JSON array where each object is a property. A snippet for a single property is shown below:
```json
// ... list starts
{
  "status": 1,
  "respData": {
    "summaryDesc": "LAND AND BUILDING AT PLOT NO.95...",
    "propertyPrice": 7545000.0,
    "city": "Chennai",
    // ... other nested fields
  },
  "property_id": "209"
}
// ... list continues
```

**Source 2: `property_details/` directory**
This directory contains thousands of JSON files, where each file represents a single property. The structure of these files is different from the first source. Here is an example from `property_3-shops-in-yogi-plaza-puna-surat.json`:
```json
{
  "success": true,
  "data": {
    "address": "Shop No 1 To 3, Ground Floor, Yogi Plaza,  Puna, Surat",
    "name": "3 Shops in Yogi Plaza, Puna, Surat",
    "reserve_price": 7000000,
    "city": "Surat",
    // ... other fields
  }
}
```

Your first major task is to write a robust data ingestion script that can parse all these files, extract and harmonize relevant information into a common schema, and create a single, unified dataset.

## Tasks

### 1. Data Engineering Pipeline

- **Parse Heterogeneous JSON**: Write a Python script to parse both `baanknet_property_details.json` and the JSON files in the `property_details/` directory.
- **Schema Mapping**: Your primary challenge is to design a unified schema. Identify corresponding fields (e.g., `propertyPrice` vs. `reserve_price`). You will need to make intelligent decisions about which fields to keep, how to rename them for consistency, and how to handle fields that exist in one dataset but not the other.
- **Create Unified DataFrame**: Combine the data into a single Pandas DataFrame.
- **Data Cleaning**:
    - Standardize units (e.g., convert all area measurements like "SQ.FT.", "SFT", "sq mtr" to a single unit).
    - Clean and standardize categorical values (e.g., `city`, `propertyType`).
    - Handle outliers using a statistically sound approach.
- **Handle Missing Values**: Systematically identify missing values. Implement and justify your strategy (e.g., mean/median/mode imputation, model-based imputation, or removal). Analyze the impact of your chosen method.

### 2. Feature Engineering

This is a critical part of the assignment. We are looking for creativity and insight.

- **Text-based Features**: From fields like `summaryDesc`, `description`, `name`, and `address`, engineer new features. Use regular expressions and text processing to extract:
    - Property size and dimensions (e.g., "471.50 SQ.FT.", "999 SFT SBUA").
    - Number of floors, rooms, bathrooms, etc.
    - Presence of specific amenities (e.g., "parking", "garden", "garage").
- **Date/Time Features**: Extract useful features from date columns (e.g., day of the week, month, time until the auction ends).
- **Categorical Features**: Encode categorical features. Experiment with and justify your choice of encoding strategy (e.g., one-hot, target encoding, feature embedding).
- **Feature Interactions**: Explore and create new features from interactions between existing ones.

### 3. Natural Language Processing (NLP) - Information Extraction

- **Named Entity Recognition (NER)**: Extract entities from text fields. You can start with a robust rule-based or regex-based extraction system. If you want a challenge, you can optionally try training a custom NER model using libraries like spaCy or Transformers. The goal is to extract:
    - **Location**: Specific addresses, landmarks, neighborhoods.
    - **Property Attributes**: Number of bedrooms/bathrooms, total area, floor number.
    - **Amenities**: Parking, swimming pool, etc.
- **Add to DataFrame**: Integrate the extracted entities as new columns in your DataFrame. Evaluate the accuracy of your extraction process on a small, manually annotated sample.

### 4. Predictive Modeling

- **Establish a Baseline**: Start by building a simple baseline model (e.g., Linear Regression) to set a performance benchmark.
- **Model Selection**: Experiment with several more advanced regression models (e.g., XGBoost, LightGBM, CatBoost, or Neural Networks). Justify your final model choice.
- **Training and Tuning**: Use a robust validation strategy like k-fold cross-validation. Perform hyperparameter tuning to optimize your model's performance.
- **Experiment Tracking**: Use a tool like **MLflow** or **Weights & Biases** to log your experiments. For each run, you should track:
    - The code version (Git commit hash).
    - Hyperparameters.
    - Evaluation metrics (R-squared, MAE, RMSE).
    - The trained model file as an artifact.
- **Evaluation**: Evaluate your model on the test set using multiple metrics (R-squared, MAE, RMSE).
- **Model Interpretability**: Use techniques like SHAP or LIME to explain your model's predictions. What are the most important features driving the price?

### 5. Image Analysis (Optional Stretch Goal)

- **Image-based Features**: If a property has images (`propertyPhoto` field), use a pre-trained model (like ResNet, VGG, EfficientNet) to extract image features. You could classify property condition ("modern", "old", "needs renovation") or type ("apartment", "house", "commercial"). You may need to manually label a small subset of images.
- **Integrate with Main Model**: Add the image-based features to your main DataFrame and assess if they improve the prediction accuracy.

### 6. Model Deployment

- **Build a REST API**: Create a web service using a framework like **FastAPI** or **Flask** that exposes your trained model.
    - The API should have a `/predict` endpoint that accepts a JSON payload with property features and returns the predicted price.
    - Include robust input validation and error handling.
- **Testing**: Write unit or integration tests for your API endpoint. For example, using `pytest` or `unittest`, you can test the `/predict` endpoint with typical inputs, malformed data, and edge cases to ensure it behaves as expected.
- **Containerization (Optional Stretch Goal)**: Write a `Dockerfile` to containerize your application. This demonstrates an understanding of modern deployment practices.

### 7. Scalability and System Design

In your report, include a section addressing the following hypothetical scenario:
- **Problem**: Your service is becoming popular, and you now need to process 1 million new property listings per day and serve thousands of prediction requests per minute.
- **Task**: Briefly describe a high-level system architecture that could handle this scale. Discuss your choice of technologies for data ingestion, processing, storage, model training/re-training, and serving. Think about message queues (e.g., RabbitMQ, Kafka), databases (SQL vs. NoSQL), batch vs. stream processing, and model versioning.

### 8. Workflow Orchestration (Optional Stretch Goal)

- **Build a DAG Pipeline**: Automate your entire machine learning workflow by creating a Directed Acyclic Graph (DAG). Use a workflow orchestrator like **Apache Airflow**, **Prefect**, or **Dagster**.
- **Pipeline Structure**: Your DAG should consist of at least the following tasks, which should run in sequence:
    1.  `data_ingestion`: Kicks off the process.
    2.  `data_validation`: Checks if the raw data has the expected format.
    3.  `data_preparation`: Runs your cleaning and schema mapping scripts.
    4.  `feature_engineering`: Creates new features for the model.
    5.  `model_training`: Trains the model, tunes hyperparameters, and logs experiments (re-using your tracking setup).
    6.  `model_evaluation`: Evaluates the model on the test set and logs the results.
    7.  `model_validation`: Compares the new model's performance against a baseline or the previously deployed model. If the new model is better, it gets "promoted."

## Suggested Project Structure

To help you organize your project, we recommend the following structure:

```
.
├── data/
│   ├── baanknet_property_details.json
│   └── property_details/
├── notebooks/
│   └── exploratory_data_analysis.ipynb
├── src/
│   ├── data_processing.py
│   ├── feature_engineering.py
│   ├── train.py
│   └── app.py (api)
├── tests/
│   └── test_app.py
├── models/
│   └── price_predictor.pkl
├── requirements.txt
├── report.md
└── Dockerfile (Optional)
```

## Deliverables

1.  **Source Code**: A well-organized and commented set of Python scripts or notebooks covering all tasks. Your project should follow the suggested structure where applicable.
2.  **Requirements File**: A `requirements.txt` file with all dependencies.
3.  **Saved Model**: The final trained model saved in a file (e.g., using `pickle` or `joblib`).
4.  **API Application**: The complete source code for your FastAPI/Flask application.
5.  **Report**: A report in Markdown or PDF summarizing your approach, key findings, and model performance. It should include:
    - Data cleaning and feature engineering decisions.
    - Model evaluation results and visualizations from your experiment tracker.
    - Model interpretation analysis (e.g., SHAP plots).
    - The high-level system design for scalability.
6.  **(Optional Stretch Goal)** The Python script defining your Airflow/Prefect/Dagster pipeline.
7.  **(Optional Stretch Goal)** A `Dockerfile` for your web service.

## Evaluation Criteria

- **Code Quality**
- **Methodological Rigor**
- **Model Accuracy and Evaluation**
- **Creativity in Problem Solving**
- **Scalability and System Design**
- **Workflow Automation and Experiment Tracking**
- **Communication and Documentation**

Don’t worry about completing everything perfectly. We value curiosity, clear thinking, and how you approach problems—even more than just accuracy. **We are most interested in the progress you make on this assignment; we do not expect you to solve everything.** Have fun! 