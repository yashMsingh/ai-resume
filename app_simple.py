"""
Flask app for LinkedIn Resume Maker with AI Integration
Uses Gemini API for intelligent resume generation
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
from datetime import datetime
import sys
import traceback

# Try to import AI components
try:
    from ai_resume_generator_fast import ResumeGeneratorTimeout
    AI_AVAILABLE = True  # Groq with timeout protection
    print("[OK] Groq AI module loaded with timeout protection")
except Exception as e:
    print(f"[INFO] Groq AI not available: {e}")
    AI_AVAILABLE = False

from linkedin_scraper_mock import MockLinkedInScraper
from pdf_generator import PDFResumeGenerator

app = Flask(__name__)

# Global variables to store progress
current_progress = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_resume():
    try:
        linkedin_url = request.form['linkedin_url']
        job_title = request.form.get('job_title', '')
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        current_progress[session_id] = {
            'status': 'Starting...',
            'progress': 0,
            'resume_content': '',
            'error': None
        }
        
        # Start processing
        result = process_resume(linkedin_url, job_title, session_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'resume_content': result['resume_content'],
                'message': 'Resume generated successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

def process_resume(linkedin_url, job_title, session_id):
    """Process LinkedIn URL and generate resume with AI"""
    try:
        # Update progress
        current_progress[session_id]['status'] = 'Analyzing LinkedIn profile...'
        current_progress[session_id]['progress'] = 20
        print(f"[DEBUG] Getting profile data...")
        
        # Initialize scraper (mock version)
        scraper = MockLinkedInScraper()
        profile_data = scraper.scrape_profile(linkedin_url)
        
        if not profile_data:
            return {
                'success': False,
                'error': 'Failed to process profile. Please check the URL and try again.'
            }
        
        print(f"[DEBUG] Profile data received: {profile_data.get('name')}")
        
        # Update progress
        current_progress[session_id]['status'] = 'Generating professional resume with AI...'
        current_progress[session_id]['progress'] = 60
        
        # Use AI if available, otherwise use professional template
        if AI_AVAILABLE:
            try:
                print(f"[DEBUG] Starting AI generation with timeout protection...")
                ai_generator = ResumeGeneratorTimeout(timeout_seconds=20)
                resume_data = ai_generator.generate_resume(profile_data, job_title)
                print(f"[DEBUG] AI generation complete")
            except Exception as e:
                print(f"[!] AI generation failed: {e}. Using template instead.")
                import traceback
                traceback.print_exc()
                resume_data = create_professional_resume(profile_data, job_title)
        else:
            print("[DEBUG] Using professional template (AI not available)")
            resume_data = create_professional_resume(profile_data, job_title)
        
        print(f"[DEBUG] Resume content ready, generating PDF...")
        
        # Update progress
        current_progress[session_id]['status'] = 'Creating PDF...'
        current_progress[session_id]['progress'] = 80
        
        # Generate PDF
        pdf_generator = PDFResumeGenerator()
        pdf_path = pdf_generator.create_resume_pdf(resume_data, profile_data)
        
        print(f"[DEBUG] PDF created: {pdf_path}")
        
        # Update progress
        current_progress[session_id]['status'] = 'Complete!'
        current_progress[session_id]['progress'] = 100
        current_progress[session_id]['resume_content'] = resume_data['formatted_content']
        current_progress[session_id]['pdf_path'] = pdf_path
        
        print(f"[DEBUG] Resume generation complete")
        
        return {
            'success': True,
            'resume_content': resume_data['formatted_content'],
            'pdf_path': pdf_path
        }
        
    except Exception as e:
        print(f"[ERROR] Error in process_resume: {e}")
        import traceback
        traceback.print_exc()
        current_progress[session_id]['status'] = f'Error: {str(e)}'
        current_progress[session_id]['error'] = str(e)
        return {
            'success': False,
            'error': str(e)
        }

def create_professional_resume(profile_data, job_title=None):
    """Create a professional resume from profile data"""
    
    job_focus = f" - Optimized for {job_title} position" if job_title else ""
    
    resume_content = f"""{profile_data.get('name', 'Your Name').upper()}
{profile_data.get('location', 'Location').upper()}

PROFESSIONAL SUMMARY
{profile_data.get('about', 'Professional with strong background in multiple domains.')}
{"" if not job_title else f"Seeking opportunities as a {job_title}."}

CORE COMPETENCIES
"""
    
    # Add skills
    skills = profile_data.get('skills', [])
    if skills:
        resume_content += "\n".join([f"• {skill}" for skill in skills[:15]])  # Top 15 skills
    
    resume_content += "\n\nPROFESSIONAL EXPERIENCE\n"
    
    # Add experiences
    for exp in profile_data.get('experience', []):
        resume_content += f"{exp}\n\n"
    
    # Add education
    if profile_data.get('education'):
        resume_content += "EDUCATION\n"
        for edu in profile_data['education']:
            resume_content += f"• {edu}\n"
    
    return {
        'formatted_content': resume_content.strip(),
        'sections': {}
    }

@app.route('/progress/<session_id>')
def get_progress(session_id):
    """Get current progress for a session"""
    progress_data = current_progress.get(session_id, {
        'status': 'Session not found',
        'progress': 0,
        'error': 'Invalid session ID'
    })
    return jsonify(progress_data)

@app.route('/download/<session_id>')
def download_resume(session_id):
    """Download generated PDF resume"""
    try:
        progress_data = current_progress.get(session_id)
        if not progress_data or 'pdf_path' not in progress_data:
            return "Resume not found", 404
        
        pdf_path = progress_data['pdf_path']
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, download_name='resume.pdf')
        else:
            return "PDF file not found", 404
            
    except Exception as e:
        return f"Error downloading resume: {str(e)}", 500

@app.route('/preview/<session_id>')
def preview_resume(session_id):
    """Preview resume content"""
    try:
        progress_data = current_progress.get(session_id)
        if not progress_data or 'resume_content' not in progress_data:
            return jsonify({"error": "Resume not found"}), 404
        
        resume_content = progress_data['resume_content']
        
        return jsonify({
            "resume_text": resume_content
        })
        
    except Exception as e:
        return jsonify({"error": f"Error previewing resume: {str(e)}"}), 500

if __name__ == '__main__':
    # Create output directory for generated files
    os.makedirs('output', exist_ok=True)
    
    # Fix encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("LinkedIn Resume Maker with AI Integration")
    print("=" * 60)
    
    if AI_AVAILABLE:
        print("[OK] AI Mode: ENABLED (Groq - Fast & Reliable)")
        print("   - Groq Mixtral 8x7b model")
        print("   - Ultra-fast resume generation (<5s typical)")
        print("   - 12-second timeout protection")
        print("   - Automatic fallback to template")
    else:
        print("[!] AI Mode: DISABLED (Using professional template)")
        print("   - Professional resume template")
        print("   - Instant generation, no waiting")
        print("   - High-quality output")
    
    print("\n[->] Visit: http://127.0.0.1:5000 in your browser")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=5000)
