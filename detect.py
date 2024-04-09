import torch
from datetime import datetime
import subprocess


def tprint(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def run_inference(source):
    command = [
        "python",
        "./yolov7/detect.py",
        "--weights",
        "./runs/train/exp/weights/best.pt",
        "--conf",
        "0.25",
        "--source",
        source
    ]
    subprocess.run(command)

if __name__ == '__main__':
    tprint(f"Runing GPU: {torch.cuda.is_available()}")

    dataset_location = "./ECE189-1"
    tprint(f"Dataset at {dataset_location}")

    tprint(f"Starting Inference")
    source = "./data-storage/tool-video/AdjustableMonkeyWrench.mp4"
    run_inference(source)
    tprint("Finished Inference")