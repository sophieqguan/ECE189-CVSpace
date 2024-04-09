import cv2
import os
import shutil
import sys
import yaml
import random
import numpy as np
import glob


def video_to_frames(input_video, k_shot=50):
    # Open the video file
    video_capture = cv2.VideoCapture(input_video)
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    # print(f"Video FPS: {fps}")
    print(f"Total Frames: {total_frames}")

    pick = np.linspace(0, total_frames, k_shot, dtype=int)
    print(f"picks: {pick}")
    frames = {}
    for frame_number in range(total_frames):
        ret, frame = video_capture.read()
        
        # taking a total of 50 frames
        if frame_number in pick:
            frames[frame_number] = frame

        if frame_number % 100 == 0:
            sys.stdout.write(f"\rProcessed {frame_number}/{total_frames} frames")
            sys.stdout.flush()

    video_capture.release()

    print("\nFrames extraction complete.")
    return frames


def get_video_path(job_id):
    with open('job_mapping.txt', 'r') as file:
        for line in file:
            i, vp = line.strip().split()
            if i == job_id:
                return vp
    return ""


def shot(job_id, frames, input_labels_folder, output_folder):
    prefix = job_id

    # Create train and valid folders if they don't exist
    train_folder = os.path.join(output_folder, 'train')
    valid_folder = os.path.join(output_folder, 'valid')

    for folder in [train_folder, valid_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            os.makedirs(os.path.join(folder, 'images'))
            os.makedirs(os.path.join(folder, 'labels'))

    total_frames = len(frames)
    train_frames = int(50 * 0.8)
    print(f"Reduced Total Frames: {50}")
    print(f"Training: {train_frames}\Validation: {50 * 0.2}")


    order = list(frames.keys())
    random.shuffle(order)
    print("Shuffled")

    # Loop through each frame and save it as an image
    for cnt, idx in enumerate(order):
        frame = frames[idx]

        if cnt <= train_frames:
            folder = train_folder
        elif cnt:
            folder = valid_folder

        # Save the frame as an images with six digits in the filename
        image_filename = os.path.join(folder, "images", f"{prefix}_{idx:06d}.jpg")
        cv2.imwrite(image_filename, frame)

        # Get the corresponding text file
        text_filename = os.path.join(input_labels_folder, f"frame_{idx:06d}.txt")

        # Save the text file to the 'label' subfolder
        label_filename = os.path.join(folder, "labels", f"{prefix}_{idx:06d}.txt")
        shutil.copy(text_filename, label_filename)

        # Print progress
        if cnt % 5 == 0:
            print(image_filename)
            sys.stdout.write(f"\rProcessed {cnt}/{len(order)} frames")
            sys.stdout.flush()

    # Release the video capture object
    print("\nFrames split complete.")


def hand_50(output_path="50-shot-dataset/robo_hand/obj_train_data", k_shot=50):
    train_folder = os.path.join(output_path, 'train')
    valid_folder = os.path.join(output_path, 'valid')

    for folder in [train_folder, valid_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            os.makedirs(os.path.join(folder, 'images'))
            os.makedirs(os.path.join(folder, 'labels'))

    # get all files (png, txt)
    hands_data_path = "./data/robo_hand/obj_train_data"
    paths = glob.glob(f"{hands_data_path}/**/*", recursive=True)
    files = [path for path in paths if os.path.isfile(path) and os.path.splitext(path)[-1] != ".yaml" ]
    # sort, so that imgs and their corresponding txt are together
    files.sort(key=lambda x: os.path.splitext(os.path.basename(x).split("/")[-1])[:-1][0])
    # get randomly 50 evenly spaced out across all. This is bound to not get consecutive images (same background)
    n = len(files) // 2
    pick = np.multiply(np.linspace(0, n // 2 - 2, k_shot, dtype=int), 2)
    print(f"len: {n}")
    print(pick)

    train_frames = int(50 * 0.8)
    print(f"Reduced Total Frames: {50}")
    print(f"Training: {train_frames}\Validation: {50 * 0.2}")
    
    # Loop through each frame and save it as an image
    for cnt, idx in enumerate(pick):
        if cnt <= train_frames:
            folder = train_folder
        elif cnt:
            folder = valid_folder

        frame_id = 2 * idx
        print(f"frame_id: {frame_id}")
        image_path = files[frame_id]
        label_path = files[frame_id + 1]
        
        def get_ext(path):
            return os.path.splitext(os.path.basename(path).split("/")[-1])[-1]

        if get_ext(label_path) != ".txt" and get_ext(label_path) != "txt": 
            print(f"WRONG EXTENSION: expected 'TXT' but was {get_ext(label_path)}")
            print(f"label: {label_path}")
            exit(1)
        if get_ext(image_path) != ".jpg" and get_ext(image_path) != "jpg": 
            print(f"WRONG EXTENSION: expected 'JPG' but was {get_ext(image_path)}")
            print(f"img: {image_path}")
            exit(1)

        name = os.path.splitext(os.path.basename(image_path).split("/")[-1])[:-1][0]

        # Save the frame as its name
        save_image_path = os.path.join(folder, "images", f"{name}.jpg")
        shutil.copy(image_path, save_image_path)

        # Save the text file to the 'label' subfolder
        save_label_path = os.path.join(folder, "labels", f"{name}.txt")
        shutil.copy(label_path, save_label_path)

        # Print progress
        if cnt % 100 == 0:
            sys.stdout.write(f"\rProcessed {cnt}")
            sys.stdout.flush()

    # Release the video capture object
    print("\nHand frames split complete.")


def cvat_tools(jobids, k_shot=50):
    for class_name, job_id in jobids.items():
        print(f"\n{class_name} [{job_id}] ==================================== ")
        video_path = get_video_path(job_id)
        if video_path == "":
            print(f"Invalid Job ID {job_id}")
            sys.exit(1)

        input_labels_folder_path = f"annotations/{job_id}/obj_train_data"
        output_folder_path = f"50-shot-dataset/{job_id}/obj_train_data"

        # create folder + images to frames
        frames = video_to_frames(video_path, k_shot=k_shot)
        shot(job_id, frames, input_labels_folder_path, output_folder_path)

def find_dupes():
    hands_data_path = "./data/robo_hand/obj_train_data"
    paths = glob.glob(f"{hands_data_path}/**/*", recursive=True)
    files = [path for path in paths if os.path.isfile(path) and os.path.splitext(path)[-1] != ".yaml" ]
    print(len(files))
    files.sort(key=lambda x: os.path.splitext(os.path.basename(x).split("/")[-1])[:-1][0])
    dupes = set()
    for i, x in enumerate(files):
        if i % 1000 == 0: print(i)
        name = os.path.splitext(os.path.basename(x).split("/")[-1])[:-1][0]
        if name in dupes:
            dupes.remove(name)
        else:
            dupes.add(name)
    
    return dupes
    

if __name__ == "__main__":
    # TAKE 50 SHOTS
    k_shot = 50
    jobids = {
        "adjustable monkey wrench": "632875",
        "monkey wrench": "632959",
        "allen key": "632859", 
        "double-flats wrench": "632955",
        "pedal lockring wrench": "632963",
        "crank remover": "632964"
    }
    cvat_tools(jobids)
    # hand_50()
    # print(find_dupes())
