import math
from datetime import datetime

import mlflow
import pandas as pd
import torch
from matplotlib import pyplot as plt
from torch import Tensor, nn
from torch.nn.utils.rnn import pad_sequence
from transformers import RobertaTokenizer

from model_utils import get_image, transpose_image
from models import LanguageModelling

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mlflow.set_experiment("Language Modelling. Experiments before Image2Caption")

mlflow.config.enable_system_metrics_logging()
mlflow.config.set_system_metrics_sampling_interval(1)

tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
model = LanguageModelling(tokenizer.vocab_size, tokenizer.pad_token_id).to(device)

# todo ограничение размера для тестов
captions = pd.read_csv("./dataset/captions.txt")[:10000]
# captions = pd.read_csv("./dataset/captions.txt")

max_length = max(captions["comment"].map(len))

captions["tokenized_str"] = captions["comment"].map(lambda x: tokenizer(x, return_tensors="pt",
                                                                        return_special_tokens_mask=True,
                                                                        padding="max_length", max_length=max_length))


def map_to_clear_token_row(tokenized):
    without_special = tokenized["input_ids"][~torch.tensor(tokenized["special_tokens_mask"], dtype=torch.bool)]
    return torch.cat([
        Tensor([tokenizer.bos_token_id]).to(torch.long),
        without_special,
        Tensor([tokenizer.eos_token_id]).to(torch.long)
    ])


captions["tokens"] = captions["tokenized_str"].map(map_to_clear_token_row)
captions["tokens_len"] = captions["tokens"].map(lambda x: len(x))

opt = torch.optim.Adam(model.parameters(), lr=0.01)  # initialize Adam optimizer
criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)  # initialize loss
# criterion = nn.CrossEntropyLoss()  # initialize loss

rows_batch_size = 75
# sequence_size = max_length // 10
sequence_size = max_length


def chunks(data, batch_size):
    current_index = 0
    while current_index < len(data):
        yield data[current_index: min(current_index + batch_size, len(data))]
        current_index += batch_size


def chunked(dataframe, batch_size):
    for captions_chunk in chunks(dataframe, batch_size):
        images = {
            image: transpose_image(get_image("./dataset/flickr30k_images_resized", image))
            for image in set(captions_chunk["image_name"])
        }
        tokenized_comments = captions_chunk["tokens"]
        input_images = [images[row["image_name"]] for _, row in captions_chunk.iterrows()]
        yield input_images, tokenized_comments


def images_with_target_tokens(image, comment):
    prevs = comment[:-1]
    target = comment[1:]
    return image, prevs, target


def get_batches(data, batch_size):
    result = []
    for row in data:
        result.append([chunk for chunk in chunks(row, batch_size)])
    return result


run_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
epochs = 50
run_name = f"{type(model).__name__}_{run_timestamp}"
epoch_train_metric_losses=[]
with mlflow.start_run(run_name=run_name) as run:
    index = 0
    for epoch in range(1, epochs + 1):
        # for epoch in range(1, 2):
        min_len, max_len, step = 0, 10, 7
        in_epoch_losses = []
        while min_len < max_length:

            len_filter = (captions["tokens_len"] >= min_len) & (captions["tokens_len"] < max_len)
            max_len += step
            min_len += step

            for _, comments in chunked(captions[len_filter], rows_batch_size):
                prev_token = []
                targets = []

                for i in range(len(comments)):
                    _, prevs, tokens = images_with_target_tokens(_, comments.iloc[i])
                    prev_token.append(prevs)
                    targets.append(tokens)

                batched_x = get_batches(prev_token, sequence_size)
                batched_y = get_batches(targets, sequence_size)

                for i in range(len(batched_x[0])):
                    hidden = None

                    x_batch = [batch[i] for batch in batched_x]
                    y_batch = [batch[i] for batch in batched_y]

                    # Если у нас только PAD в X, то берем след пакет
                    # if (all([all(v.item() == tokenizer.pad_token_id for v in t) for t in x_batch])
                    #         or all([all(v.item() == tokenizer.pad_token_id for v in t) for t in y_batch])):
                    #     continue

                    model.zero_grad()

                    x = pad_sequence(x_batch, batch_first=True, padding_value=tokenizer.pad_token_id).to(device)
                    result, hidden = model(x, hidden)

                    # y = torch.stack([t for t in y_batch]).to(torch.long)
                    y = pad_sequence(y_batch, batch_first=True, padding_value=tokenizer.pad_token_id)
                    y = y.to(torch.long).to(device)
                    loss = 0
                    losses = 0
                    for i in range(result.size(0)):
                        i_loss = criterion(result[i], y[i])
                        if not math.isnan(i_loss):
                            loss += i_loss
                            losses += 1

                    # если не удалось посчитать потери, значит все таргеты PAD
                    if not losses:
                        continue

                    loss = loss / losses
                    in_epoch_losses.append(loss)

                    loss.backward()

                    decoded = []
                    for i in range(result.size(0)):
                        result_str = "".join([tokenizer.decode(torch.argmax(t).item()) for t in result[i]])
                        target_str = "".join([tokenizer.decode(t) for t in y[i]])
                        decoded.append(f"\t{epoch}:{index}:{i} = \t{result_str}\n\t\t\t\t{target_str}")
                    decoded_str = "\n".join(decoded)
                    print(f">>> {epoch}:{index}: {loss}:\n{decoded_str}")

                    index += 1

                    # `clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
                    # we cut them
                    clip = 5
                    nn.utils.clip_grad_norm_(model.parameters(), clip)
                    # 6. update weights with optimizer
                    opt.step()

        mlflow.log_metrics({
            "train_metric": sum(in_epoch_losses) / len(in_epoch_losses),
            # "test_metric": test_metric_loss
        },
            step=epoch)
        mlflow.pytorch.log_model(model, name=f"checkpoint_{epoch}")

    model_info = mlflow.pytorch.log_model(model, name="final_model")

# range_epochs_ = [i + 1 for i in range(epochs)]
# plt.figure(figsize=(14, 7))
# plt.plot(range_epochs_, epoch_train_metric_losses, "b-", label="train_loss")
# # plt.plot(range_epochs_, epoch_test_metric_losses, "r-", label="test_loss")
# plt.legend(loc='best', fontsize=12)
# plt.xticks(range_epochs_)
# plt.xlabel("Epochs")
# plt.ylabel("Loss")
# plt.grid(True)
# plt.savefig('train_plot.svg')
