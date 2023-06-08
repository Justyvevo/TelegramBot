from math import pi
from abc import ABC, abstractmethod
class Shape(ABC):

     @abstractmethod
     def area(self) -> float:
          return 0
     

class Rectangle(Shape):
     def __init__(self, width: float, length: int) -> None:
          self._width = width
          self._length = length
          
     def get_width(self) -> float:
          return self._width
     
     def get_length(self) -> int:
          return self._length
     def perimeter(self) -> float:
          return (self._length * 2) + (self._width * 2)
     def area(self) -> float:
          return self._length * self._width


class Scquare(Rectangle):
     def perimeter(self) -> float:
          return self._length * 4
     def area(self) -> float:
          return self._length * self._width
     

class Circle(Shape):
     def __init__(self, radius) -> None:
          super().__init__()
          self._radius = radius
     def area(self) -> float:
          return self._radius ** 2 * pi
     

a = Rectangle(1,2)
print(a.area())
print(a.perimeter())
b = Scquare(3)
print(b.square())
print(b.perimeter())


