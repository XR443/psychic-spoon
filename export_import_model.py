import sys
from pathlib import Path

import mlflow
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


def import_model(model_type, device="cuda"):
    if Path(f"./models/{model_type}").exists():
        return pipeline(task="text-classification",
                        model=AutoModelForSequenceClassification.from_pretrained(Path(f"./models/{model_type}/model")),
                        tokenizer=AutoTokenizer.from_pretrained(Path(f"./models/{model_type}/tokenizer")),
                        device=device)
    model = mlflow.transformers.load_model(f"models:/{model_type}/latest", return_type="components")
    return pipeline(task="text-classification", model=model["model"], tokenizer=model["tokenizer"], device=device)


def export_model(model_type):
    model_dir = Path('./models')
    model_dir.mkdir(parents=True, exist_ok=True)
    model = mlflow.transformers.load_model(f"models:/{model_type}/latest", return_type="components")

    model["model"].save_pretrained(model_dir.joinpath(f'{model_type}/model'))
    model["tokenizer"].save_pretrained(model_dir.joinpath(f'{model_type}/tokenizer'))


if __name__ == "__main__":
    model_type = sys.argv[1] if len(sys.argv) > 1 else None
    if not model_type:
        for model_type in ["ai-forever-ruBert-base", "ai-forever-ruT5-base"]:
            export_model(model_type)
    else:
        export_model(model_type)
