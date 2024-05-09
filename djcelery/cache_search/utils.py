import json

def process_and_format_data(news_data):
    articles = news_data.get('articles', [])
    formatted_articles = []

    for article in articles:
        formatted_article = {
            'title': article.get('title', ''),
            'description': article.get('description', ''),
            'url': article.get('url', ''),
        }
        formatted_articles.append(formatted_article)

    return formatted_articles
