import os
import pdfplumber
import numpy as np
from sklearn.naive_bayes import GaussianNB
from flask import Flask, render_template, request
import tkinter as tk
from tkinter import filedialog

# Define job openings and their requirements
job_openings = {
    "Cloud Developer": {
        "skills": ["aws", "azure", "gcp", "cloud", "docker", "kubernetes"],
        "min_experience": 2
    },
    "Senior Full Stack Developer": {
        "skills": ["react", "node.js", "javascript", "html5", "css3", "mongodb", "sql"],
        "min_experience": 5
    },
    "Junior Data Scientist": {
        "skills": ["python", "r", "machine learning", "data analysis", "statistics", "sql"],
        "min_experience": 1
    },
    "Java Developer": {
        "skills": ["java", "spring", "hibernate", "javascript", "sql"],
        "min_experience": 2
    }
}

# Pre-trained Naive Bayes model (dummy model for demonstration)
nb_model = GaussianNB()

# Dummy model training for demonstration
X_train = np.array([[80, 5, 1, 3], [60, 3, 3, 1], [90, 6, 0, 4], [40, 2, 4, 1]])  # Example features
y_train = np.array([1, 0, 1, 0])  # Example labels: 1 = Accepted, 0 = Rejected
nb_model.fit(X_train, y_train)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

# Function to analyze resume
def analyze_resume(resume_text, job_requirements):
    required_skills = job_requirements["skills"]
    matched_skills = [skill for skill in required_skills if skill.lower() in resume_text.lower()]
    missing_skills = [skill for skill in required_skills if skill.lower() not in resume_text.lower()]
    skill_percentage = (len(matched_skills) / len(required_skills)) * 100

    # Dummy experience extraction (customize based on your logic)
    experience_years = 2  # Example: extract from text with regex

    # Introduce thresholds for better evaluation
    skill_threshold = 70  # Minimum skill match percentage
    experience_threshold = job_requirements["min_experience"]

    # Prepare features for Naive Bayes
    features = [skill_percentage, len(matched_skills), len(missing_skills), experience_years]
    prediction = nb_model.predict([features])[0]

    # Adjust acceptance criteria
    if skill_percentage >= skill_threshold and experience_years >= experience_threshold and prediction == 1:
        status = "Accepted"
    else:
        status = "Rejected"

    return {
        "skill_percentage": skill_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_years": experience_years,
        "status": status
    }

# Function to categorize and rank resumes
def categorize_and_rank_resumes(resumes):
    categorized_resumes = {job: [] for job in job_openings}

    # Categorize resumes based on job requirements
    for resume_path, resume_text in resumes:
        for job, requirements in job_openings.items():
            analysis_result = analyze_resume(resume_text, requirements)
            if analysis_result["status"] == "Accepted":
                categorized_resumes[job].append(analysis_result)
    
    # Rank resumes for each job opening
    for job, results in categorized_resumes.items():
        if job == "Senior Full Stack Developer":
            results.sort(key=lambda x: (x["experience_years"], x["skill_percentage"]), reverse=True)
        else:
            results.sort(key=lambda x: (x["skill_percentage"], x["experience_years"]), reverse=True)
    
    return categorized_resumes

# Flask Application
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Create a Tkinter root window for file dialog
        root = tk.Tk()
        root.withdraw()  # Hide the window

        # Open file dialog to select PDFs
        resume_paths = filedialog.askopenfilenames(
            title="Select Resume PDF(s)",
            filetypes=[("PDF files", "*.pdf")]
        )

        if resume_paths:
            resumes = [(path, extract_text_from_pdf(path)) for path in resume_paths]
            categorized_resumes = categorize_and_rank_resumes(resumes)

            return render_template("ml.html", categorized_resumes=categorized_resumes)

    return render_template("ml.html", categorized_resumes=None)

if __name__ == "__main__":
    app.run(debug=True)
