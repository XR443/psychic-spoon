from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns


def visualize(target, predictions, additional_info):
    """
    Рисует график функции

    :param target: целевой тензор, содержит x y z
    :param predictions: содержит предсказанный z по x и y
    :param additional_info: доп информация к графику
    :return:
    """
    fig = plt.figure(figsize=(15, 6))

    cmap = ListedColormap(sns.color_palette("husl", 256).as_hex())

    ax1 = fig.add_subplot(121, projection='3d')
    surf1 = ax1.scatter([x.item() for x, _, _ in target],
                        [y.item() for _, y, _ in target],
                        [z.item() for _, _, z in target],
                        s=20, c=[z.item() for _, _, z in target], marker='o', cmap=cmap, alpha=1)
    ax1.set_title(f'Ожидаемые значения: {additional_info}')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    fig.colorbar(surf1, ax=ax1, shrink=0.5)

    ax2 = fig.add_subplot(122, projection='3d')
    surf2 = ax2.scatter([x.item() for x, _, _ in target],
                        [y.item() for _, y, _ in target],
                        [z.item() for z in predictions],
                        s=20, c=[z.item() for z in predictions], marker='o', cmap=cmap, alpha=1)
    ax2.set_title(f'Фактические значения: {additional_info}')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    fig.colorbar(surf2, ax=ax2, shrink=0.5)

    plt.tight_layout()
    plt.show()