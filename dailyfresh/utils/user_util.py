import hashlib
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


#md5密码加密
def my_md5(value):
    m=hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()

