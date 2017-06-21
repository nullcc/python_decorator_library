# -*- coding: utf-8 -*-

import collections
import functools

# 1. 使用class实现函数结果缓存

class memoized(object):
   """
   缓存调用函数的结果，当第一次用某个参数调用函数时，函数会计算并返回结果，同时缓存这个参数的计算结果。
   在下次用同样参数调用函数时，不会再次计算，而是将直接返回上一次的缓存结果。
   """
   def __init__(self, func):
      self.func = func
      self.cache = {}  # 计算缓存
   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # 当参数不是一个可哈希对象时，比如一个列表，将执行计算
         return self.func(*args)
      if args in self.cache:
         # 如果参数在缓存中，直接返回缓存结果
         return self.cache[args]
      else:
         # 如果参数不再缓存中，先计算结果，再缓存结果，之后返回结果
         value = self.func(*args)
         self.cache[args] = value
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)

@memoized
def fibonacci(n):
   "Return the nth fibonacci number."
   if n in (0, 1):
      return n
   return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(12))  # 第一用12调用fibonacci函数会真正进行计算
print(fibonacci(12))  # 第一用12调用fibonacci函数不会进行真正的计算，而是返回缓存结果

# 2. 使用嵌套函数实现函数结果缓存

def memoize(obj):  # 注意这个装饰器忽略了**kwargs
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:  # 只判断了args是否在缓存中，忽略了**kwargs
            cache[args] = obj(*args, **kwargs)  # 调用被装饰的函数计算结果
        return cache[args]
    return memoizer

@memoize
def fibonacci(n):
   "Return the nth fibonacci number."
   if n in (0, 1):
      return n
   return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(12))  # 第一用12调用fibonacci函数会真正进行计算
print(fibonacci(12))  # 第一用12调用fibonacci函数不会进行真正的计算，而是返回缓存结果

# 考虑**kwargs的版本

def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)  # 把str(args) + str(kwargs)作为key进行缓存
        if key not in cache:
            cache[key] = obj(*args, **kwargs)  # 调用被装饰的函数计算结果
        return cache[key]
    return memoizer

@memoize
def fibonacci(n):
   "Return the nth fibonacci number."
   if n in (0, 1):
      return n
   return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(12))  # 第一用12调用fibonacci函数会真正进行计算
print(fibonacci(12))  # 第一用12调用fibonacci函数不会进行真正的计算，而是返回缓存结果

# 3. 用dict实现一个memoize子类实现函数结果缓存

class memoize(dict):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.func(*key)
        return result
@memoize
def foo(a, b):
    return a * b

print(foo(2, 4))  # 8
print(foo(2, 4))  # 8
print(foo)        # {(2, 4): 8}

# 4. 把函数调用结果缓存成文件

import pickle
import collections
import functools
import inspect
import os.path
import re
import unicodedata

class Memorize(object):
    """
    缓存调用函数的结果，当第一次用某个参数调用函数时，函数会计算并返回结果，同时缓存这个参数的计算结果。
    在下次用同样参数调用函数时，不会再次计算，而是将直接返回上一次的缓存结果。
    缓存会在当前目录下被保存成.cache文件以重用。如果一个python文件中使用了这个装饰器并在上次运行之后
    被更新过，那么当前缓存文件会被删除，然后建立一个新的缓存文件（如果函数行为发生了变化）。

    """
    def __init__(self, func):
        self.func = func
        self.set_parent_file() # Sets self.parent_filepath and self.parent_filename
        self.__name__ = self.func.__name__
        self.set_cache_filename()
        if self.cache_exists():
            self.read_cache() # Sets self.timestamp and self.cache
            if not self.is_safe_cache():
                self.cache = {}
        else:
            self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            self.save_cache()
            return value

    def set_parent_file(self):
        """
        Sets self.parent_file to the absolute path of the
        file containing the memoized function.
        """
        rel_parent_file = inspect.stack()[-1].filename
        self.parent_filepath = os.path.abspath(rel_parent_file)
        self.parent_filename = _filename_from_path(rel_parent_file)

    def set_cache_filename(self):
        """
        Sets self.cache_filename to an os-compliant
        version of "file_function.cache"
        """
        filename = _slugify(self.parent_filename.replace('.py', ''))
        funcname = _slugify(self.__name__)
        self.cache_filename = filename+'_'+funcname+'.cache'

    def get_last_update(self):
        """
        Returns the time that the parent file was last
        updated.
        """
        last_update = os.path.getmtime(self.parent_filepath)
        return last_update

    def is_safe_cache(self):
        """
        Returns True if the file containing the memoized
        function has not been updated since the cache was
        last saved.
        """
        if self.get_last_update() > self.timestamp:
            return False
        return True

    def read_cache(self):
        """
        Read a pickled dictionary into self.timestamp and
        self.cache. See self.save_cache.
        """
        with open(self.cache_filename, 'rb') as f:
            data = pickle.loads(f.read())
            self.timestamp = data['timestamp']
            self.cache = data['cache']

    def save_cache(self):
        """
        Pickle the file's timestamp and the function's cache
        in a dictionary object.
        """
        with open(self.cache_filename, 'wb+') as f:
            out = dict()
            out['timestamp'] = self.get_last_update()
            out['cache'] = self.cache
            f.write(pickle.dumps(out))

    def cache_exists(self):
        '''
        Returns True if a matching cache exists in the current directory.
        '''
        if os.path.isfile(self.cache_filename):
            return True
        return False

    def __repr__(self):
        """ Return the function's docstring. """
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """ Support instance methods. """
        return functools.partial(self.__call__, obj)

def _slugify(value):
    """
    Normalizes string, converts to lowercase, removes
    non-alpha characters, and converts spaces to
    hyphens. From
    http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = re.sub(r'[^\w\s-]', '', value.decode('utf-8', 'ignore'))
    value = value.strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value

def _filename_from_path(filepath):
    return filepath.split('/')[-1]
