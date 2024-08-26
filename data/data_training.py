import json
from tqdm import tqdm
import random

players = ['geocatto', 'geogasm', 'geopeter', 'geowizard', 'zi8gzag', 'rainbolttwo']
base_path = f'clues_1'
prompt = "Your return should be some visual clues based on the input image which can help to determine the actual location of it. Here are two examples of your output format: 1. blue car plate, white people. 2. tropical tree, driving on the right, could be Bankok. Please strictly follow the output format of the clues (where you should not add any other words). Your answer is:"


def load_data(path):
    with open(path, 'r') as f:
        if path.endswith(".jsonl"):
            data = [json.loads(line) for line in f]
        else:
            data = json.load(f)
    return data


def main():
    positive_training_data = []
    negative_training_data = []
    positive_testing_data = []
    negative_testing_data = []
    for player in players:
        n_p = 0
        n_n = 0
        data = load_data(f"{base_path}/evaluated_clues_{player}.jsonl")
        training_num = int(len(data)*9/10)
        # Training set, test set partition: 9:1
        for i, row in enumerate(data):
            clues = row["clues"]
            image_path = "/fs/clip-scratch/zheyuan/Geoguessr-Tryout-Project/" + row["image_path"]
            conversations = [
                {
                    'role': 'user',
                    'content': f'<image>\n{prompt}'
                },
                {
                    'role': 'assistant',
                    'content': f'{clues}'
                }
            ]
            sample = {
                "id": f"{player}{i}",
                "image": image_path,
                "conversations": conversations
            }
            if i <= training_num:
                if row["is_correct"]:
                    positive_training_data.append(sample)
                    n_p += 1
                else:
                    negative_training_data.append(sample)
                    n_n += 1
            else:
                if row["is_correct"]:
                    positive_testing_data.append(sample)
                    n_p += 1
                else:
                    negative_testing_data.append(sample)
                    n_n += 1
        
        print(f"Samples of {player}:\n", f"postive: {n_p}", f"negative: {n_n}")
    
    print("Total training positive:", len(positive_training_data))
    print("Total training negative:", len(negative_training_data))
    print("Total testing positive:", len(positive_testing_data))
    print("Total testing negative:", len(negative_testing_data))

    with open('positive_clues.json', 'w') as json_file:
        json.dump(positive_training_data, json_file)
    
    with open('negative_clues.json', 'w') as json_file:
        json.dump(negative_training_data, json_file)

    with open('positive_test_clues.json', 'w') as json_file:
        json.dump(positive_testing_data, json_file)
    
    with open('negative_test_clues.json', 'w') as json_file:
        json.dump(negative_testing_data, json_file)


def mix_set():
    mix_train_set = []
    mix_test_set = []

    for player in players:
        data = load_data(f"{base_path}/evaluated_clues_{player}.jsonl")
        training_num = int(len(data)*9/10)
        # Training set, test set partition: 9:1
        for i, row in enumerate(data):
            clues = row["clues"]
            image_path = "/fs/clip-scratch/zheyuan/Geoguessr-Tryout-Project/" + row["image_path"]
            conversations = [
                {
                    'role': 'user',
                    'content': f'<image>\n{prompt}'
                },
                {
                    'role': 'assistant',
                    'content': f'{clues}'
                }
            ]
            sample = {
                "id": f"{player}{i}",
                "image": image_path,
                "conversations": conversations
            }
            if i <= training_num:
                mix_train_set.append(sample)         
            else:
                mix_test_set.append(sample)
    
    random.shuffle(mix_train_set)
    random.shuffle(mix_test_set)
    print("Total training:", len(mix_train_set))
    print("Total testing:", len(mix_test_set))

    with open('train_clues.json', 'w') as json_file:
        json.dump(mix_train_set, json_file)
    
    with open('test_clues.json', 'w') as json_file:
        json.dump(mix_test_set, json_file)

if __name__ == '__main__':
    # main()
    mix_set()