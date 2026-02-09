import pandas as pd
import torch
from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split, ParameterGrid

TRAIN_FILE = "./dataset/data/in_domain_train.csv"
DEV_FILE = "./dataset/data/in_domain_dev.csv"

symbols = set()


def normalize_special_symbols(text):
    """
    Заменяем проблемные символы на безопасные аналоги
    """

    # Словарь замен
    replacements = {
        '\u2013': '-',  # en-dash
        '\u2014': '-',  # em-dash
        '\u2015': '-',  # horizontal bar
        '\u2212': '-',  # minus sign
        '\u2010': '-',  # hyphen
        '\u2011': '-',  # non-breaking hyphen
        '\u2012': '-',  # figure dash
    }

    # Заменяем все проблемные символы
    for old, new in replacements.items():
        text = text.replace(old, new)

    no_accent = ['о', ]
    accented = ['ó', ]

    for i in range(len(accented)):
        text = text.replace(accented[i], no_accent[i])

    drop_symbols = ['^', '­', '¯', '…', '№']
    for sym in drop_symbols:
        text = text.replace(sym, '')

    symbols.update(text)
    return text


# пропустим записи с тире, т.к. T5 tokenizer проставляет им два eos тега и ругается на этот факт
# один eos в конце и один перед тире(знаком минус)
def get_dataset():
    train_df, test_df = map(
        pd.read_csv, (TRAIN_FILE, DEV_FILE)
    )
    train_df["sentence"] = train_df["sentence"].apply(normalize_special_symbols)
    test_df["sentence"] = test_df["sentence"].apply(normalize_special_symbols)
    # train_df = train_df.drop(train_df[train_df["sentence"].str.contains("―")].index)
    # test_df = test_df.drop(test_df[test_df["sentence"].str.contains("―")].index)

    train_max_length = train_df["sentence"].str.len().max()
    dev_max_length = test_df["sentence"].str.len().max()

    train_df, dev_df = train_test_split(train_df, test_size=0.2, random_state=42)
    cols = ["sentence", "acceptable"]
    train, dev, test = map(Dataset.from_pandas, (train_df[cols], dev_df[cols], test_df[cols]))
    return DatasetDict(train=train, dev=dev, test=test), max(train_max_length, dev_max_length)


# get_dataset()

POS_LABEL = "y"
NEG_LABEL = "n"

# result["input_ids"].eq(2)
# (result["input_ids"].eq(2)).sum(1)[898]
# torch.unique_consecutive(eos_mask.sum(1)).numel()
# torch.unique_consecutive(result["input_ids"].eq(2).sum(1)).numel() 254 539
eos_vals = []


def preprocess_examples(examples, tokenizer, max_length=512):
    result = tokenizer(examples["sentence"], padding='max_length', max_length=max_length, return_tensors="pt")
    result["labels"] = examples["acceptable"]
    eos_val = torch.unique_consecutive(result["input_ids"].eq(2).sum(1)).numel()
    if eos_val > 1:
        eos_vals.append(eos_val)
        print("Кол-во данных с более чем одним eos:", f"{eos_val}/{sum(eos_vals)}")
    return result


def get_params():
    """
    Генерирует параметры для кросс-валидации
    :return: словарь параметров
    """
    param_grid = {
        'num_epochs': [i for i in range(1, 4)],
        'learning_rate': [1e-5, 2e-5, 5e-5],
        'batch_size': [8],
        'weight_decay': [0.0, 0.01],
    }

    grid = ParameterGrid(param_grid)

    return list(grid)
