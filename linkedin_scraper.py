from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from bs4 import BeautifulSoup

class LinkedInScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Set up Chrome driver with options to avoid detection"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Run in headless mode (no browser window) to avoid compatibility issues
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Note: ChromeDriver might need to be installed separately or compatibility mode checked.")
            raise
    
    def scrape_profile(self, linkedin_url):
        """Scrape LinkedIn profile and return structured data"""
        try:
            print(f"Navigating to: {linkedin_url}")
            self.driver.get(linkedin_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Initialize profile data
            profile_data = {
                'name': '',
                'headline': '',
                'location': '',
                'about': '',
                'experience': [],
                'education': [],
                'skills': [],
                'url': linkedin_url
            }
            
            # Extract basic information
            profile_data['name'] = self.extract_name()
            profile_data['headline'] = self.extract_headline()
            profile_data['location'] = self.extract_location()
            profile_data['about'] = self.extract_about()
            
            # Scroll to load more content
            self.scroll_page()
            
            # Extract experience
            profile_data['experience'] = self.extract_experience()
            
            # Extract education
            profile_data['education'] = self.extract_education()
            
            # Extract skills
            profile_data['skills'] = self.extract_skills()
            
            return profile_data
            
        except Exception as e:
            print(f"Error scraping profile: {e}")
            return None
    
    def extract_name(self):
        """Extract user's name"""
        try:
            name_selectors = [
                "h1.text-heading-xlarge",
                "h1",
                ".pv-text-details__left-panel h1",
                ".ph5 h1"
            ]
            
            for selector in name_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    name = element.text.strip()
                    if name:
                        print(f"Found name: {name}")
                        return name
                except:
                    continue
            
            return "Name not found"
        except Exception as e:
            print(f"Error extracting name: {e}")
            return "Name not found"
    
    def extract_headline(self):
        """Extract user's headline/title"""
        try:
            headline_selectors = [
                ".text-body-medium.break-words",
                ".pv-text-details__left-panel .text-body-medium",
                ".ph5 .text-body-medium"
            ]
            
            for selector in headline_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    headline = element.text.strip()
                    if headline and len(headline) > 10:  # Avoid short irrelevant text
                        print(f"Found headline: {headline}")
                        return headline
                except:
                    continue
            
            return "Professional"
        except Exception as e:
            print(f"Error extracting headline: {e}")
            return "Professional"
    
    def extract_location(self):
        """Extract user's location"""
        try:
            location_selectors = [
                ".text-body-small.inline.t-black--light.break-words",
                ".pv-text-details__left-panel .text-body-small",
                ".ph5 .text-body-small"
            ]
            
            for selector in location_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    location = element.text.strip()
                    if location and "connections" not in location.lower():
                        print(f"Found location: {location}")
                        return location
                except:
                    continue
            
            return "Location not specified"
        except Exception as e:
            print(f"Error extracting location: {e}")
            return "Location not specified"
    
    def extract_about(self):
        """Extract about section"""
        try:
            about_selectors = [
                ".pv-shared-text-with-see-more .full-width",
                ".display-flex.ph5 .pv-shared-text-with-see-more",
                ".artdeco-card .pv-shared-text-with-see-more"
            ]
            
            for selector in about_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    about = element.text.strip()
                    if about:
                        print(f"Found about section (length: {len(about)})")
                        return about
                except:
                    continue
            
            return "No about section available"
        except Exception as e:
            print(f"Error extracting about: {e}")
            return "No about section available"
    
    def scroll_page(self):
        """Scroll page to load dynamic content"""
        try:
            # Scroll down to load experience and education sections
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        except Exception as e:
            print(f"Error scrolling: {e}")
    
    def extract_experience(self):
        """Extract work experience"""
        try:
            experiences = []
            
            # Try different selectors for experience section
            experience_selectors = [
                ".pvs-list__paged-list-item",
                ".experience-section .pv-entity__summary-info",
                ".pv-profile-section__card-item-v2"
            ]
            
            for selector in experience_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements[:5]:  # Limit to first 5 experiences
                            exp_text = element.text.strip()
                            if exp_text and len(exp_text) > 20:  # Filter meaningful content
                                experiences.append(exp_text)
                        break
                except:
                    continue
            
            print(f"Found {len(experiences)} experience entries")
            return experiences
            
        except Exception as e:
            print(f"Error extracting experience: {e}")
            return ["Experience information not available"]
    
    def extract_education(self):
        """Extract education information"""
        try:
            education = []
            
            education_selectors = [
                ".education-section .pv-entity__summary-info",
                ".pvs-list__paged-list-item .pvs-entity",
                ".pv-profile-section__card-item-v2"
            ]
            
            for selector in education_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements[:3]:  # Limit to first 3 education entries
                            edu_text = element.text.strip()
                            if edu_text and len(edu_text) > 15:
                                education.append(edu_text)
                        break
                except:
                    continue
            
            print(f"Found {len(education)} education entries")
            return education
            
        except Exception as e:
            print(f"Error extracting education: {e}")
            return ["Education information not available"]
    
    def extract_skills(self):
        """Extract skills"""
        try:
            skills = []
            
            # Try to find skills section
            skill_selectors = [
                ".pv-skill-category-entity__name-text",
                ".pvs-list__paged-list-item .mr1",
                ".skill-category-entity__name"
            ]
            
            for selector in skill_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements[:10]:  # Limit to first 10 skills
                            skill_text = element.text.strip()
                            if skill_text and len(skill_text) < 50:  # Skills should be short
                                skills.append(skill_text)
                        break
                except:
                    continue
            
            print(f"Found {len(skills)} skills")
            return skills
            
        except Exception as e:
            print(f"Error extracting skills: {e}")
            return ["Skills information not available"]
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()

# Test function
def test_scraper():
    scraper = LinkedInScraper()
    
    # Test with a public profile
    test_url = "https://www.linkedin.com/in/satyanadella"
    profile_data = scraper.scrape_profile(test_url)
    
    if profile_data:
        print("\n=== SCRAPED DATA ===")
        print(json.dumps(profile_data, indent=2))
    else:
        print("Failed to scrape profile")
    
    scraper.close()

if __name__ == "__main__":
    test_scraper()