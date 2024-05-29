import cv2
import os
import shutil
import sys
import yaml
import random
import argparse


def video_to_frames(input_video, frame_reduct=9):
    # Open the video file
    print(input_video)
    video_capture = cv2.VideoCapture(input_video)
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video FPS: {fps}")
    print(f"Total Frames: {total_frames}")

    frames = {}
    for frame_number in range(total_frames):
        ret, frame = video_capture.read()
        
        # taking every f-th frame
        if frame_number % frame_reduct == 0:
            frames[frame_number] = frame

        if frame_number % 100 == 0:
            sys.stdout.write(f"\rProcessed {frame_number}/{total_frames} frames")
            sys.stdout.flush()

    video_capture.release()

    print("\nFrames extraction complete.")
    return frames


def train_test_split(job_id, frames, labels_folder, output_folder, train_ratio=0.8, test_ratio=0.1):
    prefix = job_id

    # Create train, test, and valid folders if they don't exist
    train_folder = os.path.join(output_folder, 'train')
    test_folder = os.path.join(output_folder, 'test')
    valid_folder = os.path.join(output_folder, 'valid')

    for folder in [train_folder, test_folder, valid_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            os.makedirs(os.path.join(folder, 'images'))
            os.makedirs(os.path.join(folder, 'labels'))

    total_frames = len(frames)
    train_frames = int(total_frames * train_ratio)
    test_frames = int(total_frames * test_ratio)
    print(f"Reduced Total Frames: {total_frames}")
    print(f"Training: {train_frames}\nTesting: {test_frames}")

    order = list(frames.keys())
    random.shuffle(order)
    print("Shuffled")

    # Loop through each frame and save it as an image
    for cnt, idx in enumerate(order):
        frame = frames[idx]
        
        if cnt < train_frames:
            folder = train_folder
        elif cnt < train_frames + test_frames:
            folder = test_folder
        else:
            folder = valid_folder

        # Save the frame as an images with six digits in the filename
        image_filename = os.path.join(folder, 'images', f"{prefix}_{idx:06d}.jpg")
        cv2.imwrite(image_filename, frame)

        # Get the corresponding text file
        text_filename = os.path.join(labels_folder, f"frame_{idx:06d}.txt")

        # Save the text file to the 'label' subfolder
        label_filename = os.path.join(folder, 'labels', f"{prefix}_{idx:06d}.txt")
        shutil.copy(text_filename, label_filename)

        # Print progress
        if cnt % 100 == 0:
            sys.stdout.write(f"\rProcessed {cnt}/{total_frames} frames")
            sys.stdout.flush()

    # Release the video capture object
    print("\nFrames split complete.")


def get_video_path(job_id):
    with open('job_mapping.txt', 'r') as file:
        for line in file:
            i, vp = line.strip().split()
            if i == job_id:
                return vp
    return ""


if __name__ == "__main__":
    """
    1. compile a set of annotation + tool-video into train-test-val split
    2. save it to /data under a new folder for that tool-video
    """

    # usage: python convertData.py -j <job_id> -f <frame reduction rate>

    parser = argparse.ArgumentParser()
    parser.add_argument('--f', type=int, help='take every f-th frame', default=9)
    parser.add_argument('--j', type=str, help='tool video id')
    parser.add_argument('--o', type=str, help='output location')
    args = parser.parse_args()

    job_id = args.j
    video_path = get_video_path(job_id)
    if video_path == "":
        print(f"Invalid Job ID {job_id}")
        sys.exit(1)

    labels_folder_path = f"annotations/{job_id}/obj_train_data"
    output_folder_path = f"{args.o}/{job_id}/obj_train_data"

    # create folder + images to frames
    frames = video_to_frames(video_path, frame_reduct=args.f)
    train_test_split(job_id, frames, labels_folder_path, output_folder_path)

    # generate data.yaml file
    classes = []
    with open(f'annotations/{job_id}/obj.names', 'r') as file:
        classes = [line.strip() for line in file]

    data = {
        'train': '../train/images',
        'val': '../valid/images',
        'test': '../test/images',
        'nc': len(classes),
        'names': classes
    }

    with open(f'{output_folder_path}/data.yaml', 'w') as yaml_file:
        yaml.safe_dump(data, yaml_file, default_style='', default_flow_style=False, sort_keys=False)
    print("YAML file 'data.yaml' created successfully.")