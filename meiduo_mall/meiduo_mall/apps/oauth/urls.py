from django.conf.urls import url

from .views import QQAuthUserView
from .views import QQAuthURLView

urlpatterns = [
    url(r'^qq/authorization/$', QQAuthURLView.as_view()),
    url(r'^qq/user/$', QQAuthUserView.as_view())
]