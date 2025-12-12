from collections import namedtuple
from typing import List, Tuple

import torch.nn as nn
import random
from datetime import datetime
from multiprocessing import Queue, freeze_support

import numpy as np
from sklearn.model_selection import ParameterGrid
from torch.optim import Adam, SGD, RMSprop


class RegressionFCModel(nn.Module):
    def __init__(self, first_layer, activation_1, activation_2, activation_3,
                 dropout=False, dropout_rate=0.2,                 batch_norm=False):
        super(RegressionFCModel, self).__init__()

        self.fc1 = nn.Linear(2, first_layer)
        self.activation_1 = activation_1()
        self.batch_norm = nn.BatchNorm1d(first_layer) if batch_norm else lambda x: x

        self.fc2 = nn.Linear(first_layer, first_layer // 2)
        self.activation_2 = activation_2()
        self.dropout = nn.Dropout(dropout_rate) if dropout else lambda x: x

        self.fc3 = nn.Linear(first_layer // 2, first_layer // 4)
        self.activation_3 = activation_3()
        self.dropout = nn.Dropout(dropout_rate) if dropout else lambda x: x

        self.fc4 = nn.Linear(first_layer // 4, 1)

    def forward(self, x):
        out = self.activation_1(self.fc1(x))
        out = self.batch_norm(out)

        out = self.activation_2(self.fc2(out))

        out = self.activation_3(self.fc3(out))
        out = self.dropout(out)

        return self.fc4(out)


def build_model_and_optimizer(item, skip_optimizer=False):
    """
    Построение модели и оптимизатора
    :param item: словарь параметров для построения модели
    :param skip_optimizer: флаг необходимости оптимизатора. По умолчанию создается оптимизатор
    :return: model if skip_optimizer else (model, optimizer)
    """
    model = RegressionFCModel(
        item["hidden_size"],
        item["activation_1"],
        item["activation_2"],
        item["activation_3"],
        item["dropout"],
        item["dropout_rate"],
        item["batch_norm"],
    )

    if skip_optimizer:
        return model

    optimizer = item['optimizer'](model.parameters(), lr=item['learning_rate'])

    return model, optimizer


def get_params():
    """
    Генерирует параметры для кросс-валидации
    :return: словарь параметров
    """
    param_grid = {
        'hidden_size': [2 ** i for i in range(4, 8)],
        # 'hidden_size': [12],
        'num_epochs': [i for i in range(100, 200, 25)],
        # 'num_epochs': [10],
        'learning_rate': [0.01, 0.05, 0.1],
        # 'learning_rate': [0.01],
        'batch_size': [None, *[i for i in range(1000, 3000 + 1, 1000)]],
        # 'optimizer': [Adam, SGD, RMSprop],  # до этого всегда побеждал Адам
        'optimizer': [Adam],
        # 'dropout': [True, False],
        'dropout': [True],
        'dropout_rate': [0.2, 0.25, 0.3],
        # 'batch_norm': [True, False],
        'batch_norm': [True],
    }

    for layer in range(1, 4):
        param_grid[f"activation_{layer}"] = [nn.Tanh, nn.ReLU]

    grid = ParameterGrid(param_grid)

    return list(grid)
