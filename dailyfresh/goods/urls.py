from django.conf.urls import url
from . import views

urlpatterns = [
    #url(r'^$',views.index,name='index'),
    url(r'^index$',views.IndexView.as_view(),name='index'),  #首页
    url(r'^goods/(?P<goods_id>\d+)$',views.DetailView.as_view(),name='detail'), #详情页   #?P<value>的意思就是命名一个名字为value的组，匹配规则符合后面的\d+
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$',views.ListView.as_view(),name='list'), #列表页

]
