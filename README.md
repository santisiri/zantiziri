# Hacker News Scraper and AI Content Generator

This project is a Hacker News scraper that fetches articles, summarizes them, translates the summaries to Argentine Spanish, and generates video scripts based on the content. It uses OpenAI's GPT models for natural language processing tasks and provides a web-based dashboard for monitoring the scraping process.

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install the required dependencies:
   ```
   pip install flask flask-socketio requests beautifulsoup4 fake_useragent openai
   ```

3. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

4. Ensure you have the following project structure:
   ```
   project_root/
   ├── scrapper.py
   ├── templates/
   │   └── index.html
   └── hackernews_data.json (will be created automatically)
   ```

## Usage

To run the scraper and start the dashboard:

```
python scrapper.py [--dev]
```

- Use the `--dev` flag to use GPT-3.5-turbo instead of GPT-4 for development/testing purposes.

Once running, open a web browser and navigate to `http://localhost:5000` to view the dashboard.

## Features

1. **Hacker News Scraping**: Fetches the top stories from Hacker News.
2. **Content Filtering**: Filters stories based on relevance to technology topics.
3. **Article Summarization**: Uses OpenAI's GPT models to summarize article content.
4. **Translation**: Translates summaries to Argentine Spanish.
5. **Script Generation**: Creates video scripts based on the translated summaries.
6. **Web Dashboard**: Provides a real-time view of the scraping process and results.

## Key Components

### scrapper.py

This is the main script that handles the scraping process, AI interactions, and runs the web server.

Key functions:
```python:scrapper.py
startLine: 116
endLine: 155
```
<code_block_to_apply_changes_from>
```python:scrapper.py
startLine: 157
endLine: 191
```
- `scrape_article_content(url)`: Fetches and extracts the content of individual articles.

```python:scrapper.py
startLine: 193
endLine: 214
```
- `summarize_article(content, title)`: Generates a summary of the article using GPT.

```python:scrapper.py
startLine: 216
endLine: 231
```
- `translate_to_argentine_spanish(text)`: Translates the summary to Argentine Spanish.

```python:scrapper.py
startLine: 233
endLine: 266
```
- `create_script(summary, title)`: Generates a video script based on the translated summary.

```python:scrapper.py
startLine: 401
endLine: 459
```
- `main()`: Orchestrates the entire scraping and processing workflow.

### templates/index.html

This file contains the HTML template for the web dashboard.

```html:templates/index.html
startLine: 1
endLine: 54
```

## Configuration

- The script uses environment variables for configuration. Make sure to set the `OPENAI_API_KEY` environment variable with your OpenAI API key.
- The choice between GPT-4 and GPT-3.5-turbo is made using the `--dev` command-line argument.

## Data Storage

- Scraped data is stored in `hackernews_data.json` in the project root directory.

## Limitations and Considerations

- The script respects rate limits and includes random delays to avoid overloading the Hacker News website.
- CAPTCHA detection is implemented to handle potential anti-scraping measures.
- The script processes a maximum of 5 relevant articles per run to manage API usage and processing time.

## Troubleshooting

- If you encounter CAPTCHA or access issues, try adjusting the `random_delay()` function to increase wait times between requests.
- Ensure your OpenAI API key has sufficient credits and permissions for the models being used.

## Contributing

Contributions to improve the scraper, enhance the dashboard, or extend the AI capabilities are welcome. Please submit pull requests or open issues for any bugs or feature requests.

## License

[Specify your license here]
