from typing import Iterable
class Ingredients:
     country = "Russia"

     def __init__(self, weight: float, callorage: int) -> None:
          self._weight = weight
          self._callorage = callorage
     
     def get_weight(self) -> float:
          return self._weight
     
     def get_callorage(self) -> int:
          return self._callorage
     def prepare(self):
          pass


class Bread(Ingredients):
     def prepare(self):
          print("Bread serverd")
          pass


class Tomato(Ingredients):
     def prepare(self):
          print("Tomato fried")
          self._weight *= 0.8
          self._callorage *= 1.1


class Potato(Ingredients):
     def prepare(self):
          print("Potato fried")
          self._weight += 10
          self._callorage 


class Berries(Ingredients):
     def __init__(self, count: int, weight: float, callorage: int) -> None:
          super().__init__(weight, callorage)
          self._count = count
     

potato, tomato, bread = Potato(0.3, 500), Tomato(0.4, 200), Bread(0.1, 10)


def make_dinner(ingredients: Iterable[Ingredients]):
     callorage = 0
     for ingredient in ingredients:
          ingredient.prepare()
          callorage += ingredient.get_callorage()
     print(f"Dinner was made, total {callorage}")


make_dinner((potato, tomato, bread))
