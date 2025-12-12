import random
from datetime import datetime
from multiprocessing import Queue, freeze_support

import numpy as np
import torch
import torch.multiprocessing as mp
import torch.nn as nn
from sklearn.model_selection import ParameterGrid
from torch.optim import Adam, SGD, RMSprop

from model_utils import cross_val, generate_data, test_train
from plt_utils import visualize
from regression_model import build_model_and_optimizer, get_params


def run_with(target, X_train, X_test, X_val, y_train, y_test, y_val):
    """
    Создает и запускает обучение модели

    :param target: общий тензор, необходим для сериализации на диск
    :param X_train: x для обучения
    :param X_test: x для проверки
    :param X_val: x для валидации
    :param y_train: y для обучения
    :param y_test: y для проверки
    :param y_val: y для валидации
    :return: None
    """
    all_params = get_params()
    random.shuffle(all_params)

    print(f"Всего комбинаций параметров: {len(all_params)}")

    num_processes = 15

    params_batch_size = max(1, len(all_params) // num_processes)
    batched_params = [all_params[i:i + params_batch_size] for i in range(0, len(all_params), params_batch_size)]

    results = Queue()

    processes = []
    print(f"Всего процессов будет запущено: {len(batched_params)}")
    start_time = datetime.now()

    for rank, batch in enumerate(batched_params):
        process_name = f'Process-{rank}'
        p = mp.Process(target=cross_val, args=(X_train, y_train, X_test, y_test, batch, results, device),
                       name=process_name)
        p.start()
        processes.append(p)

    print(f"Процессов запущено: {len(processes)}")

    # Wait for all processes to finish
    cross_val_results = []
    for p in processes:
        p.join()
        cross_val_results.append(results.get())

    print(f"Все процессы завершили свою работу. Получено результатов: {len(cross_val_results)}")
    print(f"Продолжительность обработки: {datetime.now() - start_time}")

    best_loss, best_params = min(cross_val_results, key=lambda x: x[0])
    print(f"Лучший результат '{best_loss}' с параметрами: {best_params}")

    model, optimizer = build_model_and_optimizer(best_params)

    criterion = nn.MSELoss()

    model = model.to(device)
    X_train = X_train.to(device)
    y_train = y_train.to(device)

    test_train(X_train, y_train,
               model, optimizer, criterion,
               best_params['num_epochs'], best_params['batch_size'],
               device)

    metadata = {
        'model_state_dict': model.state_dict(),
        'params': best_params,
    }

    torch.save(metadata, f'model_multi.pt')
    torch.save(target, 'target.pt')

    model, _ = build_model_and_optimizer(best_params)

    metadata = torch.load(f'model_multi.pt', weights_only=False)
    model.load_state_dict(metadata['model_state_dict'])

    target = torch.load('target.pt')

    model.to(device)
    model.eval()

    X_val = X_val.to(device)
    y_val = y_val.to(device)

    outputs = model(X_val)
    loss = criterion(outputs, y_val)
    print('Потери на данных для валидации: {:.4f}'.format(loss.item()))

    all_outputs = model(target[:, :-1].to(device))
    loss = criterion(all_outputs, target[:, -1].reshape(-1, 1).to(device))

    print('Итоговые потери для всех данных: {:.4f}'.format(loss.item()))

    visualize(target, all_outputs, "Мульти модель")


if __name__ == '__main__':
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    freeze_support()

    run_with(*generate_data())
