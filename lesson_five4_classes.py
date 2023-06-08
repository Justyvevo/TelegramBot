class Student:
     count = 0

     def __init__(self, name, age):
          self._name = name 
          self._age = age
          self.plus_one()
     
     @classmethod
     def plus_one(cls):
          Student.count +=1

     def bio(self):
          print(f"{self._name}, {self._age}")


def test_students():
     ruslan = Student("Ruslan", 18)
     ruslan.bio()
     Student("Ilias", 19)
     print(Student.count)
test_students()