import math
from pathlib import Path

import cv2
import numpy as np
import torch
from torch import nn, Tensor
from torch.nn.utils.rnn import pad_sequence


def train(images, y, model, optimizer, criterion, gradient_clipping=1, scheduled_sampling=0.5):
    model.zero_grad()
    sequence = y[:, :1]
    predictions = []
    hidden = None
    while len(sequence[0]) < len(y[0]):
        result, hidden = model(images, sequence, hidden)
        if torch.isnan(result).any():
            return -1, result, hidden

        last_token_result = result[:, -1, :]

        predicted_token = torch.argmax(last_token_result, dim=1, keepdim=True)
        predictions.append(last_token_result)

        if np.random.random() < scheduled_sampling:
            predicted_token = y[:, sequence.size(1):sequence.size(1) + 1]

        sequence = torch.cat([sequence, predicted_token], dim=1)

    # predictions = predictions.detach()
    loss = 0
    losses = 0
    predictions = torch.stack(predictions, dim=1)
    y = y[:, 1:]
    for i in range(predictions.size(0)):
        i_loss = criterion(predictions[i], y[i])
        if not math.isnan(i_loss.item()):
            loss += i_loss
            losses += 1

    # если не удалось посчитать потери, значит все таргеты PAD
    if not losses:
        return None, predictions, hidden

    loss = loss / losses

    loss.backward()

    if gradient_clipping > 0:
        # `clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
        # we cut them
        nn.utils.clip_grad_norm_(model.parameters(), gradient_clipping)

    # 6. update weights with optimizer
    optimizer.step()

    return loss, predictions, hidden


def test(images, y, model, criterion):
    with torch.no_grad():
        sequence = y[:, :1]
        hidden = None
        predictions = []
        while len(sequence[0]) < len(y[0]):
            result, hidden = model(images, sequence, hidden)
            if torch.isnan(result).any():
                return -1, result, hidden

            last_token_result = result[:, -1, :]
            predictions.append(last_token_result)

            # predicted_token = torch.argmax(last_token_result, dim=1, keepdim=True)
            predicted_token = torch.multinomial(torch.softmax(last_token_result, dim=1), num_samples=1)
            sequence = torch.cat([sequence, predicted_token], dim=1)

        loss = 0
        losses = 0
        predictions = torch.stack(predictions, dim=1)
        y = y[:, 1:]
        for i in range(predictions.size(0)):
            i_loss = criterion(predictions[i], y[i])
            if not math.isnan(i_loss.item()):
                loss += i_loss
                losses += 1

        # если не удалось посчитать потери, значит все таргеты PAD
        if not losses:
            return None, sequence, hidden

        loss = loss / losses

        return loss, sequence, hidden


def eval_image(images, sequence, model, eos_token):
    with torch.no_grad():
        hidden = None
        predictions = []
        while len(sequence[0]) < 512:
            result, hidden = model(images, sequence, hidden)
            if torch.isnan(result).any():
                return result, hidden

            last_token_result = result[:, -1, :]
            predictions.append(last_token_result)

            predicted_token = torch.multinomial(torch.softmax(last_token_result, dim=1), num_samples=1)
            sequence = torch.cat([sequence, predicted_token], dim=1)
            if predicted_token[-1] == eos_token:
                break

        return sequence, hidden


