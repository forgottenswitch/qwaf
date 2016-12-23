def hex_digit(x):
    u = 0
    if x < 0:
        raise Exception("digit cannot be below zero ({})".format(x))
    elif x < 10:
        u = ord("0") + int(x)
    elif x < 16:
        u = ord("a") + int(x - 10)
    return chr(u)

def int_to_base(n, base):
    divisor = 1
    while divisor <= n:
        divisor *= base

    digits = []
    while n >= base:
        divisor /= base
        d, n = divmod(n, divisor)
        digits.append(hex_digit(int(d)))
    digits.append(hex_digit(int(n)))

    return "".join(digits)
