from datetime import datetime
from functools import partial

import evaluate
import mlflow
import numpy as np
import torch
from transformers import TrainingArguments, Trainer, T5Tokenizer, T5ForSequenceClassification
from transformers.integrations import MLflowCallback

from model_utils import get_dataset, preprocess_examples, get_params

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

########################################################################################################################
model_name = "ai-forever/ruT5-base"

tokenizer = T5Tokenizer.from_pretrained(model_name)

mlflow.set_experiment("NLP Learning Experiment")

mlflow.config.enable_system_metrics_logging()
mlflow.config.set_system_metrics_sampling_interval(1)

dataset, max_length = get_dataset()
dataset = dataset.map(
    partial(preprocess_examples, tokenizer=tokenizer, max_length=max_length),
    batched=True,
    remove_columns=["sentence"],
)

run_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

for i, params in enumerate(get_params()):
    model = T5ForSequenceClassification.from_pretrained(model_name, num_labels=2, cache_dir="./.cache/huggingface")
    model = model.to(device)
    run_name = f"{model_name}_{run_timestamp}_run_{i}"
    with mlflow.start_run(run_name=run_name) as run:
        output_dir = f"./mlruns/{model_name}/{run.info.run_name}"

        training_args = TrainingArguments(
            output_dir=output_dir,
            eval_strategy="epoch",
            save_strategy="epoch",
            do_train=True,
            do_eval=True,
            learning_rate=params["learning_rate"],
            per_device_train_batch_size=params["batch_size"],
            per_device_eval_batch_size=params["batch_size"],
            num_train_epochs=params["num_epochs"],
            weight_decay=params["weight_decay"],
            logging_dir="./logs",
            logging_steps=10,
            # max_steps=100,
            load_best_model_at_end=True,
            save_total_limit=0,
            metric_for_best_model="accuracy"
        )
        # Log training parameters
        training_args_dict = training_args.to_dict()
        training_args_dict["start_params"] = params
        mlflow.log_params(training_args_dict)

        # Метрика для оценки
        metric = evaluate.load("accuracy")


        def compute_metrics(eval_pred):
            logits, labels = eval_pred
            predictions = np.argmax(logits[0], axis=-1)
            return metric.compute(predictions=predictions, references=labels)


        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset["train"],
            eval_dataset=dataset["dev"],
            compute_metrics=compute_metrics,
            callbacks=[MLflowCallback()]
        )

        trainer.train()

        mlflow.log_metrics(trainer.evaluate(dataset["test"], metric_key_prefix="test_eval"))
        transformers_model = {"model": model, "tokenizer": tokenizer}
        model_info = mlflow.transformers.log_model(transformers_model,
                                                   task="text-classification",
                                                   name=f"final_model_{run_name}".replace('/', '-'),
                                                   registered_model_name=model_name.replace('/', '-'))
