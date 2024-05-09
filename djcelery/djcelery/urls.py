from django.contrib import admin
from django.urls import path
from cache_search.views import news_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',news_view)
]
