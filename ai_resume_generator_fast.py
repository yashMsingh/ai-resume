"""
Groq AI Resume Generator with Fast Timeout Protection
Fastest and most reliable option
"""

import os
from dotenv import load_dotenv
import json
import sys
import threading
from typing import Optional, Dict

# Load environment variables
load_dotenv()

class ResumeGeneratorTimeout:
    """Groq Resume Generator with timeout protection"""
    
    def __init__(self, timeout_seconds=12):
        """Initialize with timeout - Groq is very fast"""
        self.timeout_seconds = timeout_seconds
        self.result = None
        self.client = None
        self.model = "mixtral-8x7b-32768"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client safely"""
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                print("[!] GROQ_API_KEY not found in .env")
                return
            
            from groq import Groq
            self.client = Groq(api_key=api_key)
            print("[OK] Groq client ready (12s timeout)")
        except Exception as e:
            print(f"[!] Groq init failed: {e}")
    
    def generate_with_timeout(self, prompt: str) -> Optional[str]:
        """Generate content with timeout - Groq is typically <5 seconds"""
        if not self.client:
            return None
        
        result = {"content": None, "error": None}
        
        def generate():
            try:
                message = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a professional resume writer. Create compelling, professional resumes. Be concise but impactful."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.model,
                    temperature=0.7,
                    max_tokens=1200,
                    top_p=1,
                )
                result["content"] = message.choices[0].message.content
            except Exception as e:
                result["error"] = str(e)
        
        # Run in thread with timeout
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout_seconds + 2)
        
        if thread.is_alive():
            print("[!] Timeout - using template")
            return None
        
        return result.get("content") or None
    
    def create_resume_prompt(self, profile_data: Dict, job_title: Optional[str] = None) -> str:
        """Create concise prompt for Groq"""
        job_focus = f" for {job_title}" if job_title else ""
        
        return f"""Create a professional resume{job_focus}:

{profile_data.get('name', 'Professional')} | {profile_data.get('location', 'Location')}

SUMMARY: {profile_data.get('about', 'Professional with proven track record.')}

EXPERIENCE:
{chr(10).join(profile_data.get('experience', []))}

EDUCATION: {', '.join(profile_data.get('education', ['']))}

SKILLS: {', '.join(profile_data.get('skills', []))}

Generate a professional resume with clear sections and strong action verbs."""
    
    def generate_resume(self, profile_data: Dict, job_title: Optional[str] = None) -> Dict:
        """Generate resume with timeout protection"""
        if not self.client:
            return self.create_template_resume(profile_data, job_title)
        
        try:
            prompt = self.create_resume_prompt(profile_data, job_title)
            print(f"[DEBUG] Groq generating ({self.timeout_seconds}s timeout)...")
            
            content = self.generate_with_timeout(prompt)
            
            if content:
                print("[OK] Groq success")
                return {"formatted_content": content.strip(), "sections": {}}
            else:
                return self.create_template_resume(profile_data, job_title)
        
        except Exception as e:
            print(f"[!] Error: {e}")
            return self.create_template_resume(profile_data, job_title)
    
    def create_template_resume(self, profile_data: Dict, job_title: Optional[str] = None) -> Dict:
        """Create professional template resume"""
        job_line = f"Target: {job_title}" if job_title else ""
        
        resume = f"""{profile_data.get('name', 'Your Name').upper()}
{profile_data.get('location', 'Location')}
{job_line}

PROFESSIONAL SUMMARY
{profile_data.get('about', 'Professional with strong background and proven track record of success.')}

