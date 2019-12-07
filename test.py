a = 10 ** 5
print(type(a))


import time
a = time.time()
for i in range(10000):
    print(1)
b = time.time()

print(b - a)