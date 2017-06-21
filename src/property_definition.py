# -*- coding: utf-8 -*-

# 1. 分别定义get,set和del方法的装饰器

import sys

def propget(func):
    locals = sys._getframe(1).f_locals  # 获取调用该函数的上一层函数的本地名字空间
    name = func.__name__  # 调用的函数的名称(会作为实例属性使用)
    prop = locals.get(name)  # 在上层函数的本地名字空间中获取这个"属性"的值
    if not isinstance(prop, property):  # 判断这个"属性"是否是一个property
        prop = property(func, doc=func.__doc__)  # 构造一个名称和func的名称相同的"属性"，get方法为func
    else:
        doc = prop.__doc__ or func.__doc__  # 获取文档字符串
        prop = property(func, prop.fset, prop.fdel, doc)  # 构造一个名称和func的名称相同的"属性"
    return prop

def propset(func):
    locals = sys._getframe(1).f_locals
    name = func.__name__
    prop = locals.get(name)
    if not isinstance(prop, property):
        prop = property(None, func, doc=func.__doc__)   # 构造一个名称和func的名称相同的"属性"，set方法为func
    else:
        doc = prop.__doc__ or func.__doc__
        prop = property(prop.fget, func, prop.fdel, doc)
    return prop

def propdel(func):
    locals = sys._getframe(1).f_locals
    name = func.__name__
    prop = locals.get(name)
    if not isinstance(prop, property):
        prop = property(None, None, func, doc=func.__doc__)  # 构造一个名称和func的名称相同的"属性"，del方法为func
    else:
        prop = property(prop.fget, prop.fset, func, prop.__doc__)
    return prop

#
# 示例
#

class Example(object):

    @propget
    def myattr(self):
        return self._half * 2

    @propset
    def myattr(self, value):
        self._half = value / 2

    @propdel
    def myattr(self):
        del self._half

i = Example()
i._half = 100

print(i.myattr)  # 200
i.myattr = 400
print(i.myattr)  # 400
del i.myattr
print(i.myattr)  # AttributeError: 'Example' object has no attribute '_half'

# 这几个装饰器可以用设置类对象的"计算属性"，比如某些属性不是类对象固有的，而是需要通过计算得到，就可以对相应的实例方法设置
# @propget、@propset和@propdel装饰器，这些方法可以像属性那样被使用（用obj.someattr而不用obj.someattr()）

# 2. 使用@apply

class Example(object):
    @apply  # doesn't exist in Python 3
    def myattr():
        doc = '''This is the doc string.'''

        def fget(self):
            return self._half * 2

        def fset(self, value):
            self._half = value / 2

        def fdel(self):
            del self._half

        return property(**locals())
    #myattr = myattr()  # works in Python 2 and 3

#
# 示例
#

i = Example()
i._half = 100

print(i.myattr)  # 200
i.myattr = 400
print(i.myattr)  # 400
del i.myattr
print(i.myattr)  # AttributeError: 'Example' object has no attribute '_half'

# 3. 使用@property

import sys

try:
    # Python 2
    import __builtin__ as builtins
except ImportError:
    # Python 3
    import builtins

def property(function):
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probe_func(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k, locals.get(k)) for k in keys))
            sys.settrace(None)
        return probe_func
    sys.settrace(probe_func)
    function()
    return builtins.property(**func_locals)

#
# 示例
#

from math import radians, degrees, pi

class Angle(object):
    def __init__(self, rad):
        self._rad = rad

    @property
    def rad():
        '''The angle in radians'''
        def fget(self):
            return self._rad
        def fset(self, angle):
            if isinstance(angle, Angle):
                angle = angle.rad
            self._rad = float(angle)

    @property
    def deg():
        '''The angle in degrees'''
        def fget(self):
            return degrees(self._rad)
        def fset(self, angle):
            if isinstance(angle, Angle):
                angle = angle.deg
            self._rad = radians(angle)

angle = Angle(pi)
print(angle.rad)  # 3.14159265359
print(angle.deg)  # 180.0
