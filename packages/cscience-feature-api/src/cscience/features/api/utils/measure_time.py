import timeit


def measure_time(times: int=1, ignore_first: bool=False):
    def inner(func):
        def wrapper(*args, **kwargs):

            t_total = 0
            result = None
            if ignore_first:
                result = func(*args, **kwargs)

            n = max(1, times)
            for i in range(n):
                start = timeit.default_timer()
                result = func(*args, **kwargs)
                end = timeit.default_timer()
                t_total += end - start

            max_width = 39

            print(
                f"\t{func.__name__:<{max_width}} "
                f"[mean] ⌛ {t_total / n:.5f} s for 🧮 {n} iterations"
            )
            return result
        return wrapper
    return inner