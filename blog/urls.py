from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^regist/$', views.regist, name='regist'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^index/$', views.index, name='index'),
    url(r'^newarticle/$', views.newarticle, name='newarticle'),
    url(r'^article/(?P<articleId>\d+)/$', views.article, name='article'),
    url(r'^delarticle/(?P<articleId>\d+)/$', views.delarticle, name='delarticle'),
    url(r'^editarticle/(?P<articleId>\d+)/$', views.editarticle, name='editarticle'),
    url(r'^user/(?P<hostId>\d+)/$', views.user, name='user'),
    url(r'^follow/(?P<hostId>\d+)/$', views.follow, name='follow'),
    url(r'^cancelfollow/(?P<hostId>\d+)/$', views.cancelfollow, name='cancelfollow'),
    url(r'^showfollow/(?P<hostId>\d+)/(?P<boo>\d)/$', views.showfollow, name='showfollow'),
    url(r'^timeline/$', views.timeline, name='timeline'),
]