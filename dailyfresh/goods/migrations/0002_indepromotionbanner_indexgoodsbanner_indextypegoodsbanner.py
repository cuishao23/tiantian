# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndePromotionBanner',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('name', models.CharField(max_length=20, verbose_name='活动名称')),
                ('url', models.CharField(max_length=256, verbose_name='活动链接')),
                ('image', models.ImageField(upload_to='banner', verbose_name='活动图片')),
                ('index', models.SmallIntegerField(default=0, verbose_name='展示顺序')),
            ],
            options={
                'verbose_name_plural': '页促销活动',
                'verbose_name': '页促销活动',
                'db_table': 'df_index_promotion',
            },
        ),
        migrations.CreateModel(
            name='IndexGoodsBanner',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('image', models.ImageField(upload_to='banner', verbose_name='图片')),
                ('index', models.SmallIntegerField(default=0, verbose_name='展示顺序')),
                ('sku', models.ForeignKey(to='goods.GoodsSKU', verbose_name='商品')),
            ],
            options={
                'verbose_name_plural': '首页轮播商品',
                'verbose_name': '首页轮播商品',
                'db_table': 'df_index_banner',
            },
        ),
        migrations.CreateModel(
            name='IndexTypeGoodsBanner',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('display_type', models.SmallIntegerField(default=1, choices=[(0, '标题'), (1, '图片')], verbose_name='展示形式')),
                ('index', models.SmallIntegerField(default=0, verbose_name='展示顺序')),
                ('sku', models.ForeignKey(to='goods.GoodsSKU', verbose_name='商品SKU')),
                ('type', models.ForeignKey(to='goods.GoodsType', verbose_name='商品类型')),
            ],
            options={
                'verbose_name_plural': '主页分类展示商品',
                'verbose_name': '主页分类展示商品',
                'db_table': 'df_index_type_goods',
            },
        ),
    ]
