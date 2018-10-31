from django.db import models
from db.base_model import BaseModel

class OrderInfo(BaseModel):
    '''订单表'''
    PAY_METHON_CHOICES = (
        (1,'货到付款'),
        (2,'微信支付'),
        (3,'支付宝'),
        (4,'银联支付'),
    )
    #获取方式：(小知识)
    #前段:xxx..get_order_status_display
    #后端:xxx..get_order_status_display()
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已收货'),
    )


    order_id= models.CharField(max_length = 128,primary_key=True,verbose_name='订单id') #primary_key=True  不会自动产生id
    user =models.ForeignKey('user.User',verbose_name='用户')
    addr = models.ForeignKey('user.Address', verbose_name='地址')
    pay_method =models.SmallIntegerField(choices=PAY_METHON_CHOICES,default=3,verbose_name='支付方式')

    # 为了方便使用，允许部分冗余
    total_count = models.IntegerField(default=1,verbose_name='商品数量')
    total_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品总价')

    transit_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='订单运费')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES,default=1,verbose_name='订单状态')
    trade_no =models.CharField(max_length=128,default='',verbose_name='支付编号')

    class Meta:
        db_table = 'df_order_info'
        verbose_name='订单'
        verbose_name_plural=verbose_name

class OrderGoods(BaseModel):
    # 订单详情 商品模型类
    order = models.ForeignKey('OrderInfo',verbose_name='订单')
    sku = models.ForeignKey('goods.GoodsSKU',verbose_name='商品sku')
    count = models.IntegerField(default=1,verbose_name='商品数目')
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品价格')

    class Meta:
        db_table = 'df_order_goods'
        verbose_name='订单商品'
        verbose_name_plural = verbose_name
