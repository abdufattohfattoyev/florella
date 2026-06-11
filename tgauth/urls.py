from django.urls import path
from . import views

app_name = 'tgauth'

urlpatterns = [
    path('login/',             views.login_view,  name='login'),
    path('logout/',            views.logout_view, name='logout'),
    path('new-code/',          views.new_code,    name='new_code'),
    path('check/<str:code>/',  views.check_code,  name='check_code'),
    path('webhook/',           views.bot_webhook, name='webhook'),
]
