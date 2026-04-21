from model_utils import save_and_pad_image, get_images


def print_min_max_sizes(images):
    sizes = dict()
    for image in images:
        if image.shape in sizes:
            sizes[image.shape] += 1
        else:
            sizes[image.shape] = 1

    sorted_sizes = sorted(list(sizes.keys()), key=lambda x: (x[0], x[1]))
    print("Наименьший размер изображения изображение:", sorted_sizes[0])
    print("Наибольший размер изображения изображение:", sorted_sizes[-1])


images = get_images()
print_min_max_sizes(images.values())

target_folder = "./dataset/flickr30k_images_resized/"
for name, image in images.items():
    save_and_pad_image(target_folder, name, image)

print_min_max_sizes(get_images(folder_path=target_folder).values())
