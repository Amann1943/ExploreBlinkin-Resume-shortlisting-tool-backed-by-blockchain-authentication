import os
from flask import Flask, request, render_template
import pdfplumber
from sklearn.naive_bayes import GaussianNB
import numpy as np

app = Flask(__name__)

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

# Ensure the 'uploads' directory exists
upload_folder = 'uploads'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

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

    skill_threshold = 70  # Minimum skill match percentage
    experience_threshold = job_requirements["min_experience"]

    features = [skill_percentage, len(matched_skills), len(missing_skills), experience_years]
    prediction = nb_model.predict([features])[0]

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

    for resume_text in resumes:
        for job, requirements in job_openings.items():
            analysis_result = analyze_resume(resume_text, requirements)
            if analysis_result["status"] == "Accepted":
                categorized_resumes[job].append(analysis_result)
    
    for job, results in categorized_resumes.items():
        results.sort(key=lambda x: (x["skill_percentage"], x["experience_years"]), reverse=True)
    
    return categorized_resumes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_files = request.files.getlist("resumes")
        if not uploaded_files:
            return "No files uploaded", 400

        resumes = []
        for file in uploaded_files:
            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)
            resume_text = extract_text_from_pdf(file_path)
            resumes.append(resume_text)
            os.remove(file_path)  # Remove file after processing

        categorized_resumes = categorize_and_rank_resumes(resumes)

        return render_template("results.html", categorized_resumes=categorized_resumes)
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
