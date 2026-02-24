"""
Resume Scanner & LinkedIn Job Finder
=====================================
Version that works WITHOUT pypdf - uses only built-in libraries
"""

import streamlit as st
import requests
import re
import webbrowser
from urllib.parse import quote
import io

# ============================================
# PDF PARSING - Built-in method (no pypdf needed)
# ============================================

def extract_text_from_pdf(pdf_file):
    """
    Extract text from PDF using pdfminer.six (built-in fallback)
    """
    # Try pdfminer.six first
    try:
        from pdfminer.high_level import extract_text
        pdf_file.seek(0)
        text = extract_text(pdf_file)
        if text and text.strip():
            return text
    except Exception as e:
        pass
    
    # Try reading raw PDF content as text (works for text-based PDFs)
    try:
        pdf_file.seek(0)
        content = pdf_file.read()
        
        # Try to decode as latin-1 (PDF encoding)
        try:
            text = content.decode('latin-1')
        except:
            text = content.decode('utf-8', errors='ignore')
        
        # Extract text between stream tags
        text = re.sub(r'<<[^>]*>>', '', text)
        text = re.sub(r'BT[^/]*ET', '', text, flags=re.DOTALL)
        text = re.sub(r'\$[^)]*\$', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up common PDF artifacts
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        if text and len(text) > 50:
            return text
    except Exception as e:
        pass
    
    # If PDF parsing fails, ask user for text input
    return None

# ============================================
# CONFIGURATION
# ============================================

TECHNICAL_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "golang",
    "rust", "swift", "kotlin", "php", "scala", "r", "matlab", "perl", "shell", "bash",
    "html", "css", "react", "angular", "vue", "node.js", "nodejs", "django", "flask",
    "spring", "express", "next.js", "nuxt", "svelte", "jquery", "bootstrap", "tailwind",
    "webpack", "graphql", "apollo", "redux", "typescript",
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite", "mariadb",
    "cassandra", "dynamodb", "elasticsearch", "firebase", "supabase",
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "jenkins", "circleci", "github actions", "gitlab ci", "ansible", "puppet", "helm",
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "matplotlib", "tableau", "power bi",
    "spark", "hadoop", "airflow", "nlp", "computer vision", "opencv", "xgboost",
    "git", "jira", "confluence", "figma", "postman", "swagger", "insomnia",
    "rest api", "microservices", "agile", "scrum", "kanban", "jira",
    "linux", "windows", "unix", "macos", "networking", "security", "ci/cd", "devops",
    "express.js", "fastapi", "nestjs", "prisma", "typeorm", "mongoose",
    "azure devops", "aws lambda", "google cloud functions", "serverless"
]

# ============================================
# RESUME PARSING FUNCTIONS
# ============================================

