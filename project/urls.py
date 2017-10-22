from django.conf.urls import include, url
from django.contrib import admin



from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', include('sells.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'),
    url(r'^sells/', include('sells.urls')),
    url(r'^admin/', admin.site.urls),
]

