import math

import mlflow
import pandas as pd
import pandas as pd
import numpy as np
import torch
from pandas import DataFrame
from pycocoevalcap.cider.cider import Cider
from tensorflow.python.keras.backend import in_train_phase
from torch import Tensor, nn
from torch.nn.utils.rnn import pad_sequence
from tqdm import tqdm
from transformers import RobertaTokenizer, AutoTokenizer

from model_utils import get_image, transpose_image, train, get_length_filter, chunked, images_with_target_tokens, \
    get_batches, prepare_batch, get_log, test, prepare_dataset
from models import ImageCaptionModel
from datetime import datetime

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mlflow.config.enable_system_metrics_logging()
mlflow.config.set_system_metrics_sampling_interval(1)

tokenizer_name = 'roberta-base'
# tokenizer_name = 'google-bert/bert-base-uncased'
# tokenizer_name = 'google-bert/bert-large-uncased'
tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

model = ImageCaptionModel(tokenizer.vocab_size, tokenizer.pad_token_id).to(device)
model_name = type(model).__name__

mlflow.set_experiment("Image2Caption")

rows_batch_size = 5
learning_rate = 0.0001
epochs = 15
min_len_init, max_len_init, step = 0, 10, 7

captions = pd.read_csv("./dataset/captions.txt")
captions = captions[captions['comment_number'] == 4]

np.random.seed(42)
unique_images = captions["image_name"].unique()
size_restriction_filter = None
# 1/2
# size_restriction_filter = np.random.choice(a=unique_images, size=int(len(unique_images) * .5))
# 1/4
# size_restriction_filter = np.random.choice(a=unique_images, size=int(len(unique_images) * .25))
# 1/8
# size_restriction_filter = np.random.choice(a=unique_images, size=int(len(unique_images) * .125))
if size_restriction_filter:
    captions: DataFrame = captions[captions["image_name"].isin(size_restriction_filter)]

print(f"Данных для обработки: {len(captions)}")

captions = prepare_dataset(captions, tokenizer, tokenizer_name)
max_length = max(captions["comment"].map(len))

opt = torch.optim.Adam(model.parameters(), lr=learning_rate)  # initialize Adam optimizer
criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)  # initialize loss

sequence_size = max(captions["comment"].map(len))

run_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
run_name = f"{model_name}_{run_timestamp}"

epoch_train_metric_losses = []
epoch_test_metric_losses = []


def get_sampling_rate(epoch, total_epochs, start_rate=1.0, end_rate=0.0):
    """Линейное уменьшение использования учителя"""
    return start_rate - (start_rate - end_rate) * (epoch / total_epochs)


with (mlflow.start_run(run_name=run_name) as run):
    mlflow.log_params({
        "device": device,
        "model_name": model_name,
        "tokenizer": tokenizer_name,
        "learning_rate": learning_rate,
        "epochs": epochs,
        "rows_batch_size": rows_batch_size,
        "min_len_init": min_len_init,
        "max_len_init": max_len_init,
        "len_step": step,
    })

    cider = Cider()

    unique_images = captions["image_name"].unique()
    test_filter = np.random.choice(a=unique_images, size=int(len(unique_images) * .1))
    train_captions: DataFrame = captions[~captions["image_name"].isin(test_filter)]
    test_captions: DataFrame = captions[captions["image_name"].isin(test_filter)]
    # сортируем чтобы в батче были 1 изображение и 1 предложение
    test_captions = test_captions.sort_values(by=["comment_number", "image_name"])

    batches_with_errors = 0

    for epoch in range(1, epochs + 1):
        in_epoch_train_losses = []
        in_epoch_test_losses = []
        cider_scores = []

        min_len, max_len = min_len_init, max_len_init
        # SWITCH TO TRAIN
        model.train()
        while min_len < max_length:

            len_filter = get_length_filter(train_captions, min_len, max_len)
            min_len += step
            max_len += step

            for names, images, comments in tqdm(chunked(train_captions[len_filter], rows_batch_size)):
                x_images, y = prepare_batch(images, comments, tokenizer, device)

                loss, result, _ = train(
                    x_images, y,
                    model, opt, criterion,
                    scheduled_sampling=get_sampling_rate(epoch - 1, epochs)
                )

                if loss is not None:
                    if loss == -1:
                        print(f"Не удалось обработать пакет изображений, результат nan")
                        batches_with_errors += 1
                        continue
                    in_epoch_train_losses.append(loss.item())

            if in_epoch_train_losses:
                print(f"\t{epoch}: intermediate test loss = {sum(in_epoch_train_losses) / len(in_epoch_train_losses)}")

        train_metric_calculated = False
        if in_epoch_train_losses:
            in_epoch_train_loss = sum(in_epoch_train_losses) / len(in_epoch_train_losses)
            train_metric_calculated = True
        else:
            in_epoch_train_loss = -1
        print(f"\t{epoch}: epoch test loss = {in_epoch_train_loss}")

        # SWITCH TO EVAL
        model.eval()
        for number in test_captions["comment_number"].unique():

            min_len, max_len = min_len_init, max_len_init
            batch_index = 1

            cider_results = dict()
            cider_references = dict()

            for_chunking = test_captions[test_captions["comment_number"] == number]

            while min_len < max_length:

                len_filter = get_length_filter(for_chunking, min_len, max_len)

                min_len += step
                max_len += step

                for_chunking = for_chunking[len_filter]
                for names, images, comments in chunked(for_chunking, rows_batch_size):
                    x_images, y = prepare_batch(images, comments, tokenizer, device)

                    loss, result, hidden = test(
                        x_images, y,
                        model, criterion
                    )

                    if loss is not None:
                        if loss == -1:
                            print(f"Не удалось обработать пакет изображений, результат nan")
                            batches_with_errors += 1
                            continue
                        in_epoch_test_losses.append(loss.item())

                    for image_name, decoded in zip(names,
                                                   [tokenizer.decode(t, skip_special_tokens=True) for t in result]):
                        filtered = test_captions['image_name'] == image_name
                        cider_references[image_name] = test_captions[filtered]["comment"].to_list()

                        cider_results[image_name] = [decoded]

                    print(get_log(epoch, batch_index, result, y, loss, tokenizer))
                    batch_index += 1

                    score = cider.compute_score(cider_references, cider_results)
                    cider_scores.append(score[0])

        test_metric_calculated = False
        if in_epoch_test_losses:
            in_epoch_test_loss = sum(in_epoch_test_losses) / len(in_epoch_test_losses)
            epoch_train_metric_losses.append(in_epoch_train_loss)
            test_metric_calculated = True

        cider_score = 0
        if cider_scores:
            cider_score = sum(cider_scores) / len(cider_scores)
        mlflow.log_metrics({
            "train_metric": in_epoch_train_loss,
            "train_metric_calculated": train_metric_calculated,
            "test_metric": in_epoch_test_loss,
            "test_metric_calculated": test_metric_calculated,
            "batches_with_errors": batches_with_errors,
            "cider_test_metric": cider_score
        },
            step=epoch)

        mlflow.pytorch.log_model(model, name=f"checkpoint_{epoch}")

    model_info = mlflow.pytorch.log_model(model, name="final_model")
