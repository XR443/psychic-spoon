import random

import mlflow
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from torch.optim import Adam
from tqdm import tqdm

from model_utils import test_train, transpose_image, get_image, get_image_rle, crop, get_gray_color_image, \
    dice_loss

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

data = pd.read_csv("dataset/understanding_cloud_organization/train.csv")

splitted = data['Image_Label'].str.split(pat='_', expand=True)

data['Image'] = splitted[0]
data['Label'] = splitted[1]

print(data[["Label", "EncodedPixels"]].groupby("Label").count())

images = data["Image"].unique()
images_train, images_test = train_test_split(images, test_size=0.2, random_state=42)
########################################################################################################################
import cnn_model as models

encoder_decoder = models.EncoderDecoder().to(device)
# encoder_decoder = models.EncoderDecoderWithConnections().to(device)

learning_rate = 0.01
optimizer = Adam(encoder_decoder.parameters(), lr=learning_rate)
criterion = nn.BCEWithLogitsLoss()


def train(x_list, y_list, need_learn, metric=lambda true, pred: 0):
    if not x_list or not y_list:
        return None

    X = torch.Tensor(np.asarray(x_list)).to(device)
    y = torch.Tensor(np.asarray(y_list)).to(device)

    loss, metric_loss = test_train(X, y, encoder_decoder, optimizer, criterion, 1, None, device, need_learn, metric)

    x_list.clear()
    y_list.clear()
    del X
    del y

    return loss, metric_loss


def iterate_images(images, need_learn):
    losses = []
    metric_losses = []

    random.shuffle(images)

    for index, image in enumerate(tqdm(images)):
        if index != 0 and index % packet_size == 0:
            current_loss, metric_loss = train(transposed_images, rle_images, need_learn, dice_loss)
            losses.append(current_loss)
            metric_losses.append(metric_loss)

        # image_windows, x_data, y_data = crop(get_edge(get_image(image_name=image), 150, 250))
        image_windows, x_data, y_data = crop(get_gray_color_image(get_image(image_name=image), 150))
        for window in image_windows:
            transposed_images.append(transpose_image(window))

        for val in zip(*map(lambda x: crop(x)[0], get_image_rle(data, image))):
            rle_images.append(val)
    else:
        if transposed_images and rle_images:
            print("Последний неполный пакет")
            loss, metric_loss = train(transposed_images, rle_images, need_learn, dice_loss)
            losses.append(loss)
            metric_losses.append(metric_loss)
    print("Потери за набор данных:")
    print(f"Первые: {losses[:6]}")
    print(f"Середина: {losses[len(losses) // 2 - 3:len(losses) // 2 + 3]}")
    print(f"Последние: {losses[-6:]}")

    metric_loss = sum(metric_losses) / len(metric_losses)

    losses.clear()
    metric_losses.clear()

    return metric_loss


mlflow.set_experiment("Cnn Learning Experiment")

mlflow.config.enable_system_metrics_logging()
mlflow.config.set_system_metrics_sampling_interval(1)

epochs = 25
# epochs = 50
packet_size = 2
# packet_size = 150

print("Кол-во данных (всего):", len(images), ".", "Пакетов:", len(images) / packet_size)
print("Кол-во данных (обучение):", len(images_train), ".", "Пакетов:", len(images_train) / packet_size)
print("Кол-во данных (проверка):", len(images_test), ".", "Пакетов:", len(images_test) / packet_size)

transposed_images = list()
rle_images = list()

epoch_train_metric_losses = list()
epoch_test_metric_losses = list()

early_stopping_attempt_threshold = 5
previous_test_metric_loss = 0
early_stopping_attempt = 0
epsilon = 0.001

params = {
    "epochs": epochs,
    "packet_size": packet_size,
    "epsilon": epsilon,
    "early_stopping_threshold": early_stopping_attempt_threshold,
    "learning_rate": learning_rate,
    "optimizer": type(optimizer).__name__,
    "criterion": type(criterion).__name__,
    "metric": "DiceLoss (custom def)",
}

early_stop = False

with mlflow.start_run() as run:
    # Log training parameters
    mlflow.log_params(params)

    for epoch in range(epochs):
        epoch = epoch + 1

        random.seed(epoch)
        print(f"Эпоха {epoch}/{epochs}. Обучение")
        train_metric_loss = iterate_images(images_train, True)
        epoch_train_metric_losses.append(train_metric_loss)

        print(f"Эпоха {epoch}/{epochs}. Проверка")
        test_metric_loss = iterate_images(images_test, False)
        epoch_test_metric_losses.append(test_metric_loss)

        if abs(previous_test_metric_loss - test_metric_loss) < epsilon:
            early_stopping_attempt += 1
        else:
            early_stopping_attempt = 0
            previous_test_metric_loss = test_metric_loss

        if early_stopping_attempt > early_stopping_attempt_threshold:
            print(f"### Ранняя остановка ({epoch}/{epochs}).)###")
            print(f"Изменение метрики меньше чем {epsilon} на протяжении {early_stopping_attempt_threshold} эпох")
            early_stop = True

        # Log epoch metrics
        mlflow.log_metrics({
            "train_metric": train_metric_loss,
            "test_metric": test_metric_loss,
            "early_stopping": early_stop
        },
            step=epoch)

        # Log checkpoint at the end of each epoch
        mlflow.pytorch.log_model(encoder_decoder, name=f"checkpoint_{epoch}")

        if early_stop:
            break

    # Log the final trained model
    model_info = mlflow.pytorch.log_model(encoder_decoder,
                                          name="final_model",
                                          registered_model_name=type(encoder_decoder).__name__)

########################################################################################################################
range_epochs_ = [i + 1 for i in range(epochs)]
plt.figure(figsize=(14, 7))
plt.plot(range_epochs_, epoch_train_metric_losses, "b-", label="train_loss")
plt.plot(range_epochs_, epoch_test_metric_losses, "r-", label="test_loss")
plt.legend(loc='best', fontsize=12)
plt.xticks(range_epochs_)
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.grid(True)
plt.savefig('train_plot.svg')
