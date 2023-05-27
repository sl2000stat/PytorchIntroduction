"""
Name: pytorch_helper_functions.py in Project: PytorchIntroduction
Author: Simon Leiner
Date: 27.05.23
Description: This file contains helper functions for the pytorch introduction
"""

import numpy as np
import torch


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Checked: Function works

def set_global_seed(seed=42):
    """
    This function sets the global seed for all random number generators.

    :param seed: int: seed to set
    :return: None
    """

    # set the seed for numpy, torch and cuda
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)

    return None


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Checked: Function works

def print_train_time(start, end, device=None):
    """
    This function prints the time it took to train the model.

    :param start: float: Start time of computation (preferred in timeit format).
    :param end: float: End time of computation.
    :param device: str: Device that compute is running on. Defaults to None.
    :return: total_time: float: time between start and end in seconds (higher is longer).
    """

    # calculate the total time
    total_time = end - start

    # print the total time
    print(f"\nTrain time on {device}: {total_time:.3f} seconds")

    return total_time

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

