# -*- coding: utf-8 -*-

import time
import math

def retry(tries, delay=3, backoff=2):
  """
  对一个函数或方法进行重试直到它返回True。
  delay为初始延迟秒数，backoff为每次延迟调用应该在上一次的基础上延迟多少秒的退避指数。
  backoff必须大于1否则就不是真正的退避。tries必须至少为0，delay必须大于0。
  """

  if backoff <= 1:
    raise ValueError("backoff must be greater than 1")

  tries = math.floor(tries)
  if tries < 0:
    raise ValueError("tries must be 0 or greater")

  if delay <= 0:
    raise ValueError("delay must be greater than 0")

  def deco_retry(f):
    def f_retry(*args, **kwargs):
      mtries, mdelay = tries, delay # make mutable

      rv = f(*args, **kwargs) # first attempt
      while mtries > 0:
        if rv is True: # Done on success
          return True

        mtries -= 1      # consume an attempt
        time.sleep(mdelay) # wait...
        mdelay *= backoff  # make future wait longer

        rv = f(*args, **kwargs) # Try again

      return False # Ran out of tries :-(

    return f_retry # true decorator -> decorated function
  return deco_retry  # @retry(arg[, ...]) -> true decorator
