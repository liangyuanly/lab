import random

def F(max):
    print [3]*3
    print[[3]]*3

    a = 0; b = 1
    yield a
    while b < max:
        yield b
        a, b = b, a + b

for i in F(100):
    print i
