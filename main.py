"""
Resume Scanner & Job Finder
============================
Complete working application that parses resumes and finds matching jobs.
"""

import streamlit as st
import pdfminer.high_level
import requests
import spacy
import re

# ============================================
# CONFIGURATION
# ============================================

# Get free API keys from https://developer.adzuna.com/
# Or leave as-is to use demo mode
ADZUNA_APP_ID = "your_app_id_here"
ADZUNA_API_KEY = "your_api_key_here"
ADZUNA_COUNTRY = "us"

# Comprehensive skills list
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
    "linux", "windows", "unix", "networking", "security", "ci/cd", "devops"
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

def extract_text_from_pdf(pdf_file):
    try:
        text = pdfminer.high_level.extract_text(pdf_file)
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        return ""

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
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        job_search = st.text_input("Job Title to Search", "software engineer")
        location = st.text_input("Location", "remote")
        num_jobs = st.slider("Number of Jobs to Fetch", 5, 20, 10)
        
        st.markdown("---")
        st.markdown("**📝 Note:** Without an Adzuna API key, demo jobs will be shown.")
        st.markdown("[Get free API key](https://developer.adzuna.com/)")
    
    # File upload
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Analyzing your resume..."):
            # Extract text from PDF
            text = extract_text_from_pdf(uploaded_file)
            
            if text:
                # Analyze resume
                resume_data = analyze_resume(text)
                
                # Display analysis
                st.success("✅ Resume uploaded successfully!")
                
                # Resume stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Skills Found", len(resume_data["skills"]))
                with col2:
                    st.metric("Experience", f"{resume_data['experience_years']} years")
                with col3:
                    st.metric("Detected Title", resume_data["job_title"])
                with col4:
                    if resume_data["email"]:
                        st.metric("Email", "Found ✅")
                    else:
                        st.metric("Email", "Not found")
                
                # Show detected skills
                st.subheader("🛠️ Detected Skills from Resume")
                if resume_data["skills"]:
                    skills_html = " ".join([f"`{s}`" for s in resume_data["skills"]])
                    st.markdown(skills_html)
                else:
                    st.warning("No technical skills detected. Make sure your resume clearly lists your skills!")
                
                st.divider()
                
                # Fetch jobs
                with st.spinner("Finding matching jobs..."):
                    jobs = fetch_jobs_from_adzuna(job_search, location, num_jobs)
                    matched_jobs = match_jobs_with_resume(resume_data, jobs)
                
                # Display results
                st.subheader(f"🎯 Top {len(matched_jobs)} Job Matches")
                
                for i, job in enumerate(matched_jobs, 1):
                    # Color based on match score
                    if job["match_score"] >= 70:
                        color = "🟢"
                        score_color = "green"
                    elif job["match_score"] >= 40:
                        color = "🟡"
                        score_color = "orange"
                    else:
                        color = "🔴"
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
                            st.caption(f"📝 {job['description'][:150]}...")
                        with cols[2]:
                            st.markdown(f":{score_color}[**{job['match_score']}%**]")
                            if job["url"] != "#":
                                st.link_button("Apply", job["url"])
                        st.divider()
                
                # Show matched/missing skills for top 3
                st.subheader("📊 Skills Breakdown (Top 3)")
                for job in matched_jobs[:3]:
                    with st.expander(f"{job['title']} - {job['match_score']}% Match"):
                        if job["matched_skills"]:
                            st.write("✅ **Matched Skills:** " + ", ".join(job["matched_skills"]))
                        if job["missing_skills"]:
                            st.write("💡 **Skills to Add:** " + ", ".join(job["missing_skills"]))
            else:
                st.error("Could not extract text from PDF. Please try a different file.")
    
    else:
        # Show sample when no file uploaded
        st.info("👆 Please upload a PDF resume to get started!")
        
        st.subheader("📋 How it works:")
        st.write("1. Upload your resume (PDF format)")
        st.write("2. We'll extract your skills and experience")
        st.write("3. We'll match you with relevant job opportunities")
        st.write("4. You'll see your match percentage for each job")

if __name__ == "__main__":
    main()
