"""
Resume Scanner & LinkedIn Job Finder
=====================================
Complete working application with:
- Fixed PDF parsing (multiple methods)
- LinkedIn job search integration
- Skill extraction and job matching
"""

import streamlit as st
import requests
import re
import webbrowser
from urllib.parse import quote

# ============================================
# FIXED PDF PARSING - Multiple Methods
# ============================================

def extract_text_from_pdf(pdf_file):
    """
    Extract text from PDF using multiple fallback methods
    """
    text = ""
    
    # Method 1: Try pypdf (most reliable)
    try:
        from pypdf import PdfReader
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        if text.strip():
            return text
    except Exception as e:
        pass
    
    # Method 2: Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        if text.strip():
            return text
    except Exception as e:
        pass
    
    # Method 3: Try pdfminer.six
    try:
        from pdfminer.high_level import extract_text
        pdf_file.seek(0)
        text = extract_text(pdf_file)
        if text and text.strip():
            return text
    except Exception as e:
        pass
    
    return text

# ============================================
# CONFIGURATION
# ============================================

# LinkedIn Job Search URL Template
LINKEDIN_BASE_URL = "https://www.linkedin.com/jobs/search/"

# Comprehensive skills database
TECHNICAL_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "golang",
    "rust", "swift", "kotlin", "php", "scala", "r", "matlab", "perl", "shell", "bash",
    
    # Web Technologies
    "html", "css", "react", "angular", "vue", "node.js", "nodejs", "django", "flask",
    "spring", "express", "next.js", "nuxt", "svelte", "jquery", "bootstrap", "tailwind",
    "webpack", "vite", "graphql", "apollo", "redux", "zustand",
    
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite", "mariadb",
    "cassandra", "dynamodb", "elasticsearch", "firebase", "supabase", "neon",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "jenkins", "circleci", "github actions", "gitlab ci", "ansible", "puppet",
    "helm", "argo cd", "istio", "linkerd", "prometheus", "grafana", "elk",
    
    # Data Science & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi",
    "spark", "hadoop", "airflow", "nlp", "computer vision", "opencv", "xgboost",
    "lightgbm", "catboost", "huggingface", "langchain", "openai", "llm",
    
    # Other Tools & Methodologies
    "git", "jira", "confluence", "figma", "sketch", "postman", "swagger",
    "rest api", "microservices", "agile", "scrum", "kanban", "jira",
    "linux", "windows", "unix", "macos", "networking", "security", "ci/cd",
    "tdd", "bdd", "testing", "jest", "pytest", "selenium", "cypress",
    "aws lambda", "azure functions", "google cloud functions", "serverless",
    "blockchain", "ethereum", "solidity", "web3"
]

# Job title patterns
JOB_TITLE_PATTERNS = [
    "software engineer", "senior software engineer", "junior software engineer",
    "full stack developer", "frontend developer", "backend developer",
    "data scientist", "data engineer", "machine learning engineer",
    "devops engineer", "site reliability engineer", "cloud engineer",
    "product manager", "project manager", "technical lead", "architect",
    "ux designer", "ui designer", "qa engineer", "test engineer",
    "mobile developer", "ios developer", "android developer",
    "security engineer", "network engineer", "database administrator",
    "system administrator", "backend engineer", "frontend engineer",
    "fullstack developer", "principal engineer", "staff engineer"
]

# ============================================
# RESUME PARSING FUNCTIONS
# ============================================

def extract_skills(text):
    """
    Extract technical skills from resume text
    """
    text_lower = text.lower()
    found_skills = []
    
    for skill in TECHNICAL_SKILLS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return list(set(found_skills))

def extract_experience_years(text):
    """
    Extract years of experience from resume
    """
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
    
    # Try to estimate from work history
    current_year = 2024
    work_periods = re.findall(r'(?:20\d{2}|19\d{2})\s*[-–—to]+\s*(?:present|current|now|20\d{2})', text, re.IGNORECASE)
    if work_periods:
        years_found = []
        for period in work_periods:
            year_match = re.search(r'(20\d{2}|19\d{2})', period)
            if year_match:
                years_found.append(int(year_match.group(1)))
        if years_found:
            return current_year - min(years_found)
    
    return 0

def extract_job_title(text):
    """
    Extract current/most recent job title from resume
    """
    text_lower = text.lower()
    
    # Look for common job title patterns
    for title in JOB_TITLE_PATTERNS:
        if title in text_lower:
            return title.title()
    
    # Try to find title after common phrases
    title_phrases = [
        r'(?:current|currently)\s*(?:working\s*as|position|role):\s*([^\n]+)',
        r'(?:position|role|title):\s*([^\n]+)',
        r'([a-z\s]+ engineer|developer|manager|analyst|scientist|designer|administrator)',
    ]
    
    for phrase in title_phrases:
        match = re.search(phrase, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            if len(title) > 3 and len(title) < 60:
                return title.title()
    
    return "Not detected"

def extract_contact_info(text):
    """
    Extract email and phone from resume
    """
    # Email pattern
    email_pattern = r'[\w.-]+@[\w.-]+\.\w+'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else None
    
    # Phone pattern (various formats)
    phone_patterns = [
        r'(?:\+?1[-.\s]?)?\$?\d{3}\$?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'(?:\+?1[-.\s]?)?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
    ]
    
    phone = None
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone = phone_match.group(0)
            break
    
    # LinkedIn profile
    linkedin_pattern = r'(?:linkedin\.com/in/)([a-zA-Z0-9_-]+)'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    linkedin = linkedin_match.group(0) if linkedin_match else None
    
    # GitHub profile
    github_pattern = r'(?:github\.com/)([a-zA-Z0-9_-]+)'
    github_match = re.search(github_pattern, text, re.IGNORECASE)
    github = github_match.group(0) if github_match else None
    
    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github
    }

