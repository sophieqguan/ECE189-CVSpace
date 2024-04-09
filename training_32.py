import torch
from datetime import datetime
import subprocess


def tprint(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def train(dataset_location, gpu):
    command = [
        "python",
        "./yolov7/train.py",
        "--batch",
        "32",
        "--epochs",
        "100",
        f"--data",
        f"{dataset_location}/data.yaml",
        "--weights",
        "./yolov7/yolov7-tiny.pt",
        "--hyp",
        "./yolov7/data/hyp.scratch.custom.yaml",
        "--name",
        "All_Tiny_32"]
    if gpu:
        command.append('--device')
        command.append('0')

    subprocess.run(command)


if __name__ == '__main__':
    gpu = torch.cuda.is_available()
    tprint(f"Runing GPU: {gpu}")

    dataset_location = "./data-storage/data/obj_train_data"
    tprint(f"Dataset at {dataset_location}")

    tprint(f"Starting Training")
    train(dataset_location, gpu)
    tprint("Finished Training")

    tprint("You can view the output results at ./yolov7/runs/detect/[run]/")




