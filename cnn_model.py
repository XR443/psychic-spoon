import torch.nn as nn

from sklearn.model_selection import ParameterGrid
from torch.optim import Adam


class EncoderDecoder(nn.Module):
    def __init__(self):
        super(EncoderDecoder, self).__init__()

        self.encoder = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),

            nn.AvgPool2d(kernel_size=3, stride=2, padding=1),

            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),

            nn.AvgPool2d(kernel_size=3, stride=2, padding=1),

            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),

            nn.AvgPool2d(kernel_size=3, stride=2, padding=1),
        )

        self.bottleneck = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=1, stride=1, padding=0),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Dropout2d(0.3),
        )

        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),

            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),

            nn.ConvTranspose2d(32, 4, kernel_size=3, stride=2, padding=1, output_padding=1),
            # nn.Sigmoid(),
        )

    def forward(self, x):
        encoded = self.encoder(x)
        bottleneck = self.bottleneck(encoded)
        decoded = self.decoder(bottleneck)
        return decoded


def build_model_and_optimizer(item, skip_optimizer=False):
    """
    Построение модели и оптимизатора
    :param item: словарь параметров для построения модели
    :param skip_optimizer: флаг необходимости оптимизатора. По умолчанию создается оптимизатор
    :return: model if skip_optimizer else (model, optimizer)
    """
    model = EncoderDecoder(
        # item["hidden_size"],
        # item["activation_1"],
        # item["activation_2"],
        # item["activation_3"],
        # item["dropout"],
        # item["dropout_rate"],
        # item["batch_norm"],
    )

    if skip_optimizer:
        return model

    optimizer = item['optimizer'](model.parameters(), lr=item['learning_rate'])

    return model, optimizer


def get_params():
    """
    Генерирует параметры для кросс-валидации
    :return: словарь параметров
    """
    param_grid = {
        'hidden_size': [2 ** i for i in range(8, 16)],
        # 'hidden_size': [12],
        'num_epochs': [i for i in range(100, 200, 25)],
        # 'num_epochs': [10],
        'learning_rate': [0.01, 0.05, 0.1],
        # 'learning_rate': [0.01],
        'batch_size': [None, *[i for i in range(1000, 3000 + 1, 1000)]],
        # 'optimizer': [Adam, SGD, RMSprop],  # до этого всегда побеждал Адам
        'optimizer': [Adam],
        # 'dropout': [True, False],
        'dropout': [True],
        'dropout_rate': [0.2, 0.25, 0.3],
        # 'batch_norm': [True, False],
        'batch_norm': [True],
    }

    for layer in range(1, 8):
        param_grid[f"activation_{layer}"] = [nn.Tanh, nn.ReLU]

    grid = ParameterGrid(param_grid)

    return list(grid)
