from django.conf.urls import url

from paste_app import views

app_name = 'paste'

urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^moje/$', views.moje, name='moje'),

]