import gc
import math
import os
import random
from typing import List

import numpy as np
import pytest
import torch
from numba import njit

from purem import purem

purem.configure(license_key="purem-sandbox")

ARRAY_SIZE = int(os.environ.get("ARRAY_SIZE", 200_000))


def generate_numbers(size, start=0.0, end=1.0) -> List[float]:
    """
    Generates a list of random floating-point numbers within a specified range.

    This function creates a list of random numbers based on the size specified by
    the user. The numbers are uniformly distributed and fall within the range
    defined by the `start` and `end` parameters. If `start` and `end` are not provided,
    they default to 0.0 and 1.0, respectively.

    :param size: The number of random numbers to generate.
    :type size: int
    :param start: The lower bound of the range for the random numbers. Defaults to 0.0.
    :type start: float
    :param end: The upper bound of the range for the random numbers. Defaults to 1.0.
    :type end: float
    :return: A list of random floating-point numbers within the specified range.
    :rtype: list[float]
    """
    return [random.uniform(start, end) for _ in range(size)]


@pytest.fixture(autouse=True)
def clean_memory() -> None:
    """
    A pytest fixture to clean up memory before each test.

    This fixture is automatically used for every test function due to the
    `autouse=True` parameter. It ensures that garbage collection is triggered,
    helping maintain a clean state in memory between test executions.

    :return: None
    """
    gc.collect()


@pytest.fixture
def array_instance() -> np.ndarray:
    """
    Creates and returns a numpy array fixture for testing.

    This fixture generates a numpy array based on the provided
    `generate_numbers` function and the defined `ARRAY_SIZE`.
    The array elements are cast to the `float` data type.

    :yield: A numpy array of floating-point numbers for testing.
    :rtype: np.ndarray
    """
    return np.array(generate_numbers(ARRAY_SIZE), dtype=float)


def softmax_purem(arr: np.ndarray) -> np.ndarray:
    """
    Apply the softmax function to the input array.

    The softmax function computes the probabilities for each element
    in the input array by exponentiating them and normalizing the
    results so that they sum to 1. It is commonly used in machine
    learning classification problems.

    :param arr: Input array for which to compute the softmax.
                Should be a NumPy ndarray.
    :type arr: np.ndarray
    :return: The softmax-transformed array, where values represent
             probabilities and sum to 1 over the input dimensions.
    :rtype: np.ndarray
    """
    return purem.softmax(arr)


def softmax_numpy(arr: np.ndarray) -> np.ndarray:
    """
    Compute the softmax of a given array using numpy.

    This function calculates the softmax of the input array. It stabilizes
    the computation by subtracting the maximum value from the array to
    prevent numerical overflow in the exponential calculation.

    :param arr: Input array for which softmax needs to be calculated.
    :type arr: np.ndarray
    :return: The computed softmax values as an array.
    :rtype: np.ndarray
    """
    arr_max = np.max(arr)
    shifted = arr - arr_max
    arr_exp = np.exp(shifted)
    return arr_exp / np.sum(arr_exp)


# device = "mps" if torch.backends.mps.is_available() else "cpu"
device = "cpu"


def softmax_torch(arr: np.ndarray) -> torch.Tensor:
    """
    Applies the softmax function along the last dimension of the input array.

    This function takes a NumPy array or similar Python data structure as input,
    converts it to a PyTorch tensor, and computes the softmax values along the
    last dimension. The input is cast to a float32 tensor for compatibility with
    PyTorch computations. The result is returned as a PyTorch tensor.

    :param arr: Input array to be converted to a PyTorch tensor and processed
        using the softmax function. The array can be of any shape, with the
        softmax computation applied along its last dimension.
    :type arr: array-like
    :return: A PyTorch tensor containing the softmax values computed from the
        input array along its last dimension.
    :rtype: torch.Tensor
    """
    array_torch = torch.asarray(arr, dtype=torch.float32, device=device)
    arr_torch = array_torch.to(dtype=torch.float32)
    return arr_torch.softmax(dim=-1)


