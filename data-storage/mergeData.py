import os
import shutil
import argparse


def move_folder_content(source, destination):
    try:
        for item in os.listdir(source):
            source_item_path = os.path.join(source, item)
            destination_item_path = os.path.join(destination, item)

            # If it's a file, copy it to the destination folder
            if os.path.isfile(source_item_path):
                shutil.copy2(source_item_path, destination_item_path)
                # print(f"Copied file: {item}")

        print("Copying completed.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":

    print("Fetching folder structure")
    parser = argparse.ArgumentParser()
    parser.add_argument('--o', type=str, help='output folder', default="data")
    parser.add_argument('--i', type=str, help='intput folder', default="data")
    args = parser.parse_args()
    output_data_folder = args.o
    input_data_folder = args.i

    # get list of datasets
    dataset_paths = [os.path.join(input_data_folder, item) for item in os.listdir(input_data_folder) if os.path.isdir(os.path.join(input_data_folder, item)) and item != "obj_train_data" and item != "base" and item != "fewshot"]
    # dataset_paths = [os.path.join(input_data_folder, "robo_hand")]

    output_data_folder = os.path.join(output_data_folder, "obj_train_data")
    if not os.path.exists(output_data_folder):
        os.makedirs(output_data_folder)
    
    train_folder = os.path.join(output_data_folder, 'train')
    test_folder = os.path.join(output_data_folder, 'test')
    valid_folder = os.path.join(output_data_folder, 'valid')
    for folder in [train_folder, test_folder, valid_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            os.makedirs(os.path.join(folder, 'images'))
            os.makedirs(os.path.join(folder, 'labels'))

    # migrate all datasets into large train/test/valid folders
    fns = ['train', 'test', 'valid']
    sfns = ['images', 'labels']
    for dataset_path in dataset_paths:
        print(f"Working on {dataset_path}")
        dataset_path = os.path.join(dataset_path, "obj_train_data")
        for fn in fns:
            for sfn in sfns:
                # move content
                move_folder_content(os.path.join(dataset_path, fn, sfn), os.path.join(output_data_folder, fn, sfn))
