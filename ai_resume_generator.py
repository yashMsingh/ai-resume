"""
Groq AI Resume Generator with Timeout Protection
Faster and more reliable than Gemini
"""

import os
from dotenv import load_dotenv
import json
import sys
import threading
from typing import Optional, Dict

# Load environment variables
load_dotenv()

class ResumeGenerator:
    """Groq-based Resume Generator with timeout protection"""
    
    def __init__(self, timeout_seconds=15):
        """Initialize Groq with timeout"""
        self.timeout_seconds = timeout_seconds
        self.client = None
        self.model = "mixtral-8x7b-32768"  # Fast and powerful
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
            print("[OK] Groq client initialized (mixtral-8x7b-32768)")
        except Exception as e:
            print(f"[!] Groq initialization failed: {e}")
    
    def generate_with_timeout(self, prompt: str) -> Optional[str]:
        """Generate content with timeout"""
        if not self.client:
            return None
        
        result = {"content": None, "error": None}
        
        def generate():
            try:
                message = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a professional resume writer. Create compelling, professional resumes."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.model,
                    temperature=0.7,
                    max_tokens=1500,
                    top_p=1,
                    stream=False,
                )
                result["content"] = message.choices[0].message.content
            except Exception as e:
                result["error"] = str(e)
        
        # Run in thread with timeout
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout_seconds + 3)  # Extra 3 second safety margin
        
        if thread.is_alive():
            print("[!] Groq generation timed out - using template")
            return None
        
        return result.get("content") or None
    
    def create_resume_prompt(self, profile_data: Dict, job_title: Optional[str] = None) -> str:
        """Create resume generation prompt for Groq"""
        job_focus = f" optimized for a {job_title} position" if job_title else ""
        
        prompt = f"""Create a professional resume{job_focus} based on this information:

Name: {profile_data.get('name', 'Professional')}
Headline: {profile_data.get('headline', 'Experienced Professional')}
Location: {profile_data.get('location', 'Not specified')}

Professional Summary:
{profile_data.get('about', 'Professional with strong background in multiple domains.')}

Professional Experience:
{chr(10).join('• ' + exp for exp in profile_data.get('experience', ['Experience not provided']))}

Education:
{chr(10).join('• ' + edu for edu in profile_data.get('education', ['Education not provided']))}

Key Skills: {', '.join(profile_data.get('skills', []))}

Requirements:
- Use professional language with action verbs
- Include quantifiable achievements where possible
- Format with clear sections
- Optimize for Applicant Tracking Systems (ATS)
- Keep content concise but impactful
- Use bullet points for experience

Generate a professional resume in text format:"""
        
        return prompt
    
    def generate_resume_content(self, profile_data: Dict, job_title: Optional[str] = None) -> Dict:
        """Generate resume with timeout protection"""
        if not self.client:
            print("[DEBUG] Groq not available, using template")
            return self.create_template_resume(profile_data, job_title)
        
        try:
            prompt = self.create_resume_prompt(profile_data, job_title)
            print(f"[DEBUG] Generating with Groq ({self.timeout_seconds}s timeout)...")
            
            content = self.generate_with_timeout(prompt)
            
            if content:
                print("[OK] Groq generation successful")
                return {
                    "formatted_content": content.strip(),
                    "sections": {}
                }
            else:
                print("[!] Groq generation timed out, using template")
                return self.create_template_resume(profile_data, job_title)
        
        except Exception as e:
            print(f"[!] Error: {e}")
            return self.create_template_resume(profile_data, job_title)
    
    def create_template_resume(self, profile_data: Dict, job_title: Optional[str] = None) -> Dict:
        """Create professional template resume"""
        job_line = f"Target Role: {job_title}" if job_title else ""
        
        resume = f"""{profile_data.get('name', 'Your Name').upper()}
{profile_data.get('location', 'Location')}
{job_line}

PROFESSIONAL SUMMARY
{profile_data.get('about', 'Professional with strong background and proven track record of success.')}

CORE COMPETENCIES
"""
        
        # Add top skills
        skills = profile_data.get('skills', [])
        for skill in skills[:15]:
            resume += f"• {skill}\n"
        
        resume += "\nPROFESSIONAL EXPERIENCE\n"
        
        # Add experience
        for exp in profile_data.get('experience', []):
            if isinstance(exp, dict):
                title = exp.get('title', 'Position')
                company = exp.get('company', '')
                desc = exp.get('description', '')
                resume += f"{title}"
                if company:
                    resume += f" | {company}"
                resume += "\n"
                if desc:
                    resume += f"{desc}\n"
            else:
                resume += f"{exp}\n"
            resume += "\n"
        
        # Add education
        if profile_data.get('education'):
            resume += "EDUCATION\n"
            for edu in profile_data['education']:
                if isinstance(edu, dict):
                    degree = edu.get('degree', 'Degree')
                    school = edu.get('school', '')
                    resume += f"• {degree}"
                    if school:
                        resume += f" - {school}"
                    resume += "\n"
                else:
                    resume += f"• {edu}\n"
        
        return {
            "formatted_content": resume.strip(),
            "sections": {}
        }
        """Initialize the AI resume generator with Gemini API"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Lazy import to avoid startup issues
        try:
            import google.genai as genai
            genai.configure(api_key=api_key)
            
            # Try different model names (most likely working ones first)
            self.model = None
            model_names = [
                'gemini-2.0-flash',
                'gemini-1.5-flash',
                'gemini-1.5-pro',
                'gemini-pro'
            ]
            
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    # Test the model with a simple request
                    test_response = self.model.generate_content("Hello")
                    print(f"✓ Using model: {model_name}")
                    break
                except Exception as e:
                    print(f"✗ Model {model_name} failed: {str(e)}")
                    continue
            
            if not self.model:
                raise ValueError("No working Gemini model found")
        except ImportError:
            # Fallback to old package if new one not available
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✓ Using google.generativeai (legacy)")
            except Exception as e:
                raise ValueError(f"Failed to initialize AI: {e}")
    
    def generate_resume_content(self, profile_data, job_title=None):
        """Generate professional resume content using AI"""
        try:
            # Create detailed prompt for resume generation
            prompt = self.create_resume_prompt(profile_data, job_title)
            
            print("→ Generating resume content with AI...")
            response = self.model.generate_content(prompt)
            
            if response.text:
                return self.parse_resume_response(response.text)
            else:
                return self.create_fallback_resume(profile_data)
                
        except Exception as e:
            print(f"✗ AI generation error: {str(e)}")
            return self.create_fallback_resume(profile_data)
    
    def create_resume_prompt(self, profile_data, job_title):
        """Create a detailed prompt for AI resume generation"""
        job_focus = f" for a {job_title} position" if job_title else ""
        
        prompt = f"""
        Create a professional resume{job_focus} based on the following LinkedIn profile data:

        Name: {profile_data.get('name', 'Not provided')}
        Current Role: {profile_data.get('headline', 'Not provided')}
        Location: {profile_data.get('location', 'Not provided')}
        About: {profile_data.get('about', 'Not provided')}

        Experience:
        {self.format_experience_for_prompt(profile_data.get('experience', []))}

        Education:
        {self.format_education_for_prompt(profile_data.get('education', []))}

        Skills: {', '.join(profile_data.get('skills', []))}

        Please create a professional resume with the following sections:
        1. PROFESSIONAL SUMMARY (2-3 sentences highlighting key strengths)
        2. CORE COMPETENCIES (bullet points of key skills)
        3. PROFESSIONAL EXPERIENCE (detailed bullet points with achievements)
        4. EDUCATION
        5. TECHNICAL SKILLS

        Guidelines:
        - Use action verbs and quantifiable achievements where possible
        - Keep bullet points concise but impactful
        - Tailor content to be ATS-friendly
        - Make it professional and modern
        - Focus on results and impact

        Format the response as structured text with clear section headers.
        """
        
        return prompt
    
    def format_experience_for_prompt(self, experiences):
        """Format experience data for the AI prompt"""
        if not experiences:
            return "No experience data provided"
        
        formatted = []
        for exp in experiences:
            # Handle both string and dict formats
            if isinstance(exp, dict):
                exp_text = f"- {exp.get('title', 'Unknown')}"
                if exp.get('company'):
                    exp_text += f" at {exp['company']}"
                if exp.get('description'):
                    exp_text += f": {exp['description']}"
            else:
                # String format from scraper
                exp_text = f"- {exp}"
            formatted.append(exp_text)
        
        return '\n'.join(formatted)
    
    def format_education_for_prompt(self, education):
        """Format education data for the AI prompt"""
        if not education:
            return "No education data provided"
        
        formatted = []
        for edu in education:
            # Handle both string and dict formats
            if isinstance(edu, dict):
                edu_text = f"- {edu.get('degree', 'Unknown degree')}"
                if edu.get('school'):
                    edu_text += f" from {edu['school']}"
            else:
                # String format from scraper
                edu_text = f"- {edu}"
            formatted.append(edu_text)
        
        return '\n'.join(formatted)
    
    def parse_resume_response(self, ai_response):
        """Parse AI response into structured resume data"""
        try:
            # Split response into sections
            sections = {}
            current_section = None
            current_content = []
            
            lines = ai_response.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a section header
                if any(header in line.upper() for header in [
                    'PROFESSIONAL SUMMARY', 'SUMMARY', 'OBJECTIVE',
                    'CORE COMPETENCIES', 'SKILLS', 'TECHNICAL SKILLS',
                    'PROFESSIONAL EXPERIENCE', 'EXPERIENCE', 'WORK EXPERIENCE',
                    'EDUCATION', 'ACADEMIC BACKGROUND'
                ]):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = line
                    current_content = []
                else:
                    current_content.append(line)
            
            # Add last section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            
            return {
                'formatted_content': ai_response,
                'sections': sections
            }
            
        except Exception as e:
            print(f"Error parsing AI response: {str(e)}")
            return {
                'formatted_content': ai_response,
                'sections': {}
            }
    
    def create_fallback_resume(self, profile_data):
        """Create a basic resume if AI generation fails"""
        print("🔄 Creating fallback resume...")
        
        resume_content = f"""
{profile_data.get('name', 'Your Name')}
{profile_data.get('location', 'Location')}

