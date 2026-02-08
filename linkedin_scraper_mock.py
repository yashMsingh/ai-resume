"""
Mock LinkedIn Scraper for Testing
Use this when the actual Selenium scraper has compatibility issues
"""

class MockLinkedInScraper:
    """Mock scraper that returns sample data for testing"""
    
    def __init__(self):
        self.driver = None
    
    def scrape_profile(self, linkedin_url):
        """Return mock profile data for testing"""
        print(f"📋 Mock Mode: Using sample data instead of scraping {linkedin_url}")
        
        # Return realistic sample data
        profile_data = {
            'name': 'John Doe',
            'headline': 'Senior Software Engineer | Full Stack Developer',
            'location': 'San Francisco, CA',
            'about': 'Passionate software engineer with 8+ years of experience in building scalable web applications. Specialized in Python, JavaScript, and cloud technologies. Love solving complex problems and mentoring junior developers.',
            'experience': [
                'Senior Software Engineer at TechCorp Inc (2022-Present): Led development of microservices architecture, improved system performance by 40%, mentored team of 5 engineers',
                'Software Engineer at WebSolutions LLC (2019-2022): Developed and maintained 10+ production applications, implemented CI/CD pipelines, reduced deployment time by 60%',
                'Junior Developer at StartupXYZ (2018-2019): Built responsive web applications using React and Node.js, collaborated with cross-functional teams'
            ],
            'education': [
                'Bachelor of Science in Computer Science from State University (2018)',
                'AWS Solutions Architect Certification (2021)'
            ],
            'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'PostgreSQL', 'MongoDB', 'Git', 'REST APIs', 'Agile', 'System Design'],
            'url': linkedin_url
        }
        
        return profile_data
    
    def close(self):
        """Cleanup"""
        pass
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()
