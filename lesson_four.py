def function_father(x) -> callable:
    
    def inside_function(repeat: int):
        print(x * repeat)

    return inside_function

from time import time


def time_measure(func):

     def wrapper(*args, **kwargs):
          before_execute = time()
          result = func(*args, **kwargs)
          after_exectute = time()
          print(f'{func.__name__} was called for {after_exectute - before_execute}')
          return result
     return wrapper
        
first = function_father("hello")
second = function_father("world")

# first(1)
# second(2)
# first(3)

def double(func):
    def wrapper(a, b):
        return func(a, b) * 2
    
    return wrapper

@time_measure # sum = double(sum)
def sum(a,b):
    return a + b

@time_measure
def mut(a,b):
    return a * b

@time_measure
def sub(a,b):
    return a - b

from time import time, sleep

def time_measure(func: callable):
    
    def wrapper(*args, **kwargs):
        before_execute = time()
        result = func(*args, **kwargs)
        after_exectute = time()
        print(f'{func.__name__} was called for {after_exectute - before_execute}')
        return result
    return wrapper
