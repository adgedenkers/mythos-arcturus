def print_aligned(numbers):
    formatted = [f"{n:,}".replace(",", " ") for n in numbers]
    width = max(len(s) for s in formatted)
    for s in formatted:
        print(s.rjust(width))

def fibonacci(n=100):
    numbers = []
    a, b = 0, 1
    for _ in range(n):
        numbers.append(a)
        a, b = b, a + b
    print_aligned(numbers)

def powers_of_2(n=100):
    numbers = [2 ** i for i in range(n)]
    print_aligned(numbers)


# --- Run ---
print("=== Fibonacci ===")
fibonacci(100)

print("\n=== Powers of 2 ===")
powers_of_2(100)