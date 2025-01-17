"""
Copyright VIP Group
Licensed under the Apache License, Version 2.0.
Modify from https://github.com/rwightman/pytorch-image-models
Original copyright of Ross Wightman below, modifications by VIP Group

Hacked together by / copyright Ross Wightman
"""
import jittor as jt
import jittor.nn as F
from jittor import nn
from typing import List, Tuple, Optional

from .helpers import to_2tuple
from .padding import pad_same, get_padding_value


def avg_pool2d_same(x, kernel_size: List[int], stride: List[int], padding: List[int] = (0, 0),
                    ceil_mode: bool = False, count_include_pad: bool = True):
    # FIXME how to deal with count_include_pad vs not for external padding?
    x = pad_same(x, kernel_size, stride)
    return F.avg_pool2d(x, kernel_size, stride, (0, 0), ceil_mode, count_include_pad)


class AvgPool2dSame(nn.Module):
    """ Tensorflow like 'SAME' wrapper for 2D average pooling
    """

    def __init__(self, kernel_size: int, stride=None, padding=0, ceil_mode=False, count_include_pad=True):
        kernel_size = to_2tuple(kernel_size)
        stride = to_2tuple(stride)
        super(AvgPool2dSame, self).__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = [0, 0]
        self.ceil_mode = ceil_mode
        self.count_include_pad = count_include_pad

    def execute(self, x):
        return avg_pool2d_same(
            x, self.kernel_size, self.stride, self.padding, self.ceil_mode, self.count_include_pad)


def max_pool2d_same(
        x, kernel_size: List[int], stride: List[int], padding: List[int] = (0, 0),
        dilation: List[int] = (1, 1), ceil_mode: bool = False):
    x = pad_same(x, kernel_size, stride, value=-float('inf'))
    if dilation is not None:
        kernel_size = (kernel_size[0] - 1) // 2 * (dilation[0]) * 2 + 1
        dilation = None
    return F.max_pool2d(x, kernel_size, stride[0], 0, dilation, ceil_mode=ceil_mode)


class MaxPool2dSame(nn.Module):
    """ Tensorflow like 'SAME' wrapper for 2D max pooling
    """

    def __init__(self, kernel_size: int, stride=None, padding=0, dilation=1, ceil_mode=False, count_include_pad=True):
        kernel_size = to_2tuple(kernel_size)
        stride = to_2tuple(stride)
        dilation = to_2tuple(dilation)
        super(MaxPool2dSame, self).__init__()
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = [0, 0]
        self.dilation = dilation
        self.ceil_mode = ceil_mode

    def execute(self, x):
        return max_pool2d_same(x, self.kernel_size, self.stride, self.padding, self.dilation, self.ceil_mode)


def create_pool2d(pool_type, kernel_size, stride=None, **kwargs):
    stride = stride or kernel_size
    padding = kwargs.pop('padding', '')
    padding, is_dynamic = get_padding_value(padding, kernel_size, stride=stride, **kwargs)
    if is_dynamic:
        if pool_type == 'avg':
            return AvgPool2dSame(kernel_size, stride=stride, **kwargs)
        elif pool_type == 'max':
            return MaxPool2dSame(kernel_size, stride=stride, **kwargs)
        else:
            assert False, f'Unsupported pool type {pool_type}'
    else:
        if pool_type == 'avg':
            return nn.AvgPool2d(kernel_size, stride=stride, padding=padding, **kwargs)
        elif pool_type == 'max':
            return nn.MaxPool2d(kernel_size, stride=stride, padding=padding, **kwargs)
        else:
            assert False, f'Unsupported pool type {pool_type}'
