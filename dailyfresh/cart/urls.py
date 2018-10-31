from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add$',views.CartAddView.as_view(),name='add'),  #购物车记录添加
    url(r'^count$',views.CartCountView.as_view(),name='count'),  #异步请求购物车商品数量
    url(r'^info$', views.CartInfoView.as_view(), name='info'),  # 购物车页面显示
    url(r'^update$', views.CartUpdateView.as_view(), name='update'),  # 购物车记录更新
    url(r'^delete$', views.CartDeleteView.as_view(), name='delete'),  # 购物车记录删除
]
