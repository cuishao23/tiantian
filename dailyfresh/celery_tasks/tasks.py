from celery import Celery
from django.core.mail import send_mail
from django.template import RequestContext, loader
from django.conf import settings




'''给celery看  运行django里面的信息用'''
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

from goods.models import GoodsType,IndexGoodsBanner,IndePromotionBanner,IndexTypeGoodsBanner

app = Celery('celery_tasks.tasks', broker='redis://192.168.12.189:6379/3')


#启动命令
#celery -A celery_tasks.tasks worker -l info

@app.task
def task_send_mail(subject, message, sender, receiver, html_message):
    print('发邮件begin....')
    import time
    time.sleep(10)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    print('发邮件end....')

@app.task
def task_generate_static_index():
    '''产生静态页面'''
    print('产生静态首页begin...')

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
    # 获取用户购物车中商品的数目，暂时设置为0，待完善
    cart_count = 0

    # 组织模板上下文
    context = {
        'types': types,
        'goods_banners': goods_banners,
        'promotion_banners': promotion_banners,
        'cart_count': cart_count,
    }
    # 使用模板
    #1.加载模板文件，返回模板对象
    temp=loader.get_template('static_index.html')
    #2.模板渲染
    static_index_html=temp.render(context)

    #生成首页对应的静态文件
    save_path=os.path.join(settings.BASE_DIR,'static/html/index.html')
    with open(save_path,'w') as f:
        f.write(static_index_html)

    print('产生静态首页end..')
