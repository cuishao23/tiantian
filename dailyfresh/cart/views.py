from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from goods.models import *
from utils.user_util import LoginRequiredMixin
from django.contrib.auth import authenticate, login,logout
from django.views.generic import View


class CartAddView(View):
    print('CartAddView')
    '''购物车记录添加'''
    def post(self,request):
        '''购物车记录添加'''
        user=request.user
        if not user.is_authenticated():
            return JsonResponse({'res':0,'errmsg':'请先登录'})

        #接收数据
        sku_id=request.POST.get('sku_id')
        count = request.POST.get('count')


        #数据验证
        if not all([sku_id,count]):
            return JsonResponse({'res':1,'errmsg':'数据不完整'})

        #验证添加的商品数量
        try:
            count=int(count)
        except Exception as e:
            return JsonResponse({'res':2,'errmsg':'商品数目出错'})

        #验证商品是否存在
        try:
            sku=GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res':3,'errmsg':'商品不存在'})

        #业务处理：添加购物车记录
        conn=settings.REDIS_CONN
        cart_key='cart_%d'%user.id
        #先尝试获取sku_id的值 ->  hget cart_key 属性
        #如果sku_id在hash中不存在，hget返回None
        cart_count=conn.hget(cart_key,sku_id)
        if cart_count:
            #来家购物车中商品的数目
            count+=int(cart_count)

        #验证库存
        if count>sku.stock:
            return JsonResponse({'res':4,'errmsg':'库存不足'})

        #设置hash中sku_id对应的值
        #hset-> 如果sku_id已经存在，更新数据,如果sku_id不存在,添加数据
        conn.hset(cart_key,sku_id,count)

        #计算用户购物车商品的数目条
        total_count=get_cart_count(user)
        print(total_count)

        #反应应答
        return JsonResponse({'res':5,'total_count':total_count,'message':'添加成功'})

class CartCountView(View):
    '''异步获取购物车商品总数量'''
    def get(self,request):
        total_count=get_cart_count(request.user)
        return JsonResponse({'total_count':total_count})

class CartInfoView(View):
    '''购物车页面显示'''
    def get(self,request):
        '''显示'''
        #获取登录用户
        user=request.user
        #获取用户购物车中商品的信息
        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id
        #{'商品id':商品数量,...}
        cart_dict = conn.hgetall(cart_key)

        skus=[]
        #保存用户购物车中商品的总数目和总价格
        total_count=0
        total_price=0
        #遍历获取商品的信息
        for sku_id,count in cart_dict.items():
            #根据商品的id获取商品的信息
            sku=GoodsSKU.objects.get(id=sku_id)
            #计算商品的小计
            amount=sku.price*int(count)
            #动态给sku对象增加一个属性amount,保存商品的小计
            sku.amount=amount
            #动态给sku对象增加一个属性count,保存购物车中对应的商品数量
            sku.count=count
            #添加
            skus.append(sku)

            #累计计算商品的总数目和总价格
            total_count+=int(count)
            total_price+=amount

        #组织上下文
        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus,
        }
        #使用模板
        return render(request,'cart.html',context)

class CartUpdateView(View):
    '''购物车记录更新'''
    def post(self,request):
        #获取登录用户
        user=request.user
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据验证
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        # 验证添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})

        # 验证商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理：更新购物车记录
        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id

        # 验证库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '库存不足'})

        # 设置hash中sku_id对应的值
        # hset-> 如果sku_id已经存在，更新数据,如果sku_id不存在,添加数据
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车商品的总件数
        total_count = get_cart_count(user)

        # 反应应答
        return JsonResponse({'res': 5, 'total_count': total_count, 'message': '更新成功'})


class CartDeleteView(View):
    '''购物车记录删除'''
    def post(self, request):
        # 获取登录用户
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')

        # 数据验证
        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的商品id'})

        # 验证商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品不存在'})

        # 业务处理：删除购物车记录
        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id

        #删除 hdel
        conn.hdel(cart_key, sku_id)

        # 计算用户购物车商品的总件数
        total_count = get_cart_count(user)

        # 反应应答
        return JsonResponse({'res': 3, 'total_count': total_count, 'message': '删除成功'})


def get_cart_count(user):
    '''获取用户购物车购买的商品的数目'''

    #保存用户购物车中商品的总数目
    total_count=0

    if user.is_authenticated():
        #链接redis
        conn = settings.REDIS_CONN
        #key
        cart_key = 'cart_%d' % user.id
        #获取信息
        cart_dict=conn.hgetall(cart_key)

        #便利获取商品的信息
        for sku_id,count in cart_dict.items():
            total_count+=int(count)

    return total_count