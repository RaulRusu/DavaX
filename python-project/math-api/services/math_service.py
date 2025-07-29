class MathService:
    def pow(self, base: float, exponent: float) -> float:
        return base ** exponent

    def nth_fibo_number(self, n: int) -> int:
        if n < 0:
            raise ValueError(f'negative n: {n}')

        f1, f2 = 0, 1
        for _ in range(n):
            f1, f2 = f2, f1 + f2

        return f1

    def factorial(self, number: int) -> int:
        if number < 0:
            raise ValueError(f'negative number: {number}')

        result = 1
        for i in range(1, number + 1):
            result *= i
        return result