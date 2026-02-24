"""
Resume Scanner & LinkedIn Job Finder
=====================================
Complete working application
"""

import streamlit as st
import requests
import re
import webbrowser
from urllib.parse import quote

# ============================================
# PDF PARSING - Multiple Methods
# ============================================

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF using pypdf"""
    try:
        from pypdf import PdfReader
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# ============================================
# CONFIGURATION
# ============================================

TECHNICAL_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "golang",
    "rust", "swift", "kotlin", "php", "scala", "r", "matlab", "perl", "shell", "bash",
    "html", "css", "react", "angular", "vue", "node.js", "nodejs", "django", "flask",
    "spring", "express", "next.js", "nuxt", "svelte", "jquery", "bootstrap", "tailwind",
    "webpack", "graphql", "apollo", "redux",
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite", "mariadb",
    "cassandra", "dynamodb", "elasticsearch", "firebase",
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "jenkins", "circleci", "github actions", "gitlab ci", "ansible", "puppet",
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "matplotlib", "tableau", "power bi",
    "spark", "hadoop", "airflow", "nlp", "computer vision", "opencv",
    "git", "jira", "confluence", "figma", "postman", "swagger",
    "rest api", "microservices", "agile", "scrum", "kanban",
    "linux", "windows", "unix", "networking", "security", "ci/cd"
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
    patterns = [
        r'(?:senior|junior|lead|principal|staff|chief|head|director|manager|engineer|developer|analyst|scientist|architect|consultant)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip().title()
    return "Not detected"

def extract_contact_info(text):
    email = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    phone = re.search(r'(?:\+?1[-.\s]?)?\$?\d{3}\$?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    linkedin = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
    github = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
    
    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None
    }

def analyze_resume(text):
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
    demo_jobs = [
        {"title": "Senior Python Developer", "company": "TechCorp", "location": "Remote", 
         "salary": 120000, "description": "Python Django Flask PostgreSQL AWS Docker Kubernetes",
         "url": "https://linkedin.com"},
        {"title": "Full Stack JavaScript Developer", "company": "StartupXYZ", "location": "San Francisco, CA",
         "salary": 95000, "description": "React Node.js MongoDB TypeScript JavaScript",
         "url": "https://linkedin.com"},
        {"title": "Data Scientist", "company": "DataDriven Co", "location": "New York, NY",
         "salary": 130000, "description": "Python TensorFlow SQL machine learning pandas",
         "url": "https://linkedin.com"},
        {"title": "DevOps Engineer", "company": "CloudFirst", "location": "Austin, TX",
         "salary": 110000, "description": "AWS Docker Kubernetes Terraform Jenkins",
         "url": "https://linkedin.com"},
        {"title": "Frontend Developer", "company": "WebAgency", "location": "Remote",
         "salary": 85000, "description": "React TypeScript CSS HTML JavaScript",
         "url": "https://linkedin.com"},
        {"title": "Machine Learning Engineer", "company": "AI Labs", "location": "Seattle, WA",
         "salary": 145000, "description": "PyTorch TensorFlow deep learning NLP",
         "url": "https://linkedin.com"},
        {"title": "Backend Developer", "company": "ServerSide", "location": "Chicago, IL",
         "salary": 100000, "description": "Java Spring Boot MySQL microservices",
         "url": "https://linkedin.com"},
        {"title": "Product Manager", "company": "ProductFirst", "location": "Boston, MA",
         "salary": 115000, "description": "Agile Scrum product management roadmap",
         "url": "https://linkedin.com"},
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
            
            if text and text.strip():
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
                    st.warning("No technical skills detected! Make sure your resume lists your skills clearly.")
                
                # LinkedIn Button
                st.divider()
                st.subheader("🔗 LinkedIn Job Search")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🚀 Open LinkedIn Jobs", type="primary", use_container_width=True):
                        url, query = open_linkedin_jobs(resume_data, location)
                        st.success(f"Opened LinkedIn search for: {query}")
                
                with col_btn2:
                    st.info(f"📍 Location: {location}")
                    st.info(f"🔎 Search: {resume_data['skills'][:3] if resume_data['skills'] else job_search}")
                
                st.divider()
                
                # Job Matches
                st.subheader(f"🎯 Top {num_jobs} Job Matches")
                
                jobs = get_demo_jobs(job_search)
                matched_jobs = match_jobs_with_resume(resume_data, jobs)[:num_jobs]
                
                for i, job in enumerate(matched_jobs, 1):
                    # Color based on match score
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
                        
                        with col_job2:
                            st.markdown(f"**{job['title']}**")
                            st.caption(f"🏢 {job['company']} | 📍 {job['location']}")
                            if job["salary"]:
                                st.caption(f"💰 ${job['salary']:,}")
                            if job["matched_skills"]:
                                st.caption(f"✅ Matched: {', '.join(job['matched_skills'])}")
                        
                        with col_job3:
                            st.markdown(f":{score_color}[**{job['match_score']}%**]")
                            st.link_button("Apply", job["url"], type="secondary")
                        
                        st.divider()
                
                # Skills breakdown
                if matched_jobs:
                    st.subheader("📊 Skills Breakdown")
                    with st.expander("See detailed skills analysis"):
                        for job in matched_jobs[:3]:
                            st.write(f"**{job['title']}**")
                            if job["matched_skills"]:
                                st.success(f"✅ You have: {', '.join(job['matched_skills'])}")
                            if job["missing_skills"]:
                                st.warning(f"💡 Learn: {', '.join(job['missing_skills'])}")
                            st.markdown("---")
            
            else:
                st.error("❌ Could not read PDF. Please try a different file.")
    
    else:
        # Welcome screen
        st.info("👆 Please upload a PDF resume to get started!")
        
        st.subheader("📋 How to use:")
        col_h1, col_h2, col_h3 = st.columns(3)
        
        with col_h1:
            st.markdown("### 1. Upload")
            st.markdown("Upload your PDF resume")
        
        with col_h2:
            st.markdown("### 2. Analyze")
            st.markdown("We extract skills & experience")
        
        with col_h3:
            st.markdown("### 3. Find Jobs")
            st.markdown("Get matched & apply!")

if __name__ == "__main__":
    main()
