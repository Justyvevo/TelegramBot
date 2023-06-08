from random import choice

class Human:
     GENOM_COUNT = 46
     
     def __init__(self, name: str, status: str = "") -> None:
          self.name = name
          self.status = status

     def description(self,):
          return f'{self.status}{self.name}'
     

     @classmethod
     def change_genom_count(cls):
          cls.GENOM_COUNT += 1

     @staticmethod
     def create_new_name() -> str:
          return choice(("Doctor", "Balls", "Hurt"))

me = Human(name="Balls", status="hurt.")

print(me.create_new_name())




