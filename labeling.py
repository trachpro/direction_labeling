import cv2
import numpy as np
import os
import argparse
import json

argparser = argparse.ArgumentParser(
    description='Image Segmentation Labeling too')

argparser.add_argument(
    '-i',
    '--images', default="/home/tupm/projects/cds_segment/images",
    help='image folder')

argparser.add_argument(
    '-l',
    '--labels', default="/home/tupm/projects/cds_segment/mask",
    help='image label folder')

args = argparser.parse_args()

# global variables
const_h = 450
img_index = 0
point = None

current_image = None
current_image_name = ''
file_path = ''
image_folder = args.images
label_folder = args.labels

images = [os.path.join(image_folder, e) for e in os.listdir(image_folder)]

print('d: next')
print('a: previous')


def read_image():
    global current_image, file_path
    org_image = cv2.imread(file_path)
    h, w, _ = org_image.shape
    current_image = np.zeros((h, w * 2, 3), np.uint8)
    current_image[:, int(w / 2): int(1.5 * w), :] = org_image
    cv2.line(current_image, (0, const_h), (current_image.shape[1], const_h), (0, 255, 0), 4)
    cv2.line(current_image, (w, 0), (w, h), (0, 255, 0), 4)
    return current_image


def click_and_draw(event, x, y, flags, prarms):
    global point

    if event == cv2.EVENT_LBUTTONDOWN:
        point = (x, const_h)
        draw_point()


def calculate_ratio():
    global current_image, point
    h, w, _ = current_image.shape
    x, y = point
    center = w // 2
    ratio = x / center - 1
    return ratio  # range(-1,1)


def recover_from_ratio(ratio):
    global current_image
    h, w, _ = current_image.shape
    center = w // 2
    x = int((ratio + 1) * center)
    return x


def draw_point():
    global current_image, point
    if not point:
        return
    read_image()
    cv2.circle(current_image, point, 3, (255, 0, 0), 3)
    cv2.imshow('image', current_image)


def load_point():
    global label_folder, current_image_name, point
    if current_image_name+'.json' in os.listdir(label_folder):
        json_file = os.path.join(label_folder, current_image_name + '.json')
        with open(json_file, 'r') as outfile:
            ratio = json.load(outfile)
            x = recover_from_ratio(ratio)
            point = (x, const_h)


def save():
    global point
    if not point:
        return

    json_file = os.path.join(label_folder, current_image_name+'.json')

    with open(json_file, 'w+') as outfile:

        json.dump(calculate_ratio(), outfile)
    point = None


cv2.namedWindow("image", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("image", click_and_draw)

file_path = images[img_index]
current_image_name = os.path.basename(file_path).split('.')[0]

cv2.imshow('image', read_image())
load_point()
draw_point()

while 0 <= img_index < len(images):

    k = cv2.waitKey(0)

    if k in [113, 27]:
        break
    elif ord('d') == k:
        save()
        img_index += 1
        file_path = images[img_index]
        current_image_name = os.path.basename(images[img_index]).split('.')[0]
        read_image()
        load_point()

    elif ord('a') == k:
        img_index -= 1
        file_path = images[img_index]
        current_image_name = os.path.basename(images[img_index]).split('.')[0]
        read_image()
        load_point()

    cv2.imshow('image', current_image)
    draw_point()
