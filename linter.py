def factorial_digit_sum(n):
    factorial = [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]
    return sum(factorial[int(digit)] for digit in str(n))

def dictionary_based_approach(n, L):
    seen = {}
    step = 0
    current = n

    while step < L:
        if current in seen:
            cycle_start = seen[current]
            cycle_length = step - cycle_start
            remaining_steps = (L - step) % cycle_length
            for _ in range(remaining_steps):
                current = factorial_digit_sum(current)
            return current
        seen[current] = step
        current = factorial_digit_sum(current)
        step += 1

    return current

# Example usage:
import sys

if __name__ == "__main__":
    n, L = map(int, sys.stdin.read().strip().split())
    result = dictionary_based_approach(145, 1)
    print(result)