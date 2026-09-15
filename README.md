# UrbanNexus

### AI-Powered Urban Problem Dependency & Impact Analysis

UrbanNexus is an AI-assisted urban problem intelligence platform designed to help municipal authorities understand how different urban problems are interconnected.

Instead of treating every complaint as an isolated issue, UrbanNexus identifies possible dependencies, root causes, cascading effects, and intervention priorities.

---

## Problem

Urban problems are often interconnected.

For example:

```text
Blocked Drain
      ↓
Waterlogging
      ↓
Road Blockage
      ↓
Traffic Congestion
      ↓
Emergency Response Delay
```

When these problems are handled independently, authorities may address the visible symptom while the underlying cause remains unresolved.

UrbanNexus aims to provide a connected view of urban problems.

---

## Solution

UrbanNexus combines citizen-reported problems, dependency analysis, geospatial information, and AI-assisted analysis to help municipal authorities understand urban problem relationships.

### Core pipeline

```text
Citizen Report
      ↓
Problem Detection
      ↓
Dependency Mapping
      ↓
Root Cause Identification
      ↓
Impact Analysis
      ↓
Priority Intervention
```

---

## Key Features

### Citizen Portal

Citizens can:

- Report urban problems
- Add problem descriptions
- Select problem categories
- Provide location information
- Upload supporting evidence
- Track submitted reports
- View nearby problems
- Receive notifications
- Manage their profile

---

### Municipal Command Center

Municipal officers can:

- View city-wide problem information
- Analyze reported problems
- Identify dependencies
- View high-impact problems
- Track interventions
- Explore problems on a map
- View department information
- Examine AI-assisted problem intelligence

---

### AI-Assisted Dependency Analysis

UrbanNexus analyzes relationships between urban problems.

Example:

```text
Blocked Drain
     ↓
Waterlogging
     ↓
Road Blockage
     ↓
Traffic Congestion
```

The system can identify:

- Potential dependencies
- Dependency strength
- Root causes
- Cascading effects
- Impact level
- Priority level

---

### Problem Intelligence

The Problem Intelligence dashboard provides:

- Citizen reports
- Impact level
- Priority
- Connected problems
- Root cause
- Cascading effects
- AI assessment
- Dependency information

---

### City Problem Map

UrbanNexus provides a map-based view of reported problems using geographic coordinates.

The map helps authorities understand the spatial distribution of urban problems.

---

## AI / Machine Learning

UrbanNexus uses an explainable dependency-analysis approach together with a machine-learning prototype.

The current training pipeline uses a curated UrbanNexus dependency dataset containing:

- Problem pairs
- Problem categories
- Problem descriptions
- Location
- Distance
- Time difference
- Severity
- Nearby problem frequency
- Text similarity
- Dependency relationship
- Dependency strength
- Dependency label

### Machine Learning Pipeline

```text
Training Dataset
      ↓
Data Preprocessing
      ↓
Text Feature Extraction
      ↓
Categorical Features
      ↓
Numerical Features
      ↓
ML Classifier
      ↓
Model Evaluation
      ↓
Saved Model
      ↓
UrbanNexus Application
```

The prototype model predicts whether a relationship exists between two urban problems.

---

## Technology Stack

### Frontend

- HTML
- CSS
- JavaScript
- Jinja2 Templates
- Leaflet.js

### Backend

- Python
- Flask

### Database

- MongoDB
- PyMongo

### Machine Learning

- Python
- Pandas
- Scikit-learn
- TF-IDF
- Logistic Regression
- Joblib

### Maps

- Leaflet
- OpenStreetMap

---

## Project Structure

```text
UrbanNexus/
│
├── app.py
├── database.py
├── dependency_engine.py
├── train_model.py
│
├── dataset/
│   └── urbannexus_dependency_training.csv
│
├── models/
│   └── dependency_model.pkl
│
├── templates/
│   ├── base.html
│   ├── sidebar.html
│   │
│   ├── citizen/
│   │   └── ...
│   │
│   └── municipality/
│       └── ...
│
└── static/
    ├── css/
    ├── js/
    ├── images/
    └── icons/
```

---

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project:

```bash
cd UrbanNexus
```

---

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install flask pymongo pandas scikit-learn joblib
```

If additional packages are required by the current application, install them before running the project.

---

## MongoDB Configuration

UrbanNexus uses MongoDB for storing citizen reports and urban problem information.

Configure your MongoDB connection in the application's database configuration.

Do **not** commit database passwords, connection strings, API keys, or other secrets to GitHub.

Recommended approach:

```text
Environment Variables
        ↓
Database Configuration
        ↓
MongoDB
```

---

## Training the ML Model

Place the training dataset inside:

```text
dataset/
└── urbannexus_dependency_training.csv
```

Run:

```bash
python train_model.py
```

The training process:

1. Loads the dataset
2. Preprocesses text
3. Processes categorical features
4. Processes numerical features
5. Splits the dataset into training and testing data
6. Trains the classifier
7. Evaluates the model
8. Saves the trained model

The model is saved as:

```text
models/dependency_model.pkl
```

---

## Running UrbanNexus

Start the Flask application:

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000/
```

---

## Application Portals

### Citizen Portal

```text
/citizen/dashboard
```

### Municipal Dashboard

```text
/municipality/dashboard
```

### Problem Intelligence

```text
/municipality/intelligence
```

### Dependency Analysis

```text
/municipality/dependencies
```

### Priority Problems

```text
/municipality/priority
```

### Interventions

```text
/municipality/interventions
```

### City Problem Map

```text
/municipality/map
```

### Departments

```text
/municipality/departments
```

---

## Example Dependency Chain

UrbanNexus can represent an urban dependency chain such as:

```text
Illegal Dumping
       ↓
Blocked Drain
       ↓
Waterlogging
       ↓
Road Blockage
       ↓
Traffic Congestion
       ↓
Emergency Response Delay
```

This helps authorities investigate interconnected problems instead of considering each complaint independently.

---

## Dataset

The current ML prototype uses a curated dependency dataset created specifically for UrbanNexus development.

The dataset is intended for:

- Model development
- Prototype testing
- Dependency classification
- Hackathon demonstration

It should not be interpreted as a collection of real municipal observations.

Future versions can incorporate larger real-world municipal datasets and historical citizen reports.

---

## Privacy

UrbanNexus should avoid exposing citizen identity in public problem views.

Citizen-specific information should remain protected while municipal officers receive the information necessary to process the reported problem.

Sensitive information such as:

- Passwords
- Database credentials
- API keys
- Private configuration
- Personal identifiers

must not be committed to the repository.

---

## Future Enhancements

Planned improvements include:

- Advanced NLP models
- Better dependency prediction
- Real historical municipal datasets
- Temporal dependency analysis
- Spatial dependency analysis
- Dynamic dependency graphs
- Root-cause ranking
- Automated intervention recommendations
- Department-level task assignment
- Improved model validation with real-world data
- Real-time urban problem monitoring

---

## Project Goal

UrbanNexus aims to help cities move from:

```text
Complaint-Based Response
```

towards:

```text
Connected Urban Problem Intelligence
```

By understanding relationships between urban problems, authorities can investigate root causes and cascading effects and coordinate interventions across departments.

---

## Disclaimer

UrbanNexus is a hackathon/prototype system.

AI-generated dependency predictions are decision-support information and should be reviewed by appropriate municipal personnel before operational action.