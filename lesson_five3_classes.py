class Student:
     COUNT = 0
     
     def __init__(self, name: str, age: str = "") -> None:
          self.name = name
          self.age = age

     def description(self):
          return f'{self.age}{self.name}'
     
bio = Student(name="Artemii", age="17")

print(Student.bio())




class HomelessStudent(Student):
     def __init__(self, name):
        self.name = name
     def SayH(self):
        print('я все-еще' % self.name)
student_j = HomelessStudent("бездомный")
student_j.SayH()