def get_images(folder_path="./dataset/flickr30k_images/") -> dict:
    images = dict()
    folder_path = Path(folder_path)
    for file_path in folder_path.iterdir():
        image = cv2.imread(str(file_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        images[file_path.name] = image
    return images


def get_image(folder_path="./dataset/flickr30k_images/", image_name=None):
    if image_name:
        image = cv2.imread(str(Path(folder_path).joinpath(image_name).absolute()))
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    folder_path = Path(folder_path)
    for file_path in folder_path.iterdir():
        image = cv2.imread(str(file_path))
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return None


def transpose_image(image):
    if len(image.shape) == 3:
        return image.transpose(2, 0, 1)
    else:
        return image.reshape(1, image.shape[0], image.shape[1])


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


def pad_to_size_reflect_opencv(image, target_height=512, target_width=512):
    """
    Дополняет изображение до target_height x target_width симметричным копированием

    Args:
        image: входное изображение (numpy array)
        target_height: желаемая высота
        target_width: желаемая ширина

    Returns:
        изображение с отраженными границами
    """
    h, w = image.shape[:2]

    # Вычисляем отступы
    top = (target_height - h) // 2
    bottom = target_height - h - top
    left = (target_width - w) // 2
    right = target_width - w - left

    # Применяем отражение
    padded = cv2.copyMakeBorder(
        image,
        top, bottom, left, right,
        cv2.BORDER_REFLECT
    )

    return padded


def save_and_pad_image(target_path, image_name, image):
    path = Path(target_path).joinpath(image_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    padded = pad_to_size_reflect_opencv(image)
    img_bgr = cv2.cvtColor(padded, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path.absolute()), img_bgr)


def get_length_filter(data, min_len, max_len):
    return (data["tokens_len"] >= min_len) & (data["tokens_len"] < max_len)


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
        image_names = [row["image_name"] for _, row in captions_chunk.iterrows()]
        yield image_names, input_images, tokenized_comments


def images_with_target_tokens(image, comment):
    target = comment
    return image, target


def get_batches(data, batch_size):
    result = []
    for row in data:
        result.append([chunk for chunk in chunks(row, batch_size)])
    return result


def prepare_batch(images, comments, tokenizer, device):
    images_input = []
    targets = []

    for i in range(len(comments)):
        ims, tokens = images_with_target_tokens(images[i], comments.iloc[i])
        images_input.append(ims)
        targets.append(tokens)

    x_images = Tensor(images_input).to(device)

    y = pad_sequence(targets, batch_first=True, padding_value=tokenizer.pad_token_id)
    y = y.to(torch.long).to(device)

    return x_images, y


def get_log(epoch, batch_index, result, y, loss, tokenizer):
    decoded = []
    for i in range(result.size(0)):
        if len(result.size()) == 2:
            result_str = "".join([tokenizer.decode(t) for t in result[i]])
        else:
            result_str = "".join([tokenizer.decode(torch.argmax(t).item()) for t in result[i]])
        target_str = "".join([tokenizer.decode(t) for t in y[i]])

    decoded.append(f"\t{epoch}:{batch_index}:{i} = \t{result_str}\n\t\t\t\t{target_str}")
    decoded_str = "\n".join(decoded)

    return f">>> {epoch}: {loss}:\n{decoded_str}"

def prepare_dataset(captions, tokenizer, tokenizer_name):
    captions["comment"] = captions["comment"].map(lambda x: x.replace(' .', '.'))
    captions["comment"] = captions["comment"].map(lambda x: x.replace('  ', ' '))

    uncased_tokenizer = 'uncased' in tokenizer_name
    if uncased_tokenizer:
        captions["comment"] = captions["comment"].map(lambda x: x.lower())

    max_length = max(captions["comment"].map(len))

    captions["tokenized_str"] = captions["comment"].map(lambda x: tokenizer(x, return_tensors="pt",
                                                                            return_special_tokens_mask=True,
                                                                            padding="max_length",
                                                                            max_length=max_length))

    def map_to_clear_token_row(tokenized):
        without_special = tokenized["input_ids"][~torch.tensor(tokenized["special_tokens_mask"], dtype=torch.bool)]
        return torch.cat([
            Tensor([tokenizer.bos_token_id]).to(torch.long),
            without_special,
            Tensor([tokenizer.eos_token_id]).to(torch.long)
        ])

    captions["tokens"] = captions["tokenized_str"].map(map_to_clear_token_row)
    captions["tokens_len"] = captions["tokens"].map(lambda x: len(x))

    return captions