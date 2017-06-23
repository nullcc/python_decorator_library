# -*- coding: utf-8 -*-

#
# © 2011 Christopher Arndt, MIT License
#

import time

class cached_property(object):
    """
    在一个TTL中对只读属性只求值一次

    可以使用如下方式来创建一个缓存的属性：

    import random

    # the class containing the property must be a new-style class
    class MyClass(object):
        # create property whose value is cached for ten minutes
        @cached_property(ttl=600)
        def randint(self):
            # will only be evaluated every 10 min. at maximum.
            return random.randint(0, 100)

    属性的值会被缓存在类的实例对象的'_cache'属性中。'_cache'属性是一个字典，里面存放了所有被这个装饰器装饰的方法。
    缓存中的每一个值只在属性被第一次访问的时候创建，这个值是一个包含两个元素的元组，一个是最后一次被计算出的属性值，一个
    是最后一次更新的时间（秒）。

    默认的TTL是300秒（5分钟）。如果想要让缓存永远不过期，可以把TTL设置为0。

    下面的代码可以手动让一个属性的缓存过期：

        del instance._cache[<property name>]

    """

    def __init__(self, ttl=300):
        self.ttl = ttl

    def __call__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        now = time.time()
        try:
            value, last_update = inst._cache[self.__name__]
            if self.ttl > 0 and now - last_update > self.ttl:
                raise AttributeError
        except (KeyError, AttributeError):
            value = self.fget(inst)
            try:
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.__name__] = (value, now)
        return value

#
# 示例
#

import random

class MyClass(object):

    @cached_property(ttl=600)
    def randint(self):
        return random.randint(0, 100)

i = MyClass()

print(i.randint)
print(i.randint)

# 在一个TTL内，上面两次访问i.randint的值是相同的
