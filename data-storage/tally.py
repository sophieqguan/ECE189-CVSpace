import os

def tally_class_counts():
    # iterates through dataset to tally class count
    dataset_path = "./data/obj_train_data"
    nc = 7
    tally = [0 for _ in range(nc)]
    tc = 0
    
    label_paths = [os.path.join(dataset_path, "test/labels"), os.path.join(dataset_path, "train/labels"), os.path.join(dataset_path, "valid/labels")]

    for label_path in label_paths:
        print(f"Entering {label_path}:")
        for filename in os.listdir(label_path):
            if filename.endswith(".txt"):
                tc += 1
                file_path = os.path.join(label_path, filename)
                
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                
                for line in lines:
                    if line.strip():  # check if line is not empty
                        tally[int(line[0])] += 1            # class is 0-indexed
                        if int(line[0]) == 7: 
                            print(file_path)
                    
    return tally, tc

if __name__ == "__main__":
    """
    iterate_and_change('./data/robo_hand/obj_train_data/test/labels')
    iterate_and_change('./data/robo_hand/obj_train_data/train/labels')
    iterate_and_change('./data/robo_hand/obj_train_data/valid/labels')
    """

    # later on might want to do argparse since convert-data.job runs utility.py for tallying after updating dataset
    cn = ["adjustable monkey wrench", "monkey wrench",  "allen key",  "double-flats wrench", "hand", "pedal lockring wrench", "crank remover"]
    tally, tc = tally_class_counts()
    sum = 0
    for c in tally:
        sum += c

    with open("tally.txt", 'w') as tally_file: 
        tally_file.write(f"Total instances: {tc}\n\n")
        for i, c in enumerate(tally):
            print(f"i: {i}")
            print(f"{cn[i]}: {c} instances ({(c / sum) * 100:.2f}%)")
            tally_file.write(f"{cn[i]}: {c} instances\n")






