# decorator to output job duration
import time


def job_timer(func):
    """Example usage:
        @job_timer
        def my_function():
            # your function logic here

    my_function()  # This will print the execution time to the console
    """

    def wrapper(*args, **kwargs):
        print(f"Running function {func.__name__}")
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Function {func.__name__} took {execution_time:.4f} seconds to run")
        return result

    return wrapper
