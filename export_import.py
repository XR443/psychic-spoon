import sys
from pathlib import Path

import mlflow
import torch


def import_model(model_type, model_name):
    torch.serialization.add_safe_globals([model_type])
    model_path = Path(f"./models/{model_name}.pt")
    if model_path.exists():
        return torch.load(model_path, weights_only=False)
    return mlflow.pytorch.load_model(f"models:/{model_name}/latest")


def export_model(model_type):
    model_dir = Path('./models')
    model_dir.mkdir(parents=True, exist_ok=True)
    model = mlflow.pytorch.load_model(f"models:/{model_type}/latest")
    torch.save(model, model_dir.joinpath(f'{model_type}.pt'))


if __name__ == "__main__":
    model_type = sys.argv[1] if len(sys.argv) > 1 else "Image2Caption"
    export_model(model_type)
