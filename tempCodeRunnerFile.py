class Person:
    def __init__(self,fname,lname):
        self.firstname = fname
        self.lastname = lname
y = Person("Gokul","Krishnan")
y.print(self.fname)


class Student:
    def __init__(self,stdid,age):
        super().__init__(fname, lname)
        self.rollno = stdid
        self.age = age

    def printdata(self):
        print(f"Welcome{self.firstname}")
        print("Your Roll Number is :",self.rollno)
        print(f"you are {self.age} years old")


x = Student(64,22)
x.printdata()