def analyze_resume(text):
    """
    Complete resume analysis
    """
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
        "full_text": text,
        "word_count": len(text.split())
    }

# ============================================
# LINKEDIN INTEGRATION
# ============================================

def generate_linkedin_search_url(resume_data, location=""):
    """
    Generate LinkedIn job search URL based on resume skills
    """
    skills = resume_data.get("skills", [])
    job_title = resume_data.get("job_title", "")
    
    # Build search query
    if skills:
        # Use top 3 skills for search
        top_skills = skills[:3]
        search_query = " ".join(top_skills)
    elif job_title and job_title != "Not detected":
        search_query = job_title
    else:
        search_query = "software engineer"
    
    # Encode for URL
    encoded_query = quote(search_query)
    encoded_location = quote(location) if location else ""
    
    # Build LinkedIn URL
    url = f"{LINKEDIN_BASE_URL}?keywords={encoded_query}"
    
    if encoded_location:
        url += f"&location={encoded_location}"
    
    return url, search_query

def open_linkedin_jobs(resume_data, location=""):
    """
    Open LinkedIn job search in browser
    """
    url, query = generate_linkedin_search_url(resume_data, location)
    
    try:
        webbrowser.open(url)
        return True, url, query
    except Exception as e:
        return False, url, query

# ============================================
# JOB MATCHING FUNCTIONS
# ============================================

def calculate_match_score(resume_skills, job_description):
    """
    Calculate how well resume matches a job description
    """
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
    """
    Match resume against job listings
    """
    resume_skills = resume_data.get("skills", [])
    results = []
    
    for job in jobs:
        match_score, matched, missing = calculate_match_score(
            resume_skills, 
            job.get("description", "")
        )
        
        # Boost score if job title contains relevant keywords
        title_lower = job.get("title", "").lower()
        for skill in resume_skills:
            if skill.lower() in title_lower:
                match_score += 5
        
        # Cap at 100
        match_score = min(100, match_score)
        
        results.append({
            **job,
            "match_score": match_score,
            "matched_skills": matched,
            "missing_skills": missing[:5]
        })
    
    # Sort by match score
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results

# ============================================
# DEMO JOBS DATABASE
# ============================================

def get_demo_jobs(search_query=""):
    """
    Get demo jobs for testing
    """
    demo_jobs = [
        {
            "title": "Senior Python Developer",
            "company": "TechCorp Inc.",
            "location": "Remote",
            "salary": 120000,
            "description": "We are looking for a Senior Python Developer with experience in Django, Flask, PostgreSQL, Docker, and AWS. Must have 5+ years of experience with Python and machine learning.",
            "url": "#",
            "date_posted": "2024-01-15",
            "source": "Demo"
        },
        {
            "title": "Full Stack JavaScript Developer",
            "company": "StartupXYZ",
            "location": "San Francisco, CA",
            "salary": 95000,
            "description": "Join our team! We're seeking a Full Stack Developer with React, Node.js, MongoDB, TypeScript, and Docker experience. Experience with AWS is a plus.",
            "url": "#",
            "date_posted": "2024-01-14",
            "source": "Demo"
        },
        {
            "title": "Data Scientist",
            "company": "DataDriven Co.",
            "location": "New York, NY",
            "salary": 130000,
            "description": "Looking for a Data Scientist with Python, TensorFlow, SQL, pandas, and machine learning experience. Background in statistics and deep learning required.",
            "url": "#",
            "date_posted": "2024-01-13",
            "source": "Demo"
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudFirst Ltd.",
            "location": "Austin, TX",
            "salary": 110000,
            "description": "Seeking DevOps Engineer with AWS, Docker, Kubernetes, Terraform, Jenkins, and CI/CD experience. Must have strong Linux skills.",
            "url": "#",
            "date_posted": "2024-01-12",
            "source": "Demo"
        },
        {
            "title": "Frontend Developer",
            "company": "WebAgency",
            "location": "Remote",
            "salary": 85000,
            "description": "Frontend Developer needed with React, TypeScript, CSS, HTML, and JavaScript skills. Experience with Figma and responsive design is a plus.",
            "url": "#",
            "date_posted": "2024-01-11",
            "source": "Demo"
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Innovations",
            "location": "Seattle, WA",
            "salary": 145000,
            "description": "ML Engineer with PyTorch, TensorFlow, deep learning, and Python experience required. PhD preferred. Experience with NLP and computer vision.",
            "url": "#",
            "date_posted": "2024-01-10",
            "source": "Demo"
        },
        {
            "title": "Backend Developer",
            "company": "ServerSide Inc.",
            "location": "Chicago, IL",
            "salary": 100000,
            "description": "Backend Developer with Java, Spring Boot, MySQL, and PostgreSQL experience required. Experience with microservices and REST APIs.",
            "url": "#",
            "date_posted": "2024-01-09",
            "source": "Demo"
        },
        {
            "title": "Product Manager",
            "company": "ProductFirst",
            "location": "Boston, MA",
            "salary": 115000,
            "description": "Product Manager with agile, scrum, and technical background preferred. Experience with Jira, Confluence, and roadmap planning.",
            "url": "#",
            "date_posted": "2024-01-08",
            "source": "Demo"
        },
        {
            "title": "Software Engineer",
            "company": "TechStart",
            "location": "Remote",
            "salary": 105000,
            "description": "Software Engineer with Python, JavaScript, React, Docker, and AWS experience. Must have strong problem-solving skills and experience with git.",
            "url": "#",
            "date_posted": "2024-01-07",
            "source": "Demo"
        },
        {
            "title": "Cloud Engineer",
            "company": "CloudSolutions",
            "location":
