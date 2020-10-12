import os

from PIL import Image


def get_size(file):
    image = Image.open(file)
    return image.size


def resize(file, filename, max_size: ()):
    image = Image.open(file)
    image.thumbnail(max_size)
    size = image.size
    new_name = get_filename_with_size(filename, size)
    return new_name, image


def get_filename_with_size(filename, size):
    base_file, extension = os.path.splitext(filename)
    return f'{base_file}-{size[0]}x{size[1]}{extension}'


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_max_square(pil_img):
    # https://note.nkmk.me/en/python-pillow-image-crop-trimming/
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def make_small_square(file, file_name, wished_side):
    pil_img = Image.open(file)
    cropped = crop_max_square(pil_img)
    result = cropped.resize((150, 150))
    new_name = get_filename_with_size(file_name, (wished_side, wished_side))
    return new_name, result
