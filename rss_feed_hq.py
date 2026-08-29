import feedparser
from flask import Flask, render_template, request
import time
import math

app = Flask(__name__)

# Updated feeds (MarketWatch feed replaced with a reliable WSJ RSS feed)
RSS_FEEDS = {
    "Hacker News": "https://news.ycombinator.com/rss",
    "Reddit Machine Learning": "https://www.reddit.com/r/MachineLearning/.rss",
    "Wall Street Tech": "https://feeds.a.dj.com/rss/RSSWSJD.xml",
    "Reddit muslim Ventures": "https://www.reddit.com/r/MuslimVentures/",
}

# Custom User-Agent to bypass 403 Forbidden blocks
AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_entry_date(entry):
    if hasattr(entry[1], 'published_parsed') and entry[1].published_parsed:
        return entry[1].published_parsed
    if hasattr(entry[1], 'updated_parsed') and entry[1].updated_parsed:
        return entry[1].updated_parsed
    return time.gmtime(0)

def fetch_feed(url):
    return feedparser.parse(url, agent=AGENT)

@app.route("/")
def index():
    articles = []
    for source, feed_url in RSS_FEEDS.items():
        parsed_feed = fetch_feed(feed_url)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    articles = sorted(articles, key=get_entry_date, reverse=True)

    page = request.args.get("page", 1, type=int)
    per_page = 10
    total_articles = len(articles)
    total_pages = math.ceil(total_articles / per_page) if total_articles > 0 else 1

    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    return render_template('index.html', articles=paginated_articles, page=page, total_pages=total_pages)

@app.route("/search")
def search():
    query = request.args.get('q', '').strip().lower()
    page = request.args.get("page", 1, type=int)
    per_page = 10
    
    if not query:
        return render_template("search_results.html", articles=[], query="", page=1, total_pages=1)

    articles = []
    for source, feed_url in RSS_FEEDS.items():
        parsed_feed = fetch_feed(feed_url)
        for entry in parsed_feed.entries:
            title = getattr(entry, 'title', '')
            summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
            
            if query in title.lower() or query in summary.lower():
                articles.append((source, entry))

    articles = sorted(articles, key=get_entry_date, reverse=True)

    total_articles = len(articles)
    total_pages = math.ceil(total_articles / per_page) if total_articles > 0 else 1
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = articles[start:end]

    return render_template("search_results.html", articles=paginated_results, query=query, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=True)