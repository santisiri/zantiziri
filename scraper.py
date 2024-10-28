import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape(self, url):
        """
        Scrapes content from the given URL.
        Returns a string containing the main content of the page.
        """
        try:
            # Fetch the webpage
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # If it's Hacker News, handle it differently
            if 'news.ycombinator.com' in url:
                return self._scrape_hackernews(soup)
            
            # For other websites, try to get the main content
            return self._extract_main_content(soup)

        except Exception as e:
            raise Exception(f"Failed to scrape URL: {str(e)}")

    def _scrape_hackernews(self, soup):
        """
        Special handling for Hacker News website
        """
        stories = []
        
        # Find all story rows
        story_rows = soup.find_all('tr', class_='athing')
        
        for story in story_rows:
            try:
                # Get the title and link
                title_cell = story.find('td', class_='title')
                if not title_cell:
                    continue
                
                title_link = title_cell.find('a', class_='titlelink') or title_cell.find('a', class_='storylink')
                if not title_link:
                    continue

                title = title_link.get_text(strip=True)
                story_url = title_link.get('href')
                
                # Get the subtext (points, author, time, comments)
                subtext = story.find_next_sibling('tr')
                if subtext:
                    subtext = subtext.find('td', class_='subtext')
                    if subtext:
                        subtext = subtext.get_text(strip=True)
                    else:
                        subtext = "No additional information"
                
                # Combine the information
                story_text = f"Title: {title}\nURL: {story_url}\nDetails: {subtext}\n"
                stories.append(story_text)

            except Exception as e:
                print(f"Error processing story: {str(e)}")
                continue

        if not stories:
            raise Exception("No stories found on Hacker News")

        # Combine all stories into one text
        return "\n\n".join(stories)

    def _extract_main_content(self, soup):
        """
        Attempts to extract the main content from a generic webpage
        """
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()

        # Try to find main content containers
        main_content = None
        possible_content_tags = [
            soup.find('main'),
            soup.find('article'),
            soup.find('div', class_=['content', 'main-content', 'post-content']),
            soup.find('div', {'role': 'main'})
        ]
        
        for tag in possible_content_tags:
            if tag:
                main_content = tag
                break
        
        # If no main content container found, use body
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Get text while preserving some structure
            paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content = '\n\n'.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            return content
        
        # Fallback: just get all text
        return soup.get_text()
