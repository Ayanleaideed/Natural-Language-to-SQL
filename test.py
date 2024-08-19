
"""
Today I will try to implement a python caching system without using and importing any external libraries or classes. 
will create a all the methods and functions that i need 


"""

# main object 
class UserDatabase:
  def __init__(self) -> None:
    self.cache = {}
  
  def set(self, key, value):
    self.cache[key] = value

def get(self, key):
    return self.cache[key]
  
def __str__(self):
    return str(self.cache)
  
  
fake_users = [
  {'id': 1, 'name': 'John', 'age': 30, 'gender': 'male'},
  {'id': 2, 'name': 'Jane', 'age': 25, 'gender': 'female'},
  {'id': 3, 'name': 'Bob', 'age': 35, 'gender': 'male'},
  {'id': 4, 'name': 'Alice', 'age': 40, 'gender': 'female'},
  {'id': 5, 'name': 'Dave', 'age': 45, 'gender': 'male'},
  {'id': 6, 'name': 'Eve', 'age': 50, 'gender': 'female'}, 
  {'id': 7, 'name': 'Frank', 'age': 55, 'gender': 'male'},
  {'id': 8, 'name': 'George', 'age': 60, 'gender': 'female'},
  {'id': 9, 'name': 'Hannah', 'age': 65, 'gender': 'female'},
  {'id': 10, 'name': 'Isabella', 'age': 70, 'gender': 'female'},
]

# add fake users to the database
def add_user(self, user):
  self.set({user['id']: user['id'], user['name']: user['name'], user['age']: user['age'], user['gender']: user['gender']})

# get user by id
def get_user_by_id(self, id):
  return self.cache[id]

# get user by name
def get_user_by_name(self, name):
  return self.cache[name]

# get user by age
def get_user_by_age(self, age):
  return self.cache[age]

# get user by gender
def get_user_by_gender(self, gender):
  return self.cache[gender]


print(get_user_by_gender)