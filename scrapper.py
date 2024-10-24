import requests
from bs4 import BeautifulSoup
import json
import logging
from urllib.parse import urlparse
import random
import time
from fake_useragent import UserAgent
import openai
import os
import mimetypes
import argparse
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize UserAgent
ua = UserAgent()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Scrape Hacker News and generate summaries and scripts.")
parser.add_argument("--dev", action="store_true", help="Use GPT-3.5-turbo instead of GPT-4")
args = parser.parse_args()

# Choose the model based on the --dev flag
MODEL = "gpt-3.5-turbo" if args.dev else "gpt-4"

# Flask app setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

PROMPT_FILE = 'prompt.txt'
DEFAULT_PROMPT = """You are an AI assistant tasked with creating engaging social media content. Your goal is to transform the given article summary into a captivating script for an influencer to present on platforms like TikTok or Instagram Reels.

Here's the format for the script:

1. Hook (Attention-grabbing opening line)
2. Introduction (Brief context about the topic)
3. Key Points (2-3 main takeaways from the article)
4. Call-to-Action (Encourage viewers to engage or learn more)

Keep the script concise, engaging, and suitable for a 60-second video. Use casual language and incorporate trending phrases or hashtags when appropriate.

Article Title: {title}
Article Summary: {summary}

Please generate the script based on this information."""

TAGS_FILE = 'tags.json'
DEFAULT_TAGS = [
    'artificial intelligence', 'ai', 'machine learning', 'deep learning', 'neural networks',
    # ... (other default tags) ...
]

def load_prompt():
    try:
        with open(PROMPT_FILE, 'r') as f:
            return f.read()
    except FileNotFoundError:
        save_prompt(DEFAULT_PROMPT)
        return DEFAULT_PROMPT

def save_prompt(prompt):
    with open(PROMPT_FILE, 'w') as f:
        f.write(prompt)

def load_tags():
    if os.path.exists(TAGS_FILE):
        with open(TAGS_FILE, 'r') as f:
            return json.load(f)
    else:
        save_tags(DEFAULT_TAGS)
        return DEFAULT_TAGS

def save_tags(tags):
    with open(TAGS_FILE, 'w') as f:
        json.dump(tags, f)

@app.route('/')
def index():
    scraped_url = "https://news.ycombinator.com"  # Default URL
    return render_template('index.html', scraped_url=scraped_url, dev_mode=args.dev)

@app.route('/get_prompt')
def get_prompt():
    return load_prompt()

@app.route('/save_prompt', methods=['POST'])
def save_prompt_route():
    new_prompt = request.json['prompt']
    save_prompt(new_prompt)
    return jsonify({"success": True})

@app.route('/get_tags')
def get_tags():
    return jsonify(load_tags())

@app.route('/save_tags', methods=['POST'])
def save_tags_route():
    new_tags = request.json['tags']
    save_tags(new_tags)
    return jsonify({"success": True})

def emit_log(message):
    print(message)  # Print to console
    socketio.emit('log_update', {'message': message})

def get_random_headers():
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def random_delay():
    time.sleep(random.uniform(1, 3))

def make_request(url, max_retries=3):
    for _ in range(max_retries):
        try:
            headers = get_random_headers()
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.warning(f"Request failed: {e}. Retrying...")
            random_delay()
    return None

def detect_captcha(response):
    captcha_indicators = [
        'captcha',
        'recaptcha',
        'Are you a robot?',
        'human verification',
        'security check',
        'prove you\'re not a robot'
    ]
    
    if any(indicator.lower() in response.text.lower() for indicator in captcha_indicators):
        return True
    
    soup = BeautifulSoup(response.text, 'html.parser')
    captcha_elements = soup.find_all(['div', 'iframe'], attrs={'class': ['captcha', 'g-recaptcha']})
    if captcha_elements:
        return True
    
    return False

