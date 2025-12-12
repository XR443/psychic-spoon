import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch import no_grad, nn

from regression_model import build_model_and_optimizer


def train(X, y, model, optimizer, criterion, need_to_learn=True):
    """
    Метод 1 прохода обучения модели с backward

    :param X: входные данные
    :param y: ожидаемый выход
    :param model: модель обучения
    :param optimizer: оптимизатор
    :param criterion: функция потерь
    :param need_to_learn: необходимо ли обновлять веса модели
    :return: значение потерь
    """
    optimizer.zero_grad()

    if need_to_learn:
        outputs = model(X)
        loss = criterion(outputs, y)
        # loss = criterion(min_max_scale(outputs), y)

        # Backpropagation and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    else:
        with no_grad():
            outputs = model(X)
            loss = criterion(outputs, y)

    return loss.item()


def test_train(X, y, model, optimizer, criterion, num_epochs, batch_size, device):
    """
    Метод обучения модели по эпохам

    :param X: входные данные
    :param y: ожидаемый выход
    :param model: модель обучения
    :param optimizer: оптимизатор
    :param criterion: функция потерь
    :param num_epochs: количество эпох
    :param batch_size: размер пакета для обучения, если None то используется весь X
    :param device: куда поместить значения
    :return: None
    """
    for epoch in range(num_epochs):
        if batch_size:
            X_batched = X.split(batch_size)
            y_batched = y.split(batch_size)
            for i in range(len(X_batched)):
                train(X_batched[i].to(device), y_batched[i].to(device), model, optimizer, criterion)
        else:
            train(X, y, model, optimizer, criterion)


def cross_val(X_train, y_train, X_test, y_test, params, storage, device):
    """
    Провод кросс-валидацию с подбором гиперпараметров для обучения.

    :param X_train: x для обучения
    :param y_train: y для обучения
    :param X_test: x для проверки
    :param y_test: y для проверки
    :param params: параметры создания модели и обучения
    :param storage: куда сохранять результаты
    :param device: куда поместить значения
    :return: минимальную найденную ошибку, лучший набор параметров, который привел к наименьшей ошибке
    """
    best_item = None
    min_loss = float('inf')

    for item in params:
        model, optimizer = build_model_and_optimizer(item)

        model.to(device)

        X_train = X_train.to(device)
        y_train = y_train.to(device)
        X_test = X_test.to(device)
        y_test = y_test.to(device)

        criterion = nn.MSELoss()

        test_train(X_train, y_train, model, optimizer, criterion, item['num_epochs'], item['batch_size'], device)

        test_loss = train(X_test, y_test, model, optimizer, criterion, need_to_learn=False)
        if test_loss < min_loss:
            min_loss = test_loss
            best_item = item

    storage.put((min_loss, best_item))
    print(f'Наименьшая ошибка ({min_loss:.4f}) достигнута при параметрах: {best_item}')
    return min_loss, best_item


def generate_data():  # генерируем случайные точки
    """
    Генерирует данные для обучения
    :return: общий тензор, X_train, X_test, X_val, y_train, y_test, y_val
    """
    np.random.seed(42)
    samples = torch.Tensor(np.random.uniform(-10, 10, (20000, 2)))
    target = torch.Tensor([(x, y, np.sin(x + 2 * y) * np.exp(-(2 * x + y) ** 2)) for x, y in samples])
    X_train, X_test, y_train, y_test = train_test_split(target[:, :-1], target[:, -1].reshape(-1, 1),
                                                        test_size=0.3, random_state=42)
    X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, test_size=0.5, random_state=42)

    if len(X_train) != len(y_train):
        raise ValueError("Train data does not have same length as train target")

    if len(X_test) != len(y_test):
        raise ValueError("Test data does not have same length as test target")

    if len(X_val) != len(y_val):
        raise ValueError("Val data does not have same length as va; target")

    # sin(x + 2*y)exp(-(2x + y)^2)

    return target, X_train, X_test, X_val, y_train, y_test, y_val
