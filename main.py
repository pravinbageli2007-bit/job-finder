"""
Simple Resume Scanner & Job Finder
===================================
"""

import streamlit as st
import re
import webbrowser
from urllib.parse import quote

# ============================================
# CONFIGURATION
# ============================================

TECHNICAL_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "golang",
    "rust", "swift", "kotlin", "php", "scala", "r", "matlab", "perl", "shell", "bash",
    "html", "css", "react", "angular", "vue", "node.js", "nodejs", "django", "flask",
    "spring", "express", "next.js", "nuxt", "svelte", "jquery", "bootstrap", "tailwind",
    "graphql", "redux", "typescript",
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite", "mariadb",
    "cassandra", "dynamodb", "elasticsearch", "firebase",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "jenkins", "circleci", "github", "gitlab", "ansible", "puppet",
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "pandas", "numpy", "matplotlib", "tableau", "power bi",
    "spark", "hadoop", "airflow", "nlp", "computer vision",
    "git", "jira", "confluence", "figma", "postman", "swagger",
    "rest api", "microservices", "agile", "scrum", "kanban",
    "linux", "windows", "unix", "networking", "security", "ci/cd", "devops"
]

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
    ]
    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        years.extend([int(y) for y in matches])
    if years:
        return max(years)
    return 0

def extract_email(text):
    email = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    return email.group(0) if email else None

def analyze_resume(text):
    skills = extract_skills(text)
    experience_years = extract_experience_years(text)
    email = extract_email(text)
    
    return {
        "skills": skills,
        "experience_years": experience_years,
        "email": email,
        "full_text": text
    }

# ============================================
# LINKEDIN FUNCTIONS
# ============================================

def open_linkedin_jobs(skills, location=""):
    if skills:
        search_query = " ".join(skills[:3])
    else:
        search_query = "software engineer"
    
    encoded_query = quote(search_query)
    encoded_location = quote(location) if location else ""
    
    url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}"
    if encoded_location:
        url += f"&location={encoded_location}"
    
    webbrowser.open(url)
    return url, search_query

# ============================================
# JOB DATABASE
# ============================================

def get_jobs(search_query=""):
    jobs = [
        {"title": "Senior Python Developer", "company": "TechCorp", "location": "Remote", 
         "salary": 120000, "description": "python django flask postgresql aws docker"},
        {"title": "Full Stack JavaScript Developer", "company": "StartupXYZ", "location": "San Francisco",
         "salary": 95000, "description": "react node.js mongodb typescript javascript html css"},
        {"title": "Data Scientist", "company": "DataDriven", "location": "New York",
         "salary": 130000, "description": "python tensorflow sql pandas numpy machine learning"},
        {"title": "DevOps Engineer", "company": "CloudFirst", "location": "Austin",
         "salary": 110000, "description": "aws docker kubernetes terraform jenkins ci/cd linux"},
        {"title": "Frontend Developer", "company": "WebAgency", "location": "Remote",
         "salary": 85000, "description": "react typescript css html javascript vue angular"},
        {"title": "Machine Learning Engineer", "company": "AI Labs", "location": "Seattle",
         "salary": 145000, "description": "pytorch tensorflow deep learning nlp computer vision python"},
        {"title": "Backend Developer", "company": "ServerSide", "location": "Chicago",
         "salary": 100000, "description": "java spring boot mysql postgresql microservices"},
        {"title": "Product Manager", "company": "ProductFirst", "location": "Boston",
         "salary": 115000, "description": "agile scrum product management roadmap"},
    ]
    
    if search_query:
        query_lower = search_query.lower()
        filtered = [j for j in jobs if query_lower in j["title"].lower() or query_lower in j["description"].lower()]
        return filtered if filtered else jobs
    return jobs

# ============================================
# MATCHING FUNCTIONS
# ============================================

def calculate_match_score(resume_skills, job_description):
    job_desc_lower = job_description.lower()
    matched = []
    missing = []
    
    for skill in resume_skills:
        if skill.lower() in job_desc_lower:
            matched.append(skill)
        else:
            missing.append(skill)
    
    if not resume_skills:
        return 0, [], []
    
    match_rate = len(matched) / len(resume_skills) * 100
    return round(match_rate, 1), matched, missing

def match_jobs(resume_skills, jobs):
    results = []
    for job in jobs:
        score, matched, missing = calculate_match_score(resume_skills, job.get("description", ""))
        results.append({**job, "match_score": score, "matched": matched, "missing": missing[:5]})
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    st.set_page_config(page_title="Job Finder", page_icon="🔍")
    
    st.title("🔍 Resume Scanner & Job Finder")
    st.markdown("Paste your resume to find matching jobs!")
    st.write("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        location = st.text_input("Location", "Remote")
        num_jobs = st.slider("Number of Jobs", 3, 10, 5)
    
    # Resume input
    st.subheader("📄 Paste Your Resume")
    resume_text = st.text_area("Copy and paste your resume text here:", height=200)
    
    if resume_text:
        with st.spinner("Analyzing..."):
            resume_data = analyze_resume(resume_text)
            
            st.success("✅ Resume analyzed!")
            
            # Stats
            col1, col2, col3 = st.columns(3)
            col1.metric("Skills Found", len(resume_data["skills"]))
            col2.metric("Experience", f"{resume_data['experience_years']} years")
            col3.metric("Email", "Found" if resume_data["email"] else "Not found")
            
            # Skills
            st.subheader("🛠️ Your Skills")
            if resume_data["skills"]:
                st.write(", ".join([f"`{s}`" for s in resume_data["skills"]]))
            else:
                st.warning("No skills detected!")
            
            # LinkedIn button
            st.write("---")
            if st.button("🔗 Open LinkedIn Jobs", type="primary"):
                url, query = open_linkedin_jobs(resume_data["skills"], location)
                st.success(f"Opened LinkedIn for: {query}")
            
            # Job matches
            st.write("---")
            st.subheader("🎯 Job Matches")
            
            jobs = get_jobs()
            matched_jobs = match_jobs(resume_data["skills"], jobs)[:num_jobs]
            
            for i, job in enumerate(matched_jobs, 1):
                score = job["match_score"]
                if score >= 70:
                    color = "green"
                elif score >= 40:
                    color = "orange"
                else:
                    color = "red"
                
                st.markdown(f"**{i}. {job['title']}**")
                st.caption(f"🏢 {job['company']} | 📍 {job['location']} | 💰 ${job['salary']:,}")
                st.markdown(f":{color}[**{score}% Match**]")
                
                if job["matched"]:
                    st.caption(f"✅ Matched: {', '.join(job['matched'])}")
                if job["missing"]:
                    st.caption(f"💡 Missing: {', '.join(job['missing'])}")
                
                st.write("---")
    
    else:
        st.info("👆 Paste your resume above to get started!")

if __name__ == "__main__":
    main()
