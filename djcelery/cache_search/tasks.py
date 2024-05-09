from celery import current_task, shared_task, Celery
import redis
import requests
import json
from .utils import process_and_format_data
import logging

celery_app = Celery('djcelery')

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, update_cache.s(), name='update_cache_task')


@shared_task
def update_cache(search_q=None,scheduled_task=False):
    redis_conn = redis.StrictRedis(host='redis', port=6379, db=0)
    redis_conn.ping()
    print("Connected to Redis successfully!")


    try:
        if not search_q:

            # task_id = current_task.request.id
            # task_name = current_task.request.task
            # logging.info(f"Task ID: {task_id}, Task Name: {task_name}, Updating cache for search_q: {search_q}")
            search_q = redis_conn.get('search_q') or ''
            if not search_q:
                # Handle the case when search_q is still empty
                logging.warning("Empty search query. Skipping cache update.")
                return {'status': 'error', 'message': 'Empty search query. Cache update skipped.'}

        logging.info(f"Updating cache for search_q: {search_q}")

        # Clear only the relevant key in Redis
        redis_conn.delete(search_q)


        response = requests.get(f'https://newsapi.org/v2/everything?q={search_q}&apiKey=6131ba71b67840229498d60fbd334ee6')

        if response.status_code == 429:
            # Handle rate-limiting error
            logging.error("API rate limit exceeded. Cache update skipped.")
            return {'status': 'error', 'message': 'API rate limit exceeded. Cache update skipped.'}

        response.raise_for_status()
        news_data = response.json()

        articles = process_and_format_data(news_data)

        redis_conn.hset(search_q, 'articles', json.dumps(articles))
        redis_conn.expire(search_q, 60)

        logging.info(f"Cache updated successfully for search_q: {search_q}")

        # Return a value if needed
        return {'status': 'success', 'message': f'Cache updated for {search_q}'}

    except requests.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
        # Return an error value if needed
        return {'status': 'error', 'message': f'Error fetching data for {search_q}: {e}'}