CORE COMPETENCIES
"""
        
        for skill in profile_data.get('skills', [])[:12]:
            resume += f"• {skill}\n"
        
        resume += "\nPROFESSIONAL EXPERIENCE\n"
        for exp in profile_data.get('experience', []):
            resume += f"{exp}\n\n"
        
        if profile_data.get('education'):
            resume += "EDUCATION\n"
            for edu in profile_data['education']:
                resume += f"• {edu}\n"
        
        return {"formatted_content": resume.strip(), "sections": {}}

    
    def generate_with_timeout(self, prompt: str) -> Optional[str]:
        """Generate content with timeout"""
        if not self.model:
            return None
        
        result = {"content": None, "error": None}
        
        def generate():
            try:
                response = self.model.generate_content(prompt, timeout=self.timeout_seconds)
                result["content"] = response.text if response else None
            except Exception as e:
                result["error"] = str(e)
        
        # Run in thread
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout_seconds + 5)  # Extra 5 second safety margin
        
        if thread.is_alive():
            print("[!] AI generation timed out after 20 seconds - using template")
            return None
        
        return result.get("content") or None
    
    def create_resume_prompt(self, profile_data: Dict, job_title: Optional[str] = None) -> str:
        """Create resume generation prompt"""
        job_focus = f" for a {job_title} position" if job_title else ""
        
        prompt = f"""Create a professional resume{job_focus} based on this data:

Name: {profile_data.get('name', 'Not provided')}
Title: {profile_data.get('headline', 'Not provided')}
Location: {profile_data.get('location', 'Not provided')}
About: {profile_data.get('about', 'Not provided')}

Experience:
{chr(10).join(profile_data.get('experience', []))}

Education:
{chr(10).join(profile_data.get('education', []))}

Skills: {', '.join(profile_data.get('skills', []))}

Create a professional resume with clear sections and strong action verbs."""
        
        return prompt
    
    def generate_resume(self, profile_data: Dict, job_title: Optional[str] = None) -> Dict:
        """Generate resume with timeout protection"""
        if not self.model:
            print("[DEBUG] AI not available, using template")
            return self.create_template_resume(profile_data, job_title)
        
        try:
            prompt = self.create_resume_prompt(profile_data, job_title)
            print("[DEBUG] Generating with AI (20 second timeout)...")
            
            content = self.generate_with_timeout(prompt)
            
            if content:
                print("[OK] AI generation successful")
                return {
                    "formatted_content": content,
                    "sections": {}
                }
            else:
                print("[!] AI generation timed out, using template")
                return self.create_template_resume(profile_data, job_title)
        
        except Exception as e:
            print(f"[!] Error: {e}")
            return self.create_template_resume(profile_data, job_title)
    
    def create_template_resume(self, profile_data: Dict, job_title: Optional[str] = None) -> Dict:
        """Create professional template resume"""
        job_line = f"Target: {job_title}" if job_title else ""
        
        resume = f"""{profile_data.get('name', 'Your Name').upper()}
{profile_data.get('location', 'Location')}
{job_line}

PROFESSIONAL SUMMARY
{profile_data.get('about', 'Professional with strong background.')}

CORE COMPETENCIES
"""
        
        for skill in profile_data.get('skills', [])[:12]:
            resume += f"- {skill}\n"
        
        resume += "\nPROFESSIONAL EXPERIENCE\n"
        for exp in profile_data.get('experience', []):
            resume += f"{exp}\n\n"
        
        if profile_data.get('education'):
            resume += "EDUCATION\n"
            for edu in profile_data['education']:
                resume += f"- {edu}\n"
        
        return {
            "formatted_content": resume.strip(),
            "sections": {}
        }


# Quick test
if __name__ == "__main__":
    test_data = {
        'name': 'John Doe',
        'headline': 'Senior Developer',
        'location': 'San Francisco, CA',
        'about': 'Experienced developer',
        'experience': ['Lead Developer at Tech Co (2020-2025)'],
        'education': ['BS Computer Science'],
        'skills': ['Python', 'JavaScript', 'React']
    }
    
    generator = ResumeGeneratorTimeout()
    result = generator.generate_resume(test_data, "Full Stack Developer")
    print(result['formatted_content'][:200])
