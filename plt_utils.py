import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap

colormaps = ['PuRd_r', 'Blues_r', 'Purples_r', 'winter_r']


def show_image(image, mask=None, title=None, gray_color=False):
    if gray_color:
        plt.imshow(image, cmap='gray')
    else:
        plt.imshow(image)
    plt.axis('off')
    plt.tight_layout()

    if mask is not None:
        if len(mask) == 4:
            for i, m in enumerate(mask):
                if m.any():
                    plt.imshow(m, alpha=0.25, cmap=colormaps[i])
        else:
            plt.imshow(mask, alpha=0.25, cmap=colormaps[0])

    if title:
        plt.title(title)

    plt.show()
