from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from user.models import *
import re
from django.views.generic import View
from utils.user_util import *
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.conf import settings
from io import BytesIO
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from celery_tasks.tasks import task_send_mail
from django.contrib.auth import authenticate, login,logout
from utils.user_util import LoginRequiredMixin
from django.core import serializers
from django.http import *
from redis import StrictRedis
from goods.models import *
from order.models import *
from django.core.paginator import Paginator

class RegisterView(View):
    def get(self,request):
        return render(request, 'register.html')
    def post(self,request):
        # 接受用户值
        uname = request.POST.get('user_name', '').strip()
        upwd = request.POST.get('pwd', '').strip()
        ucpwd = request.POST.get('cpwd', '').strip()
        uemail = request.POST.get('email', '').strip()
        uallow = request.POST.get('allow')

        # 进行校验
        if not all([uname, upwd, ucpwd, uemail]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        if upwd != ucpwd:
            # 两次密码不一致
            return render(request, 'register.html', {'errmsg': '两次密码不一致'})
        if not re.match('^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', uemail):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        if uallow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 验证用户名是否重复
        try:
            user = User.objects.get(username=uname)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理：进行用户注册
        user = User.objects.create_user(uname,uemail,upwd)
        user.is_active = 0  #未激活
        user.save()

        # 反应应答，跳转到首页
        #return redirect(reverse('user:login'))

        '''邮箱激活'''
        #
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode()
        encryption_url = 'http://192.168.12.189:8888/user/active/%s' % token
        # 发邮件
        subject = '天天欢迎你'
        message = ''
        sender = settings.EMAIL_FROM
        receiver = [uemail]
        html_message = '<h1>%s,欢迎注册</h1>点击链接<br/><a href="%s">%s</a>' % (uname, encryption_url, encryption_url)


        task_send_mail.delay(subject, message, sender, receiver, html_message)#发送
        return redirect(reverse('user:login'))


class ActiveView(View):
    print('nihao')
    '''用户激活'''
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']

            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            return redirect(reverse('user:login'))
        except SignatureExpired as e:

            return HttpResponse('激活链接以过期')
        except BadSignature as e:
            return HttpResponse('激活链接以非法')

class LoginView(View):
    def get(self,request):
        # 获取cookie
        remember_username = request.COOKIES.get('remember_username', '')
        return render(request, 'login.html', {'remember_username': remember_username})

    def post(self,request):
        # 获取属性
        validate = request.POST.get('validate_code', '').strip().lower()
        # 判断验证码
        if validate == '' or validate != request.session.get('validate_code').lower():
            # return HttpResponseRedirect(reverse("user:login"))
            return render(request, 'login.html', {'error_name': '数据不完整'})

        # 获取属性
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember')
        # pwd = my_md5(pwd)
        # print(pwd)

        # 进行校验
        if username == '' or password == '' or validate == '':
            # 数据不完整
            return render(request, 'login.html', {'error_name': '数据不完整'})
        # 查询
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)
                request.session['login_user_id'] = user.id

                #判断是否回到登录前的页面
                next_url=request.GET.get('next')
                #print(next_url)
                if next_url:
                    resp=redirect(next_url)
                else:
                    # 删除临时验证码
                    del request.session['validate_code']
                    # 跳转到首页
                    resp = redirect(reverse('goods:index'))

                # 记住用户名
                if remember == '1':
                    resp.set_cookie('remember_username', username, 3600 * 24 * 7)
                else:
                    resp.set_cookie('remember_username', username, 0)
                return resp
            else:
                # 用户未激活
                return render(request, 'login.html', {'error_name': '用户未激活'})

        else:
            return redirect(reverse('user:login'))

#退出登录
def loginout(request):
    logout(request)  # 注销用户
    return redirect(reverse('goods:index'))


#修改密码
class Change_passwdView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, "changepwd.html")
    def post(self, request):
        user = request.user

        old_password = request.POST.get("old_pwd")  # 获取原来的密码，默认为空字符串
        new_password = request.POST.get("new_pwd")  # 获取新密码，默认为空字符串
        confirm = request.POST.get("again_new_pwd")  # 获取确认密码，默认为空字符串

        if user.check_password(old_password):  # 到数据库中验证旧密码通过
            if new_password=='' or confirm=='':  # 新密码或确认密码为空
                return render(request, 'changepwd.html', {'errmsg': '新密码或确认密码为空'})
            elif new_password != confirm:  # 新密码与确认密码不一样
                return render(request, 'changepwd.html', {'errmsg': '两次密码不一致'})
            else:
                user.set_password(new_password)  # 修改密码
                user.save()
                return redirect(reverse('user:login'))

        else:
            return render(request, 'changepwd.html', {'errmsg': '旧密码输入错误'})



def validate_code(request):
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(
        20, 100), 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]

    #保存到session
    request.session['validate_code']=rand_str
    # 构造字体对象
    font = ImageFont.truetype(settings.FONT_STYLE, 23)
    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    for i in range(4):
        draw.text((5+20*i, 2), rand_str[i], font=font, fill=fontcolor)
    # draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    # draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    # draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    # draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw

    # 内存文件操作
    buf = BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')

