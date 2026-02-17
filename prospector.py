import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def scrape_website(url):
    """The Scout: Fetches website text."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return ' '.join(soup.get_text().split())[:3000]
    except:
        return "Scraping Failed"

def analyze_company(url):
    """The Brain: Returns structured analysis."""
    content = scrape_website(url)
    prompt = f"Analyze this company: {url}. Content: {content}. Provide: 1. Industry, 2. One AI Automation Idea, 3. A 1-sentence email hook. Format as a simple list."
    
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
    except:
        return "AI Analysis Failed"

def run_pipeline(url_list):
    """The Secretary: Loops and saves data."""
    results = []
    
    for url in url_list:
        print(f"🔄 Processing: {url}")
        
        # 1. Get the business analysis
        analysis = analyze_company(url)
        
        # 2. Generate the email draft based on that analysis
        email_draft = generate_email_draft(analysis)
        
        # 3. Save everything into ONE dictionary (one row in the CSV)
        results.append({
            "URL": url, 
            "Analysis": analysis, 
            "Email_Draft": email_draft
        })
    
    # Create a DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv("leads_report.csv", index=False)
    print("\n✅ Success! Your 'leads_report.csv' is ready with analyses and email drafts.")

def generate_email_draft(analysis_text):
    """The Closer: Turns analysis into a ready-to-send email."""
    prompt = f"""
    Based on this analysis: {analysis_text}
    
    Write a professional cold email from Zax (AI Automation Intern at ScandicTech) to the CEO of this company.
    - Subject line must be punchy and Nordic-business friendly.
    - Mention the specific AI automation idea we found.
    - Keep it under 150 words.
    - Use a respectful, innovative, and practical tone.
    """
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
    except:
        return "Email generation failed."

if __name__ == "__main__":
    # Add any Nordic or Tech websites you want to analyze here!
    companies_to_track = [
        "https://www.seedprogramming.org/",
        "https://softecnu.org/",
        "https://www.devsinc.com/",
        "https://arbisoft.com/"
    ]
    run_pipeline(companies_to_track)