# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('goods', '0002_indepromotionbanner_indexgoodsbanner_indextypegoodsbanner'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('count', models.IntegerField(default=1, verbose_name='商品数目')),
                ('price', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')),
            ],
            options={
                'db_table': 'df_order_goods',
                'verbose_name_plural': '订单商品',
                'verbose_name': '订单商品',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('order_id', models.CharField(primary_key=True, serialize=False, max_length=128, verbose_name='订单id')),
                ('pay_method', models.SmallIntegerField(choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')], default=3, verbose_name='支付方式')),
                ('total_count', models.IntegerField(default=1, verbose_name='商品数量')),
                ('total_price', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')),
                ('transit_price', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单运费')),
                ('order_status', models.SmallIntegerField(choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已收货')], default=1, verbose_name='订单状态')),
                ('trade_no', models.CharField(default='', max_length=128, verbose_name='支付编号')),
                ('addr', models.ForeignKey(to='user.Address', verbose_name='地址')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'db_table': 'df_order_info',
                'verbose_name_plural': '订单',
                'verbose_name': '订单',
            },
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='order',
            field=models.ForeignKey(to='order.OrderInfo', verbose_name='订单'),
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='sku',
            field=models.ForeignKey(to='goods.GoodsSKU', verbose_name='商品sku'),
        ),
    ]