def is_downloadable_content(url):
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()
    extension = os.path.splitext(path)[1]
    
    # List of extensions to avoid
    avoid_extensions = ['.mp3', '.mp4', '.wav', '.avi', '.mov', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']
    
    if extension in avoid_extensions:
        return True
    
    # Check mime type
    mime_type, _ = mimetypes.guess_type(url)
    if mime_type and not mime_type.startswith('text/'):
        return True
    
    return False

def scrape_hackernews(url):
    try:
        logging.info(f"Fetching stories from {url}")
        response = make_request(url)
        if not response:
            raise Exception(f"Failed to fetch stories from {url} after multiple attempts")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stories = []
        for item in soup.find_all('tr', class_='athing'):
            rank = item.find('span', class_='rank').text.strip('.')
            title_element = item.find('span', class_='titleline')
            title = title_element.a.text
            link = title_element.a['href']
            
            # Get the next sibling for additional info
            subtext = item.find_next_sibling('tr').find('td', class_='subtext')
            score = subtext.find('span', class_='score').text if subtext.find('span', class_='score') else "0 points"
            author = subtext.find('a', class_='hnuser').text if subtext.find('a', class_='hnuser') else "Unknown"
            comments_element = subtext.find_all('a')[-1].text
            comments = comments_element.split()[0] if comments_element.split()[0].isdigit() else "0"
            
            stories.append({
                "rank": int(rank),
                "title": title,
                "link": link if link.startswith('http') else f"{url}/{link}",
                "score": int(score.split()[0]),
                "author": author,
                "comments": int(comments)
            })
        
        logging.info(f"Successfully scraped {len(stories)} stories from {url}")
        return stories
        
    except Exception as e:
        logging.error(f"Error scraping stories: {e}")
        return None

def scrape_article_content(url):
    if is_downloadable_content(url):
        logging.warning(f"Skipping downloadable content: {url}")
        return None
    
    try:
        logging.info(f"Fetching article content from {url}")
        response = make_request(url)
        if not response:
            raise Exception("Failed to fetch article content after multiple attempts")
        
        if detect_captcha(response):
            logging.warning(f"CAPTCHA detected for {url}")
            return None
        
        # Check content type in response headers
        content_type = response.headers.get('Content-Type', '').lower()
        if not content_type.startswith('text/html'):
            logging.warning(f"Skipping non-HTML content: {url}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        logging.error(f"Error scraping article content: {e}")
        return None

def summarize_article(content, title):
    prompt = f"""Summarize the following article in a concise manner. The summary should be engaging and suitable for social media sharing. Include key points and any notable insights. If relevant, suggest how this information might be applicable or interesting to a general audience.

Title: {title}

Content: {content[:8000] if MODEL == "gpt-4-0613" else content[:4000]}

Summary:"""

    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250 if MODEL == "gpt-4-0613" else 150
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        return None

def translate_to_argentine_spanish(text):
    prompt = f"Translate the following text to Argentine Spanish:\n\n{text}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates text to Argentine Spanish."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Error translating text: {e}")
        return None

def create_script(summary, title):
    prompt = load_prompt()
    prompt = f"""Actúa como Santiago Siri en primera persona, reconocido emprendedor, programador y dedicador a la tecnología desde hace más de 20 años. Crea un guion para un video de noticias tecnológicas en redes sociales basado en el siguiente resumen y título. El guion debe reflejar la personalidad de Santiago: un tono auténtico, sin exageraciones ni superlativos innecesarios, pero siempre con una mirada crítica y equilibrada.

Presenta la noticia de manera imparcial, mostrando tanto los aspectos positivos como negativos del tema, invitando a la audiencia a pensar por sí misma. Comienza con un buen 'hook' que enganche a la audiencia de inmediato, captando su atención de forma genuina y directa, y termina con un llamado claro a la acción para que se suscriban al canal.

El tono del guion debe ser cercano pero informado, sin caer en el sensacionalismo. Evita el uso excesivo de superlativos, y usa un lenguaje que transmita seguridad y experiencia, pero sin sonar distante.

Instrucciones adicionales:
1. Evitar completamente el uso de superlativos.
2. No mencionar buzzwords o palabras de moda.
3. Explicar en detalle un aspecto saliente sobre la noticia que se está analizando en profundidad.

Título: {title}
Resumen: {summary}

El guion no puede exceder los 2000 caracteres y no debe incluir preguntas.

Importante: No uses descripciones de escena ni indicadores entre corchetes como [inicio], [fin], etc. El guion debe ser un monólogo continuo sin interrupciones ni acotaciones. Tampoco te presentes a ti mismo en el comienzo. Ve directo al tema que concierne al contenido.

Guion:"""

    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates scripts for social media videos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000 if MODEL == "gpt-4-0613" else 800
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Error creating script: {e}")
        return None

def save_to_json(stories):
    with open('hackernews_data.json', 'w') as f:
        json.dump(stories, f, indent=2)

def emit_article_update(article):
    socketio.emit('article_update', article)

def is_relevant_topic(title):
    relevant_keywords = load_tags()
    # Check if any of the keywords are in the title
    if any(keyword in title.lower() for keyword in relevant_keywords):
        return True
    
    # If no keyword match, use GPT to classify
    prompt = f"""Classify the following article title as either 'relevant' or 'not relevant' based on whether it's related to technology topics such as artificial intelligence, crypto, bitcoin, gaming, software development, coding, metaverse, and other cutting-edge tech fields. Also consider topics related to digital economy, universal basic income, digital democracy, and technology developments in Argentina.

Title: {title}

Classification:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that classifies article titles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        classification = response.choices[0].message['content'].strip().lower()
        return 'relevant' in classification
    except Exception as e:
        logging.error(f"Error classifying title: {e}")
        return False

def filter_stories(stories):
    return [story for story in stories if is_relevant_topic(story['title'])]

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(main)

@socketio.on('change_model')
def handle_change_model(data):
    global MODEL
    MODEL = data['model']
    print(f"Model changed to: {MODEL}")

@socketio.on('run_scraper')
def run_scraper(data):
    url = data['url']
    emit_log(f"Starting scraper for URL: {url}")
    socketio.start_background_task(main, url)

@app.route('/generate_images', methods=['POST'])
def generate_images():
    data = request.json
    prompt = data['prompt']
    # Replace with actual Midjourney API call
    images = call_midjourney_api(prompt)
    return jsonify({'images': images})

def call_midjourney_api(prompt):
    # This is a placeholder function. Replace with actual API call.
    # Example: response = requests.post('https://api.midjourney.com/generate', json={'prompt': prompt})
    # return response.json().get('images', [])
    return [
        'https://example.com/image1.jpg',
        'https://example.com/image2.jpg',
        'https://example.com/image3.jpg',
        'https://example.com/image4.jpg',
        'https://example.com/image5.jpg'
    ]

def main(url):
    logging.info(f"Using model: {MODEL}")
    stories = scrape_hackernews(url)
    if stories:
        # Filter stories based on relevance
        relevant_stories = filter_stories(stories)
        emit_log(f"Found {len(relevant_stories)} relevant stories out of {len(stories)} total stories.")
        
        sorted_stories = sorted(relevant_stories, key=lambda x: x['score'], reverse=True)
        processed_articles = 0
        processed_urls = set()  # To keep track of processed URLs
        
        for story in sorted_stories:
            if processed_articles >= 5:
                break
            
            if story['link'] in processed_urls:
                continue  # Skip if we've already processed this URL
            
            emit_log(f"Processing article {processed_articles + 1}:")
            emit_log(json.dumps(story, indent=2))
            
            if is_downloadable_content(story['link']):
                emit_log("Skipping downloadable content.")
                continue
            
            article_content = scrape_article_content(story['link'])
            if article_content and len(article_content) >= 500:
                emit_log(f"\nArticle content length: {len(article_content)} characters")
                
                summary = summarize_article(article_content, story['title'])
                if summary:
                    emit_log("\nArticle Summary:")
                    emit_log(summary)
                    
                    translated_summary = translate_to_argentine_spanish(summary)
                    if translated_summary:
                        emit_log("\nTranslated Summary (Argentine Spanish):")
                        emit_log(translated_summary)
                        
                        script = create_script(translated_summary, story['title'])
                        if script:
                            emit_log("\nVideo Script (as Santiago Siri):")
                            emit_log(script)
                            
                            # Update the story with new information
                            story['summary'] = summary
                            story['translated_summary'] = translated_summary
                            story['script'] = script
                            
                            # Emit the updated article to the frontend
                            emit_article_update(story)
                            
                            processed_articles += 1
                            processed_urls.add(story['link'])  # Mark this URL as processed
                        else:
                            emit_log("\nFailed to create script.")
                    else:
                        emit_log("\nFailed to translate summary.")
                else:
                    emit_log("\nFailed to generate summary.")
            elif article_content is None:
                emit_log("CAPTCHA detected, downloadable content, or failed to scrape. Skipping to next article.")
            else:
                emit_log("Article content too short. Skipping to next article.")
            
            random_delay()
        
        # Save the updated stories to JSON
        save_to_json(sorted_stories)
        
        emit_log(f"\nProcessed {processed_articles} articles successfully.")
        socketio.emit('scraping_complete')  # Add this line
    else:
        emit_log("Failed to scrape Hacker News")

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
