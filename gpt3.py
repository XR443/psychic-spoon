from datetime import datetime
from functools import partial

import evaluate
import mlflow
import numpy as np
import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, \
    AutoModelForCausalLM, GenerationConfig
from transformers.integrations import MLflowCallback

from model_utils import get_dataset, preprocess_examples, get_params

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

########################################################################################################################
model_name = "ai-forever/rugpt3medium_based_on_gpt2"
# model_name = "ai-forever/rugpt3large_based_on_gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to(device)

mlflow.set_experiment("NLP Learning Experiment")

mlflow.config.enable_system_metrics_logging()
mlflow.config.set_system_metrics_sampling_interval(1)

run_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")


def acceptable_to_str(acceptable):
    return "Правильно" if acceptable else "Неправильно"


def build_prompt(sentence, shots):
    """
    Проверь грамматику предложения. Ответь только "Правильно" или "Неправильно".

    Пример 1:
    Предложение: "Он читает книгу."
    Ответ: Правильно
    Пример 2:
    Предложение: "Он иду в магазин."
    Ответ: Неправильно
    Запрос:
    Предложение: {sentence}
    """
    return f"""Проверь грамматику предложения. Ответь только "Правильно" или "Неправильно".\n
{"\n".join([f"Пример {i + 1}:\nПредложение: \"{shot[0]}\"\nОтвет: {acceptable_to_str(shot[1])}" for i, shot in enumerate(shots)])}
Запрос:
Предложение: {sentence}
"""

train_df = pd.read_csv("./dataset/data/in_domain_train.csv")
dev_df = pd.read_csv("./dataset/data/in_domain_dev.csv")

for i in range(0, 6):
    if i:
        shots = train_df.sample(n=i, random_state=42).apply(lambda x: (x["sentence"], x["acceptable"]),
                                                            axis=1).to_list()
    else:
        shots = []
    run_name = f"{model_name}_{run_timestamp}_shot_{i}"
    with mlflow.start_run(run_name=run_name) as run:
        output_dir = f"./mlruns/{model_name}/{run.info.run_name}_shot_{i}"

        generation_config = GenerationConfig(
            max_new_tokens=5, do_sample=False,
        )

        mlflow.log_params(generation_config.to_dict())
        mlflow.log_params({"shots": shots})

        # Метрика для оценки
        metric = evaluate.load("accuracy")

        labels = []
        predictions = []
        for i, row in tqdm(dev_df.iterrows(), f"Обработка датасета. Примеров: {i}"):
            sentence = row["sentence"]
            acceptable = row["acceptable"]

            tokenized = tokenizer(build_prompt(sentence, shots), return_tensors="pt").to(device)

            output = model.generate(**tokenized, max_new_tokens=5, temperature=0, do_sample=False)

            decoded = tokenizer.decode(output[0][len(tokenized["input_ids"][0]):], skip_special_tokens=True)
            answer = "".join(decoded).strip()

            labels.append(acceptable)
            predictions.append(0 if "неправильно" in answer.lower() or not "правильно" in answer.lower() else 1)

        metric = metric.compute(predictions=predictions, references=labels)
        mlflow.log_metrics(metric)
        print(metric)

# tokenizer.decode(output[0][len(tokenized["input_ids"][0]):], skip_special_tokens=True)