class UserInfoView(LoginRequiredMixin,View):
    '''用户中心-信息页'''
    def get(self,request):
        # 获取登录用户对应的User对象
        user = request.user
        # 获取用户默认的用户地址
        try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            # 不存在默认地址
            address = None

        #读取历史记录
        #连接redis
        conn=StrictRedis('192.168.12.189')
        history=conn.lrange('history_%d' % user.id,0,-1)


        #goodskus=GoodsSKU.objects.filter(id__in=history)                       #按照商品添加顺序排序
        goodskus = [GoodsSKU.objects.get(id=goods_id) for goods_id in history]  #按照浏览商品前后添加顺序排序

        context={'page':'1','address':address,'goodskus':goodskus}
        return render(request,'user_center_info.html',context)

class UserOrderView(LoginRequiredMixin,View):
    '''用户中心-订单页'''
    def get(self, request,page):
        '''显示'''
        #获取用户的订单信息
        user=request.user
        orders=OrderInfo.objects.filter(user=user).order_by('-create_time')

        #遍历获取的商品的信息
        for order in orders:
            #根据order_id查询订单商品信息
            order_skus=OrderGoods.objects.filter(order_id=order.order_id)

            #遍历order_skus计算商品的小计
            for order_sku in order_skus:
                #计算小计
                amount=order_sku.count*order_sku.price
                #动态给order_sku增加属性amount,保存订单商品的小计
                order_sku.amount=amount

            #动态给order增加属性，保存订单商品的信息
            order.order_skus=order_skus

        #分页
        paginator=Paginator(orders,1)
        #获取地page页的Page实例对象
        try:
            page=int(page)
        except Exception as e:
            page=1

        if page>paginator.num_pages:
            page=1

        #获取page页的Page实例对象
        order_page=paginator.page(page)

        #进行页码的控制，页面上最多显示5个页面

        #1.总页数小于5页，页面上显示所有页面
        #2.如果当前页是前三页，显示1-5页
        #3.如果当前页是后三页，显示后5页
        #4.其他情况，显示当前页的钱2页，当前页，当前页的后2页
        num_pages=paginator.num_pages
        if num_pages<5:
            pages=range(1,num_pages+1)
        elif page<=3:
            pages=range(1,6)
        elif num_pages-page<=2:
            pages=range(num_pages-4,num_pages+1)
        else:
            pages=range(page-2,page+3)

        #组织上下文
        context = {
            'order_page': order_page,
            'pages': pages,
            'page': '2',

        }
        #使用模板
        return render(request, 'user_center_order.html', context)

class UserAddressView(LoginRequiredMixin,View):
    '''用户中心-地址页'''
    def get(self, request):
        #获取登录用户对应的User对象
        user=request.user
        #获取用户默认的用户地址
        try:
            address=Address.objects.get(user=user,is_default=True)
        except Address.DoesNotExist:
            #不存在默认地址
            address=None

        #数据字典
        context = {
            'page': '3',
            'address':address
        }
        #渲染
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        # 接收数据
        receiver = request.POST.get('receiver')
        addre = request.POST.get('address')
        print(type(addre))
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone', '').strip()

        province_id = request.POST.get('province_id')
        city_id = request.POST.get('city_id')
        area_id = request.POST.get('area_id')
        p=str(Province.objects.get(id=province_id))
        c=str(City.objects.get(id=city_id))
        a=str(Area.objects.get(id=area_id))

        # 进行校验
        if not all([receiver, addre, postcode, phone]):
            # 数据不完整
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})
        #邮编格式
        if not re.match('[1-9]\d{5}(?!\d)', postcode):
            return render(request, 'user_center_site.html', {'postcode_errmsg': '邮编格式不正确'})
        #手机号格式
        if not re.match('^1[3,4,5,7,8]\d{9}$', phone):
            return render(request, 'user_center_site.html', {'phone_errmsg': '手机号格式不正确'})


        #获取登录用户对应的User对象
        user = request.user
        try:
            address=Address.objects.get(user=user,is_default=True)
            address.is_default=False
            address.save()
        except Address.DoesNotExist:
            #不存在默认地址
            pass


        #添加地址
        Address.objects.create(
            user=user,
            receiver=receiver,
            address=p+c+a+addre,
            postcode=postcode,
            phone=phone,
            is_default=True,
        )
        return redirect(reverse('user:address')) #get请求


#获取所有的省份，转成json
def get_all_province(request):
    province_list=Province.objects.all()
    content={
        'province_list':serializers.serialize('json',province_list)
    }
    return JsonResponse(content)

#根据省份id获取下面的城市，转成json
def get_city_by_pid(request):
    province_id=request.GET.get('province_id')
    city_list=City.objects.filter(cprovince_id=province_id)
    content={
        'city_list':serializers.serialize('json',city_list)
    }
    return JsonResponse(content)

#根据市id获取下面的地区，转成json
def get_area_by_cid(request):
    city_id=request.GET.get('city_id')
    area_list=Area.objects.filter(acity_id=city_id)
    content={
        'area_list':serializers.serialize('json',area_list)
    }
    return JsonResponse(content)





