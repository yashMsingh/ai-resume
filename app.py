from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
from datetime import datetime
from ai_resume_generator import ResumeGenerator
from linkedin_scraper_mock import MockLinkedInScraper as LinkedInScraper
# To use actual Selenium scraper (may have compatibility issues), uncomment:
# from linkedin_scraper import LinkedInScraper
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
        
        # Start processing in background (for now, we'll do it synchronously)
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
    """Process LinkedIn URL and generate resume"""
    try:
        # Update progress
        current_progress[session_id]['status'] = 'Scraping LinkedIn profile...'
        current_progress[session_id]['progress'] = 20
        
        # Initialize scraper
        scraper = LinkedInScraper()
        profile_data = scraper.scrape_profile(linkedin_url)
        
        if not profile_data:
            return {
                'success': False,
                'error': 'Failed to scrape LinkedIn profile. Please check the URL and try again.'
            }
        
        # Update progress
        current_progress[session_id]['status'] = 'Generating resume with AI...'
        current_progress[session_id]['progress'] = 60
        
        # Initialize AI generator
        ai_generator = ResumeGenerator()  # Fixed class name
        resume_data = ai_generator.generate_resume_content(profile_data, job_title)
        
        # Update progress
        current_progress[session_id]['status'] = 'Creating PDF...'
        current_progress[session_id]['progress'] = 80
        
        # Generate PDF
        pdf_generator = PDFResumeGenerator()
        pdf_path = pdf_generator.create_resume_pdf(resume_data, profile_data)
        
        # Update progress
        current_progress[session_id]['status'] = 'Complete!'
        current_progress[session_id]['progress'] = 100
        current_progress[session_id]['resume_content'] = resume_data['formatted_content']
        current_progress[session_id]['pdf_path'] = pdf_path
        
        return {
            'success': True,
            'resume_content': resume_data['formatted_content'],
            'pdf_path': pdf_path
        }
        
    except Exception as e:
        current_progress[session_id]['status'] = f'Error: {str(e)}'
        current_progress[session_id]['error'] = str(e)
        return {
            'success': False,
            'error': str(e)
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
            return "Resume not found", 404
        
        resume_content = progress_data['resume_content']
        # Convert to HTML for better display
        html_content = resume_content.replace('\n', '<br>')
        
        return f"""
        <html>
        <head><title>Resume Preview</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px; line-height: 1.6;">
            <h2>Resume Preview</h2>
            <div style="border: 1px solid #ddd; padding: 20px; background: #f9f9f9;">
                {html_content}
            </div>
            <br>
            <a href="/download/{session_id}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Download PDF</a>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"Error previewing resume: {str(e)}", 500

if __name__ == '__main__':
    # Create output directory for generated files
    os.makedirs('output', exist_ok=True)
    app.run(debug=True, port=5000)