import os
import pdfplumber
from sklearn.naive_bayes import GaussianNB
import numpy as np
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
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
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

# Command-line interface for uploading resumes
def main():
    print("Resume Analyzer CLI")
    print("====================")

    # Create a Tkinter root window (it's required for using filedialog)
    root = tk.Tk()
    root.withdraw()  # Hide the root window as we only want the file dialog

    # Ask user to select PDF file(s) via file dialog
    resume_paths = filedialog.askopenfilenames(
        title="Select Resume PDF(s)",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not resume_paths:
        print("No PDF files selected.")
        return

    # Extract text from each resume
    resumes = []
    for path in resume_paths:
        resume_text = extract_text_from_pdf(path)
        print(f"Extracted text from {os.path.basename(path)}:")
        print(resume_text[:500])  # Print the first 500 characters of the extracted text for debugging
        resumes.append((path, resume_text))

    # Categorize and rank resumes
    categorized_resumes = categorize_and_rank_resumes(resumes)

    # Display the results
    for job, results in categorized_resumes.items():
        print(f"\nJob Opening: {job}")
        if results:
            for idx, result in enumerate(results):
                print(f"  Rank {idx + 1}:")
                print(f"    Skill Match Percentage: {result['skill_percentage']:.2f}%")
                print(f"    Matched Skills: {', '.join(result['matched_skills'])}")
                print(f"    Missing Skills: {', '.join(result['missing_skills'])}")
                print(f"    Experience: {result['experience_years']} years")
                print("=" * 50)
        else:
            print("  No suitable candidates found.")
            print("=" * 50)

if __name__ == "__main__":
    main()
