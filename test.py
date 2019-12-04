a = 10 ** 5
print(type(a))

filename = "a.jpg"
file = open(filename, 'rb')
data = file.read(5)
data = bytearray(data)
for i in range(5):
    print(data[i] - 48)
data = file.read(5)
data = bytearray(data)
for i in range(5):
    print(data[i] - 48)
print(data)