@njit(parallel=True, fastmath=True)
def softmax_numba(arr: np.ndarray) -> np.ndarray:
    """
    Computes the softmax function for a given array with NumPy and Numba for
    parallelized execution. The function calculates the exponential normalization
    of a NumPy array to transform input values into probabilities that sum to one.

    The function optimizes the computation using the maximum value of the input
    array to improve numerical stability, specifically by avoiding overflow
    and underflow during exponentiation.

    :param arr: Input array of floats
    :type arr: numpy.ndarray
    :return: Array of softmax probabilities corresponding to the input
    :rtype: numpy.ndarray
    """
    n = arr.shape[0]
    out = np.empty_like(arr)
    x_max = -np.inf
    for i in range(n):
        if arr[i] > x_max:
            x_max = arr[i]
    total = 0.0
    for i in range(n):
        out[i] = math.exp(arr[i] - x_max)
        total += out[i]
    for i in range(n):
        out[i] /= total
    return out


functions = {
    'Softmax: Purem': softmax_purem,
    'Softmax: NumPy': softmax_numpy,
    'Softmax: PyTorch': softmax_torch,
    'Softmax: Numba': softmax_numba,
}


@pytest.mark.parametrize("func_name", [pytest.param("Softmax: Purem")])
def test_purem_softmax(benchmark, func_name, array_instance):
    """
    Tests the performance of the `softmax_purem` function using the Benchmark fixture.

    :param benchmark: Benchmark fixture provided by pytest-benchmark for measuring
        the performance of the `softmax_purem` function.
    :param func_name: Name of the function being tested in the benchmarking process.
    :param array_instance: Input data instance provided to the `softmax_purem` function
        during the benchmarking test.
    :return: None
    """
    benchmark(softmax_purem, array_instance)


@pytest.mark.parametrize("func_name", [pytest.param("Softmax: NumPy")])
def test_numpy_softmax(benchmark, func_name, array_instance):
    """
    Benchmark test for the numpy implementation of the softmax function. This test
    uses pytest parametrize to evaluate the performance of the function across
    different sizes of input and under a specific function name label. It clears
    garbage, generates random floating-point numbers of the specified size, and
    then benchmarks the softmax function.

    :param benchmark: The pytest-benchmark fixture used for executing the
        performance test of the softmax function.
    :param func_name: Determines the function name label for benchmarking.
    :param size: The size of the input data array to be generated and used in
        the softmax function.
    :return: None
    """
    benchmark(softmax_numpy, array_instance)


@pytest.mark.parametrize("func_name", [pytest.param("Softmax: PyTorch")])
def test_torch_softmax(benchmark, func_name, array_instance):
    """
    Tests the performance of the PyTorch implementation of the softmax function over
    an array of a specified size using the pytest benchmarking framework.

    This test generates a random array of numbers of the given size, applies the
    softmax operation implemented in PyTorch, and records its performance metrics
    using the pytest-benchmark plugin.

    :param benchmark: A pytest-benchmark function used to measure the performance
        of the specified function under test.
    :param func_name: The name of the function being tested.
    :param size: The size of the input array for which softmax computation is executed.
    :rtype: None
    :return: Returns None as this function is a test case invoked by pytest.
    """
    benchmark(softmax_torch, array_instance)


@pytest.mark.parametrize("func_name", [pytest.param("Softmax: Numba")])
def test_numba_softmax(benchmark, func_name, array_instance):
    """
    Tests the performance of the Numba-accelerated softmax function using pytest.

    This test leverages the pytest benchmarking tool to measure the time taken
    to compute the softmax operation on an array of specified size using the
    Numba implementation. It uses parameterized inputs for varying
    function names and sizes to validate the performance in different configurations.

    :param benchmark: The pytest benchmarking fixture used to time the execution
                      of the softmax function.
    :param func_name: The name of the function being tested. This parameter is
                      parameterized by the pytest decorator.
    :param size: The size of the input array for which the softmax function is
                 benchmarked. This parameter is also parameterized by the
                 pytest decorator.
    :return: None
    """
    benchmark(softmax_numba, array_instance)