PROFESSIONAL SUMMARY
{profile_data.get('about', 'Professional with experience in various roles and responsibilities.')}

PROFESSIONAL EXPERIENCE
"""
        
        # Add experiences
        for exp in profile_data.get('experience', []):
            if isinstance(exp, dict):
                resume_content += f"\n{exp.get('title', 'Position')}"
                if exp.get('company'):
                    resume_content += f" | {exp['company']}"
                if exp.get('description'):
                    resume_content += f"\n• {exp['description']}"
            else:
                # String format from scraper
                resume_content += f"\n{exp}"
            resume_content += "\n"
        
        # Add education
        if profile_data.get('education'):
            resume_content += "\nEDUCATION\n"
            for edu in profile_data['education']:
                if isinstance(edu, dict):
                    resume_content += f"{edu.get('degree', 'Degree')} | {edu.get('school', 'Institution')}\n"
                else:
                    # String format from scraper
                    resume_content += f"{edu}\n"
        
        # Add skills
        if profile_data.get('skills'):
            resume_content += f"\nSKILLS\n{', '.join(profile_data['skills'])}\n"
        
        return {
            'formatted_content': resume_content.strip(),
            'sections': {}
        }

# Test function
if __name__ == "__main__":
    try:
        generator = ResumeGenerator()
        
        # Test data
        test_profile = {
            'name': 'Test User',
            'headline': 'Software Developer',
            'about': 'Experienced developer with passion for creating innovative solutions',
            'experience': [
                {
                    'title': 'Senior Developer',
                    'company': 'Tech Corp',
                    'description': 'Led development of web applications'
                }
            ],
            'education': [
                {
                    'degree': 'Computer Science',
                    'school': 'University'
                }
            ],
            'skills': ['Python', 'JavaScript', 'React']
        }
        
        result = generator.generate_resume_content(test_profile, "Full Stack Developer")
        print("✅ Resume generated successfully!")
        print("\n" + "="*50)
        print(result['formatted_content'])
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")