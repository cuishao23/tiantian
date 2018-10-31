from django.shortcuts import render,redirect
from django.views.generic import View
from goods.models import *
from django.core.cache import cache
from django.contrib.auth import authenticate, login,logout
from redis import StrictRedis
from django.core.paginator import Paginator
from cart.views import get_cart_count

# class IndexView(View):
#     def get(self,request):
#         # 获取商品的种类信息
#         goodstype_list = GoodsType.objects.all()
#         # 准备数据字典
#         context = {'goodstype_list':goodstype_list}
#         #返回首页
#         return render(request,'test_index.html',context)


class IndexView(View):
    def get(self,request):
        '''显示首页'''
        context = cache.get('cache_index')
        if context == None:
            print('设置换缓存')
            # 获取商品的种类信息
            types = GoodsType.objects.all()
            # 获取首页轮播商品信息
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')
            # 获取首页促销活动信息
            promotion_banners = IndePromotionBanner.objects.all().order_by('index')

            # 获取首页分类商品展示信息
            for type in types:  # GoodsType
                # 获取type种类首页分类的商品的图片展示信息
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                # 获取type种类首页分类的商品的文字展示信息
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

                # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
                type.image_banners = image_banners
                type.title_banners = title_banners

            # 组织模板上下文
            context = {
                'types': types,
                'goods_banners': goods_banners,
                'promotion_banners': promotion_banners,

            }

            cache.set('cache_index', context, 3600)
        # 获取用户购物车中商品的数目，暂时设置为0，待完善
        cart_count = get_cart_count(request.user)
        context.update(cart_count=cart_count)

        # 使用模板
        return render(request, 'index.html', context)




class DetailView(View):
    '''详情页'''
    def get(self,request,goods_id):
        '''显示商品详细页面'''
        try:
           sku=GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            #商品不存在
            return redirect(reverse('goods:index'))

        #获取商品的分类信息
        types = GoodsType.objects.all()
        #获取商品评论后，后期扩展
        #获取新品信息
        new_skus=GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        #获取同一个SPU的其他规格商品，后期扩展
        same_spu_skus=GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        #如果用户已经登录
        user=request.user
        if user.is_authenticated():
            #添加用户的历史记录

            #链接redis
            conn=StrictRedis('192.168.12.189')
            #key
            history_key='history_%d' % user.id
            #移除列表中的goods_id
            conn.lrem(history_key,0,goods_id)
            #把goods_id插入到列表的左侧
            conn.lpush(history_key,goods_id)
            #只保存用户浏览的5条信息
            conn.ltrim(history_key,0,4)

        #获取用户购物车商品的数目
        cart_count = get_cart_count(request.user)
        #组织模板上下文
        context = {
            'sku': sku,
            'types': types,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'same_spu_skus': same_spu_skus,
        }
        # 使用模板
        return render(request, 'detail.html', context)


#种类id 页码 排序方式
#restful api --> 请求一种资源
#/list?type_id种类id&page=页码&sort=排序方式
#/list/种类id/页码/排序方式
#/list/种类id/页码？sort=排序方式
class ListView(View):
    '''列表页'''
    def get(self,request,type_id,page):
        '''显示列表页'''
        #获取种类信息
        try:
            type=GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            #种类不存在
            return redirect(reverse('goods:index'))

        #获取商品的分类信息
        types=GoodsType.objects.all()
        #读取排序方式，获取分类商品的信息
        #sort=default 按照默认id排序
        #sort=price 按照商品价格排序
        #sort=hot 按照商品销量排序
        sort=request.GET.get('sort')

        if sort=='price':
            skus=GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort=='hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort='default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        #对数据进行分页
        paginator=Paginator(skus,2)
        #获取page页的内容
        try:
            page=int(page)
        except Exception as e:
            page=1

        if page>paginator.num_pages:
            page=1

        #获取page页的Page实例对象
        skus_page=paginator.page(page)

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
        #获取新的信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 获取用户购物车商品的数目
        cart_count = get_cart_count(request.user)
        # 组织模板上下文
        context = {
            'type': type,
            'types': types,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'pages': pages,
            'sort':sort,
        }
        # 使用模板
        return render(request, 'list.html', context)








