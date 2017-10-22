from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='sells'),
    url(r'news$', views.news, name='news'),
]