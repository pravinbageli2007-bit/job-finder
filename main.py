"""
Resume Scanner & Job Finder
============================
Complete working application with fixed PDF parsing
"""

import streamlit as st
import requests
import spacy
import re
import os

# ============================================
# FIXED PDF PARSING - Multiple methods
# ============================================

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF using multiple fallback methods"""
    text = ""
    
    # Method 1: Try pypdf (most reliable)
    try:
        from pypdf import PdfReader
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        if text.strip():
            return text
    except Exception as e:
        pass
    
    # Method 2: Try pdfminer.six
    try:
        from pdfminer.high_level import extract_text
        pdf_file.seek(0)  # Reset file pointer
        text = extract_text(pdf_file)
        if text.strip():
            return text
    except Exception as e:
        pass
    
    # Method 3: Try pdfplumber
    try:
        import pdfplumber
        pdf_file.seek(0)
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        if text.strip():
            return text
    except Exception as e:
        pass
    
    return text

# ============================================
# CONFIGURATION
# ============================================

ADZUNA_APP_ID = "your_app_id_here"
ADZUNA_API_KEY = "your_api_key_here"
ADZUNA_COUNTRY = "us"

TECHNICAL_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "golang",
    "rust", "swift", "kotlin", "php", "scala", "r", "matlab", "perl", "shell",
    "html", "css", "react", "angular", "vue", "node.js", "nodejs", "django", "flask",
    "spring", "express", "next.js", "nuxt", "svelte", "jquery", "bootstrap", "tailwind",
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite", "mariadb",
    "cassandra", "dynamodb", "elasticsearch", "firebase",
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "jenkins", "circleci", "github actions", "gitlab ci", "ansible", "puppet",
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "matplotlib", "tableau", "power bi",
    "spark", "hadoop", "airflow", "nlp", "computer vision",
    "git", "jira", "confluence", "figma", "sketch", "postman", "swagger",
    "graphql", "rest api", "microservices", "agile", "scrum", "kanban",
    "linux", "windows", "unix", "networking", "security", "ci/cd", "devops",
    "data analysis", "data scientist", "data engineer", "analytics", "big data",
    "ios", "android", "mobile", "react native", "flutter", "graphql"
]

# ============================================
# LOAD NLP MODEL
# ============================================

@st.cache_resource
def load_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        import subprocess
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")

nlp = load_nlp_model()

# ============================================
# RESUME PARSING FUNCTIONS
# ============================================

def extract_skills(text):
    text_lower = text.lower()
    found_skills = []
    for skill in TECHNICAL_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return list(set(found_skills))

def extract_experience_years(text):
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)?',
        r'experience\s*(?:of\s*)?(\d+)\+?\s*(?:years?|yrs?)',
    ]
    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        years.extend([int(y) for y in matches])
    if years:
        return max(years)
    return 0

def extract_job_title(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "TITLE"]:
            return ent.text
    return "Not detected"

def analyze_resume(text):
    skills = extract_skills(text)
    experience_years = extract_experience_years(text)
    job_title = extract_job_title(text)
    email = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    phone = re.search(r'(?:\+?1[-.\s]?)?\$?\d{3}\$?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    
    return {
        "skills": skills,
        "experience_years": experience_years,
        "job_title": job_title,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "full_text": text
    }

# ============================================
# JOB FETCHING FUNCTIONS
# ============================================

def fetch_jobs_from_adzuna(search_query, location="", num_jobs=10):
    if ADZUNA_APP_ID == "your_app_id_here":
        return get_demo_jobs(search_query)
    
    base_url = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "what": search_query,
        "where": location if location else "",
        "results_per_page": num_jobs,
    }
    
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for job in data.get("results", []):
                jobs.append({
                    "title": job.get("title", ""),
                    "company": job.get("company", {}).get("display_name", "Unknown"),
                    "location": job.get("location", {}).get("display_name", "Unknown"),
                    "salary": job.get("salary_min", 0) or job.get("salary_max", 0),
                    "description": job.get("description", ""),
                    "url": job.get("redirect_url", ""),
                    "date_posted": job.get("date", "")
                })
            return jobs
        else:
            return get_demo_jobs(search_query)
    except:
        return get_demo_jobs(search_query)

def get_demo_jobs(search_query):
    demo_jobs = [
        {"title": "Senior Python Developer", "company": "TechCorp Inc.", "location": "Remote", 
         "salary": 120000, "description": "Python Django Flask PostgreSQL 5+ years experience required.",
         "url": "#", "date_posted": "2024-01-15"},
        {"title": "Full Stack JavaScript Developer", "company": "StartupXYZ", "location": "San Francisco, CA",
         "salary": 95000, "description": "React Node.js MongoDB JavaScript TypeScript experience needed.",
         "url": "#", "date_posted": "2024-01-14"},
        {"title": "Data Scientist", "company": "DataDriven Co.", "location": "New York, NY",
         "salary": 130000, "description": "Python TensorFlow SQL machine learning data science background.",
         "url": "#", "date_posted": "2024-01-13"},
        {"title": "DevOps Engineer", "company": "CloudFirst Ltd.", "location": "Austin, TX",
         "salary": 110000, "description": "AWS Docker Kubernetes Terraform Jenkins DevOps experience.",
         "url": "#", "date_posted": "2024-01-12"},
        {"title": "Frontend Developer", "company": "WebAgency", "location": "Remote",
         "salary": 85000, "description": "React TypeScript CSS HTML JavaScript frontend experience.",
         "url": "#", "date_posted": "2024-01-11"},
        {"title": "Machine Learning Engineer", "company": "AI Innovations", "location": "Seattle, WA",
         "salary": 145000, "description": "PyTorch TensorFlow deep learning ML engineer PhD preferred.",
         "url": "#", "date_posted": "2024-01-10"},
        {"title": "Backend Developer", "company": "ServerSide Inc.", "location": "Chicago, IL",
         "salary": 100000, "description": "Java Spring Boot MySQL backend development experience.",
         "url": "#", "date_posted": "2024-01-09"},
        {"title": "Product Manager", "company": "ProductFirst", "location": "Boston, MA",
         "salary": 115000, "description": "Agile Scrum product management technical background preferred.",
         "url": "#", "date_posted": "2024-01-08"},
    ]
    
    if search_query:
        query_lower = search_query.lower()
        filtered = [j for j in demo_jobs if query_lower in j["title"].lower() or query_lower in j["description"].lower()]
        return filtered if filtered else demo_jobs
    return demo_jobs

# ============================================
# MATCHING FUNCTIONS
# ============================================

def calculate_match_score(resume_skills, job_description):
    job_desc_lower = job_description.lower()
    matched_skills = []
    missing_skills = []
    
    for skill in resume_skills:
        if skill.lower() in job_desc_lower:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
    
    if not resume_skills:
        return 0, [], []
    
    match_rate = len(matched_skills) / len(resume_skills) * 100
    return round(match_rate, 1), matched_skills, missing_skills

def match_jobs_with_resume(resume_data, jobs):
    resume_skills = resume_data.get("skills", [])
    results = []
    
    for job in jobs:
        match_score, matched, missing = calculate_match_score(resume_skills, job.get("description", ""))
        
        title_lower = job.get("title", "").lower()
        for skill in resume_skills:
            if skill.lower() in title_lower:
                match_score += 5
        
        match_score = min(100, match_score)
        
        results.append({
            **job,
            "match_score": match_score,
            "matched_skills": matched,
            "missing_skills": missing[:5]
        })
    
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    st.set_page_config(page_title="AI Resume Scanner & Job Finder", page_icon="🔍", layout="wide")
    
    st.title("🔍 AI Resume Scanner & Job Finder")
    st.markdown("Upload your resume and find matching job opportunities!")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        job_search = st.text_input("Job Title to Search", "software engineer")
        location = st.text_input("Location", "remote")
        num_jobs = st.slider("Number of Jobs", 5, 20, 10)
    
    # File upload
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Analyzing your resume..."):
            text = extract_text_from_pdf(uploaded_file)
            
            if text and text.strip():
                resume_data = analyze_resume(text)
                
                st.success("✅ Resume uploaded successfully!")
                
                # Stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Skills Found", len(resume_data["skills"]))
                with col2:
                    st.metric("Experience", f"{resume_data['experience_years']} years")
                with col3:
                    st.metric("Detected Title", resume_data["job_title"])
                with col4:
                    st.metric("Email", "Found ✅" if resume_data["email"] else "Not found")
                
                # Skills
                st.subheader("🛠️ Detected Skills")
                if resume_data["skills"]:
                    skills_html = " ".join([f"`{s}`" for s in resume_data["skills"]])
                    st.markdown(skills_html)
                else:
                    st.warning("No skills detected!")
                
                st.divider()
                
                # Jobs
                with st.spinner("Finding jobs..."):
                    jobs = fetch_jobs_from_adzuna(job_search, location, num_jobs)
                    matched_jobs = match_jobs_with_resume(resume_data, jobs)
                
                st.subheader(f"🎯 Top {len(matched_jobs)} Job Matches")
                
                for i, job in enumerate(matched_jobs, 1):
                    if job["match_score"] >= 70:
                        score_color = "green"
                    elif job["match_score"] >= 40:
                        score_color = "orange"
                    else:
                        score_color = "red"
                    
                    with st.container():
                        cols = st.columns([1, 5, 1])
                        with cols[0]:
                            st.markdown(f"### {i}")
                        with cols[1]:
                            st.markdown(f"**{job['title']}**")
                            st.caption(f"🏢 {job['company']} | 📍 {job['location']}")
                            if job["salary"]:
                                st.caption(f"💰 ${job['salary']:,}")
                        with cols[2]:
                            st.markdown(f":{score_color}[**{job['match_score']}%**]")
                            if job["url"] != "#":
                                st.link_button("Apply", job["url"])
                        st.divider()
            else:
                st.error("Could not read PDF. Please try another file.")
    
    else:
        st.info("👆 Upload a PDF resume to get started!")

if __name__ == "__main__":
    main()
