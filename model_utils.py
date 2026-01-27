from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch
from torch import no_grad


def train(X, y, model, optimizer, criterion, need_to_learn=True, metric=lambda true, pred: torch.Tensor(0)):
    """
    Метод 1 прохода обучения модели с backward

    :param metric: функция расчета метрики
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

        # Backpropagation and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        metric_loss = metric(y, outputs)
    else:
        with no_grad():
            outputs = model(X)
            loss = criterion(outputs, y)
            metric_loss = metric(y, outputs)

    return loss.item(), metric_loss.item()


def test_train(X, y, model, optimizer, criterion, num_epochs, batch_size, device, need_learn=True,
               metric=lambda true, pred: torch.Tensor(0)):
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
    :return: min loss from training
    """
    avg_loss = None
    avg_metric_loss = None

    loss_sum = lambda current, new: (current + new) / 2 if current else new
    loss = 0
    metric_loss = 0
    for epoch in range(num_epochs):
        if batch_size:
            X_batched = X.split(batch_size).to(device)
            y_batched = y.split(batch_size).to(device)
            for i in range(len(X_batched)):
                loss, metric_loss = train(X_batched[i], y_batched[i], model, optimizer, criterion, need_learn, metric)
        else:
            loss, metric_loss = train(X, y, model, optimizer, criterion, need_learn, metric)
        avg_loss = loss_sum(avg_loss, loss)
        avg_metric_loss = loss_sum(avg_metric_loss, metric_loss)
    return avg_loss, avg_metric_loss


def get_images(folder_path="./dataset/understanding_cloud_organization/train_images/"):
    images = dict()
    folder_path = Path(folder_path)
    for file_path in folder_path.iterdir():
        image = cv2.imread(str(file_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        images[file_path.name] = image
    return images


def get_image(folder_path="./dataset/understanding_cloud_organization/train_images/", image_name=None):
    if image_name:
        image = cv2.imread(str(Path(folder_path).joinpath(image_name).absolute()))
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    folder_path = Path(folder_path)
    for file_path in folder_path.iterdir():
        image = cv2.imread(str(file_path))
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return None


def crop(image, size=512):
    x_size = image.shape[1]
    x_full_squares = x_size // size
    x_overlap = (((x_full_squares + 1) * size) - x_size) // x_full_squares

    y_size = image.shape[0]
    y_full_squares = y_size // size
    y_overlap = (((y_full_squares + 1) * size) - y_size) // y_full_squares

    results = []

    y = 0
    while y < y_size:
        y -= y_overlap if y > 0 else 0
        x = 0
        while x < x_size:
            x -= x_overlap if x > 0 else 0

            image_crop = image[y:y + size, x:x + size]
            results.append(image_crop)

            x += size

        y += size

    return np.asarray(results), (x_size, x_overlap, size), (y_size, y_overlap, size)


def get_edge(image, threshold1, threshold2):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edge_image = cv2.Canny(gray_image, threshold1, threshold2)
    return edge_image


def get_gray_color_image(image, threshold=None):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if threshold:
        gray_image[gray_image >= threshold] = 255
        gray_image[gray_image < threshold] = 0
    return gray_image


def rle_decode(encoded_pixels, mask_val=1, shape=(1400, 2100)):
    if pd.isna(encoded_pixels):
        return np.zeros(shape)
    encoded_pixels = encoded_pixels.split()

    starts = np.array(encoded_pixels[0::2], dtype=np.int32) - 1
    lengths = np.array(encoded_pixels[1::2], dtype=int)

    ends = starts + lengths

    mask = np.zeros(shape[0] * shape[1], dtype=np.uint8)
    for start, end in zip(starts, ends):
        mask[start:end] = mask_val

    return np.reshape(mask, shape, order='F')


def rle_decode_reshape(encoded_pixels, mask_val=1, shape=(1400, 2100)):
    return rle_decode(encoded_pixels, mask_val, shape).reshape(1, 1400, 2100)


def transpose_image(image):
    if len(image.shape) == 3:
        return image.transpose(2, 0, 1)
    else:
        return image.reshape(1, image.shape[0], image.shape[1])


def tensor_to_mask(tensor):
    return tensor.permute(1, 2, 0).reshape(1400, 2100)


def get_image_rle(data, image):
    image_labels = data[data["Image"] == image]

    fish_rle = rle_decode(image_labels[image_labels["Label"] == "Fish"]["EncodedPixels"].iloc[0])
    flower_rle = rle_decode(image_labels[image_labels["Label"] == "Flower"]["EncodedPixels"].iloc[0])
    gravel_rle = rle_decode(image_labels[image_labels["Label"] == "Gravel"]["EncodedPixels"].iloc[0])
    sugar_rle = rle_decode(image_labels[image_labels["Label"] == "Sugar"]["EncodedPixels"].iloc[0])

    return fish_rle, flower_rle, gravel_rle, sugar_rle


def dice_loss(y_true, y_pred):
    y_pred_thr = y_pred.mean()
    y_pred_bin = y_pred.clone()
    y_pred_bin[y_pred_bin >= y_pred_thr] = 1
    y_pred_bin[y_pred_bin < y_pred_thr] = 0
    return 1 - ((2 * ((y_true > 0) & (y_pred_bin > 0)).sum()) / ((y_true > 0).sum() + (y_pred_bin > 0).sum()))