def extract_skills(text):
    """Extract technical skills from resume text"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in TECHNICAL_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return list(set(found_skills))

def extract_experience_years(text):
    """Extract years of experience from resume"""
    if not text:
        return 0
    
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)?',
        r'(?:over|more than)\s*(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\s*(?:to\s*)?\d+\s*(?:years?|yrs?)',
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
    """Extract job title from resume"""
    if not text:
        return "Not detected"
    
    patterns = [
        r'(?:position|role|title):\s*([^\n]+)',
        r'(?:current|currently)\s*(?:working\s*as|role|position):\s*([^\n]+)',
    ]
    
    title_patterns = [
        "software engineer", "senior software engineer", "junior software engineer",
        "full stack developer", "frontend developer", "backend developer",
        "data scientist", "data engineer", "machine learning engineer",
        "devops engineer", "site reliability engineer", "cloud engineer",
        "product manager", "project manager", "technical lead", "architect",
        "ux designer", "ui designer", "qa engineer", "test engineer",
        "mobile developer", "ios developer", "android developer",
        "security engineer", "network engineer", "database administrator",
        "system administrator", "backend engineer", "frontend engineer"
    ]
    
    text_lower = text.lower()
    for title in title_patterns:
        if title in text_lower:
            return title.title()
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            if len(title) > 3 and len(title) < 60:
                return title.title()
    
    return "Not detected"

def extract_contact_info(text):
    """Extract contact information from resume"""
    if not text:
        return {}
    
    email = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    phone = re.search(r'(?:\+?1[-.\s]?)?\$?\d{3}\$?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    linkedin = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
    github = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
    portfolio = re.search(r'(?:https?://)?[\w-]+\.(?:com|io|me|dev)[\w-]*', text)
    
    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
        "portfolio": portfolio.group(0) if portfolio else None
    }

def analyze_resume(text):
    """Complete resume analysis"""
    skills = extract_skills(text)
    experience_years = extract_experience_years(text)
    job_title = extract_job_title(text)
    contact = extract_contact_info(text)
    
    return {
        "skills": skills,
        "experience_years": experience_years,
        "job_title": job_title,
        "email": contact["email"],
        "phone": contact["phone"],
        "linkedin": contact["linkedin"],
        "github": contact["github"],
        "portfolio": contact["portfolio"],
        "full_text": text
    }

# ============================================
# LINKEDIN FUNCTIONS
# ============================================

def open_linkedin_jobs(resume_data, location=""):
    """Open LinkedIn job search based on resume skills"""
    skills = resume_data.get("skills", [])
    job_title = resume_data.get("job_title", "")
    
    if skills:
        search_query = " ".join(skills[:3])
    elif job_title and job_title != "Not detected":
        search_query = job_title
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

def get_demo_jobs(search_query=""):
    """Get demo jobs for testing"""
    demo_jobs = [
        {"title": "Senior Python Developer", "company": "TechCorp Inc.", "location": "Remote", 
         "salary": 120000, "description": "Python Django Flask PostgreSQL AWS Docker Kubernetes machine learning",
         "url": "https://www.linkedin.com/jobs"},
        {"title": "Full Stack JavaScript Developer", "company": "StartupXYZ", "location": "San Francisco, CA",
         "salary": 95000, "description": "React Node.js MongoDB TypeScript JavaScript HTML CSS Docker",
         "url": "https://www.linkedin.com/jobs"},
        {"title": "Data Scientist", "company": "DataDriven Co.", "location": "New York, NY",
         "salary": 130000, "description": "Python TensorFlow SQL pandas numpy machine learning deep learning",
         "url": "https://www.linkedin.com/jobs"},
        {"title": "DevOps Engineer", "company": "CloudFirst Ltd.", "location": "Austin, TX",
         "salary": 110000, "description": "AWS Docker Kubernetes Terraform Jenkins CI/CD Linux Azure",
         "url": "https://www.linkedin.com/jobs"},
        {"title": "Frontend Developer", "company": "WebAgency", "location": "Remote",
         "salary": 85000, "description": "React TypeScript CSS HTML JavaScript Vue Angular Bootstrap",
         "url": "https://www.linkedin.com/jobs"},
        {"title": "Machine Learning Engineer", "company": "AI Labs", "location": "Seattle, WA",
         "salary": 145000, "description": "PyTorch TensorFlow deep learning NLP computer vision Python",
         "url": "https://www.linkedin.com/jobs"},
        {"title": "Backend Developer", "company": "ServerSide Inc.", "location": "Chicago, IL",
         "salary": 100000, "description": "Java Spring Boot MySQL PostgreSQL microservices REST API",
         "url": "https://www.linkedin.com/jobs"},
        {"title": "Product Manager", "company": "ProductFirst", "location": "Boston, MA",
         "salary": 115000, "description": "Agile Scrum product management roadmap Jira Confluence",
         "url": "https://www.linkedin.com/jobs"},
        {"title": "Software Engineer", "company": "TechStart", "location": "Remote",
         "salary": 105000, "description": "Python JavaScript React Docker AWS Git CI/CD",
         "url": "https://www.linkedin.com/jobs"},
        {"title": "Cloud Engineer", "company": "CloudSolutions", "location": "Denver, CO",
         "salary": 125000, "description": "AWS Azure GCP Kubernetes Terraform Docker Linux networking",
         "url": "https://www.linkedin.com/jobs"},
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
    """Calculate how well resume matches a job"""
    if not job_description:
        return 0, [], []
    
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
    """Match resume against job listings"""
    resume_skills = resume_data.get("skills", [])
    results = []
    
    for job in jobs:
        match_score, matched, missing = calculate_match_score(resume_skills, job.get("description", ""))
        
        # Boost score if job title contains relevant keywords
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
    st.set_page_config(page_title="Resume Scanner & Job Finder", page_icon="🔍", layout="wide")
    
    st.title("🔍 Resume Scanner & LinkedIn Job Finder")
    st.markdown("Upload your resume to find matching jobs and open LinkedIn search!")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        job_search = st.text_input("Job Title to Search", "software engineer")
        location = st.text_input("Location", "Remote")
        num_jobs = st.slider("Number of Jobs", 5, 20, 10)
        
        st.markdown("---")
        st.markdown("**📝 How it works:**")
        st.markdown("1. Upload your PDF resume")
        st.markdown("2. We extract your skills")
        st.markdown("3. Find matching jobs")
        st.markdown("4. Open LinkedIn search")
    
    # File upload
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Analyzing your resume..."):
            # Extract text from PDF
            text = extract_text_from_pdf(uploaded_file)
            
            if text and text.strip() and len(text) > 50:
                # Analyze resume
                resume_data = analyze_resume(text)
                
                st.success("✅ Resume uploaded successfully!")
                
                # Stats row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Skills Found", len(resume_data["skills"]))
                with col2:
                    st.metric("Experience", f"{resume_data['experience_years']} years")
                with col3:
                    st.metric("Job Title", resume_data["job_title"])
                with col4:
                    st.metric("Email", "Found ✅" if resume_data["email"] else "Not found")
                
                # Show detected skills
                st.subheader("🛠️ Detected Skills from Resume")
                if resume_data["skills"]:
                    skills_html = " ".join([f"`{s}`" for s in resume_data["skills"]])
                    st.markdown(skills_html)
                else:
                    st.warning("No technical skills detected!")
                    st.info("💡 Tip: Make sure your resume clearly lists your technical skills like: Python, Java, React, AWS, etc.")
                
                # LinkedIn Button
                st.divider()
                st.subheader("🔗 LinkedIn Job Search")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🚀 Open LinkedIn Jobs", type="primary", use_container_width=True):
                        url, query = open_linkedin_jobs(resume_data, location)
                        st.success(f"✅ Opened LinkedIn search for: **{query}**")
                
                with col_btn2:
                    st.info(f"📍 Location: {location}")
                    search_terms = ", ".join(resume_data['skills'][:5]) if resume_data['skills'] else job_search
                    st.info(f"🔎 Searching for: {search_terms}")
                
                st.divider()
                
                # Job Matches
                st.subheader(f"🎯 Top {num_jobs} Job Matches")
                
                jobs = get_demo_jobs(job_search)
                matched_jobs = match_jobs_with_resume(resume_data, jobs)[:num_jobs]
                
                for i, job in enumerate(matched_jobs, 1):
                    if job["match_score"] >= 70:
                        score_color = "green"
                        emoji = "🟢"
                    elif job["match_score"] >= 40:
                        score_color = "orange"
                        emoji = "🟡"
                    else:
                        score_color = "red"
                        emoji = "🔴"
                    
                    with st.container():
                        col_job1, col_job2, col_job3 = st.columns([1, 4, 1])
                        
                        with col_job1:
                            st.markdown(f"### {i}")
