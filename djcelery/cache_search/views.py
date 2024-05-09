import redis
import json
import requests
from django.shortcuts import render
from djcelery.celery import celery_app
from .tasks import update_cache
from .utils import process_and_format_data



def news_view(request):
    search_q = request.GET.get('q')

    if search_q is None or not search_q:
        try:
            response = requests.get('https://newsapi.org/v2/top-headlines?country=us&apiKey=6131ba71b67840229498d60fbd334ee6')
            response.raise_for_status()
            news_data = response.json()

            articles = process_and_format_data(news_data)

        except requests.RequestException as e:
            error_message = f"Error: {e}"
            return render(request, 'search.html', {'error_message': error_message})
    else:
        redis_conn = redis.StrictRedis(host='redis', port=6379, db=0)

        cached_data = redis_conn.hget(search_q, 'articles')
        if cached_data:
            print("DATA COMING FROM CACHE")
            articles = convert_json_to_list(cached_data)
        else:
            try:
                # Set search_q in Redis cache
                redis_conn.set('search_q', search_q)

                # Schedule the Celery task with the current search_q
                update_cache.apply_async(args=[search_q], countdown=0)

                response = requests.get(f'https://newsapi.org/v2/everything?q={search_q}&apiKey=6131ba71b67840229498d60fbd334ee6')
                response.raise_for_status()
                news_data = response.json()

                articles = process_and_format_data(news_data)

                redis_conn.hset(search_q, 'articles', json.dumps(articles))
                redis_conn.expire(search_q, 60)

            except requests.RequestException as e:
                error_message = f"Error: {e}"
                return render(request, 'error_template.html', {'error_message': error_message})

    return render(request, 'search.html', {'articles': articles, 'search_q': search_q})


def convert_json_to_list(cached_data):
    return json.loads(cached_data.decode('utf-8'))
