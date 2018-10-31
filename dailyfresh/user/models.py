from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel

'''
继承AbstractUser：用他的属性
继承BaseModel：共有的属性
'''

class User(AbstractUser,BaseModel):
    '''用户模型类'''
    class Meta:
        db_table='de_user'
        verbose_name='用户'
        verbose_name_plural=verbose_name


class Address(BaseModel):
    '''地址模型类'''
    user=models.ForeignKey('User',verbose_name='所属账户')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    address = models.CharField(max_length=256, verbose_name='收件地址')
    postcode = models.CharField(max_length=6, null=True,verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default=models.BooleanField(default=False,verbose_name='是否默认')

    '''地址模型类'''
    class Meta:
        db_table='de_address'
        verbose_name='地址'
        verbose_name_plural=verbose_name

class Province(models.Model):
    pname=models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.pname

class City(models.Model):
    cname=models.CharField(max_length=100,unique=True)
    cprovince=models.ForeignKey(Province)
    def __str__(self):
        return self.cname

class Area(models.Model):
    aname=models.CharField(max_length=100,unique=True)
    acity = models.ForeignKey(City)
    def __str__(self):
        return self.aname