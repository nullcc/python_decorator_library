# -*- coding: utf-8 -*-

def simple_decorator(decorator):
    """
    这个装饰器可以用来把简单的装饰器转换成一个规范的装饰器。
    如果一个装饰器需要一个函数作为参数然后返回一个函数（不是描述符），
    且它不会修改函数的属性或文档字符串，那么就可以使用这个装饰器来进行规范化。
    只需要为你的装饰器加上@simple_decorator，它会自动保存被装饰函数的文档字符串和函数属性。

    :param decorator: 需要被装饰的装饰器
    :return:          新的装饰器
    """

    def new_decorator(f):
        """
        :param f: 需要被装饰的函数
        :return:  被装饰器装饰过的函数
        """

        g = decorator(f)  # 调用需要被装饰的装饰器装饰函数f
        g.__name__ = f.__name__  # 把这个装饰完毕的函数的__name__改为和原函数f的__name__
        g.__doc__ = f.__doc__  # 把这个装饰完毕的函数的__doc__改为和原函数f的__doc__
        g.__dict__.update(f.__dict__)  # 使用原函数f的__dict__更新这个装饰完毕的函数的__dict__
        return g  # 返回这个装饰完毕的函数

    # 在这里需要把这个新装饰器的一些属性更改为原函数的属性(通过上面返回的那个新装饰器)
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)

    return new_decorator

#
# 示例
#

# 先来看看不用@simple_decorator的情况：

def my_simple_logging_decorator(func):
    def you_will_never_see_this_name(*args, **kwargs):
        print 'calling {}'.format(func.__name__)
        return func(*args, **kwargs)
    return you_will_never_see_this_name

@my_simple_logging_decorator
def double(x):
    'Doubles a number.'
    return 2 * x

assert double.__name__ == 'double'            # AssertionError
assert double.__doc__ == 'Doubles a number.'  # AssertionError

print(double.__name__)  # you_will_never_see_this_name
print(double.__doc__)   # None
print double(155)       # 310

# 使用@simple_decorator的情况：

@simple_decorator
def my_simple_logging_decorator(func):
    def you_will_never_see_this_name(*args, **kwargs):
        print 'calling {}'.format(func.__name__)
        return func(*args, **kwargs)
    return you_will_never_see_this_name

@my_simple_logging_decorator
def double(x):
    'Doubles a number.'
    return 2 * x

assert double.__name__ == 'double'
assert double.__doc__ == 'Doubles a number.'

print(double.__name__)  # double
print(double.__doc__)   # Doubles a number.
print double(155)       # 310

#
# 解析
#

# 不使用@simple_decorator的时候，打印double.__name__和double.__doc__都会输出被装饰器
# @my_simple_logging_decorator装饰后返回的you_will_never_see_this_name函数的相应属性。
# 其实我们期望的是能够返回最终被装饰的那个函数double的相应属性。然后我们使用装饰器@simple_decorator
# 装饰了my_simple_logging_decorator这个装饰器，实际上@simple_decorator就是把最终被装饰的函数
# double的一些函数属性和文档字符串搬移到了最终返回的装饰器上面。

# 理解@simple_decorator的的关键是要明白它是如何把最终返回的装饰器的一些属性改成被装饰函数的相应属性的。
