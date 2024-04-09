import cv2
import os
import shutil
import sys
import yaml
import random
import numpy as np
import glob


def move_folder_content(source, destination):
    try:
        for item in os.listdir(source):
            source_item_path = os.path.join(source, item)
            if not os.path.isfile(source_item_path):
                print(f"Error: Source file '{source_item_path}' not found.")
                return
                
            destination_item_path = os.path.join(destination, item)
            
            # print(f"\tsource={source_item_path}\n\tdest={destination_item_path}")

            # If it's a file, copy it to the destination folder
            if os.path.isfile(source_item_path):
                shutil.copy(source_item_path, destination_item_path)
                # print(f"Copied file: {item}")

        print("Copying completed.")

    except Exception as e:
        print(f"An error occurred: {e}")


def get_FS_dataset(output_folder, classes):
    print("base + novel")
    dataset_paths = []
    for class_name, folder_name in classes.items():
        p = os.path.join("50-shot-dataset", folder_name)
        dataset_paths.append(p)

    data_folder = os.path.join(output_folder, "obj_train_data")
    if not os.path.exists(data_folder):
            os.makedirs(data_folder)
    train_folder = os.path.join(data_folder, 'train')
    valid_folder = os.path.join(data_folder, 'valid')
    for folder in [train_folder, valid_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            os.makedirs(os.path.join(folder, 'images'))
            os.makedirs(os.path.join(folder, 'labels'))

    fns = ['train', 'valid']
    sfns = ['images', 'labels']
    for dataset_path in dataset_paths:
        print(f"Working on {dataset_path}")
        dataset_path = os.path.join(dataset_path, "obj_train_data")
        for fn in fns:
            for sfn in sfns:
                # move content
                move_folder_content(source=os.path.join(dataset_path, fn, sfn), destination=os.path.join(data_folder, fn, sfn))


def get_base_dataset(output_folder, classes):
    print("base")
    dataset_paths = []
    for class_name, folder_name in classes.items():
        p = os.path.join("data", folder_name, "obj_train_data")
        dataset_paths.append(p)

    data_folder = os.path.join(output_folder, "obj_train_data")
    if not os.path.exists(data_folder):
            os.makedirs(data_folder)
    train_folder = os.path.join(data_folder, 'train')
    test_folder = os.path.join(data_folder, 'test')
    valid_folder = os.path.join(data_folder, 'valid')
    for folder in [train_folder, test_folder, valid_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            os.makedirs(os.path.join(folder, 'images'))
            os.makedirs(os.path.join(folder, 'labels'))

    fns = ['train', 'test', 'valid']
    sfns = ['images', 'labels']
    for dataset_path in dataset_paths:
        print(f"Working on {dataset_path}")
        for fn in fns:
            for sfn in sfns:
                # move content
                move_folder_content(source=os.path.join(dataset_path, fn, sfn), destination=os.path.join(data_folder, fn, sfn))

if __name__ == "__main__":
    base_classes = {
        "adjustable monkey wrench": "632875",
        "adjustable monkey wrench and monkey wrench": "632949",
        "monkey wrench": "632959",
        "hand": "robo_hand",
    }
    novel_classes = {
        "adjustable monkey wrench": "632875",
        "monkey wrench": "632959",
        "hand": "robo_hand",
        "allen key": "632859", 
        "double-flats wrench": "632955",
        "pedal lockring wrench": "632963",
        "crank remover": "632964"
    }

    output_folder_base = "50-shot-dataset/base"
    output_folder_FS = "50-shot-dataset/fewshot"

    get_base_dataset(output_folder_base, base_classes)
    get_FS_dataset(output_folder_FS, novel_classes)