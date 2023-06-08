import os

if not os.path.exists("cats"):
    os.makedirs("cats")


with open('cats/example.txt', "w") as file:
    file.write("Cats")