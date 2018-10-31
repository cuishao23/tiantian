from django.conf.urls import url
from user import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^register$',views.RegisterView.as_view(),name='register'),#用户注册
    url(r'^login$',views.LoginView.as_view(),name='login'),#用户登录
    url(r'^loginout$',views.loginout,name='loginout'),#退出登录
    url(r'^change_passwd$', views.Change_passwdView.as_view(), name='change_passwd'),#修改密码
    url(r'^validate_code$',views.validate_code,name='validate_code'),#验证码
    url(r'^active/(?P<token>.*)$', views.ActiveView.as_view(), name='active'),#用户激活

    #'''利用装饰器判定登录-方法1 (推荐)'''
    url(r'^$', views.UserInfoView.as_view(), name='user'), # 用户中心-信息页
    url(r'^order/(?P<page>\d+)$', views.UserOrderView.as_view(), name='order'),  # 用户中心-订单页  #?P<value>的意思就是命名一个名字为value的组，匹配规则符合后面的\d+
    url(r'^address$', views.UserAddressView.as_view(), name='address'),  # 用户中心-地址页

    #'''利用装饰器判定登录-方法2'''
    # url(r'^$', login_required(views.UserInfoView.as_view()), name='user'), # 用户中心-信息页
    # url(r'^order$', login_required(views.UserOrderView.as_view()), name='order'),  # 用户中心-订单页
    # url(r'^address$', login_required(views.UserAddressView.as_view()), name='address'),  # 用户中心-地址页

    #''省市县三级联动'''
    url(r'^get_all_province$', views.get_all_province, name='get_all_province'),
    url(r'^get_city_by_pid$', views.get_city_by_pid, name='get_city_by_pid'),
    url(r'^get_area_by_cid$', views.get_area_by_cid, name='get_area_by_cid'),

]
