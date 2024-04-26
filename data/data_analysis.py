import json


def load_data(path):
    with open(path, 'r') as f:
        if path.endswith(".jsonl"):
            data = [json.loads(line) for line in f]
        else:
            data = json.load(f)
    return data


def count_tokens(text):
    return len(text.split(" "))


def main():
    data = load_data("data/full_data.jsonl")
    # calculate the average tokens in the transcript
    total_tokens = 0
    for item in data:
        total_tokens += count_tokens(item['transcript'])
    average_tokens = total_tokens / len(data)
    print(average_tokens)
    processed_data = load_data("data/processed_data.jsonl")
    # calculate the average tokens in the processed transcript
    total_tokens = 0
    total_is_correct = 0
    for item in processed_data:
        total_tokens += count_tokens(item['paraphrased_transcript'])
        if item['is_correct']:
            total_is_correct += 1
    average_processed_tokens = total_tokens / len(processed_data)
    print(average_processed_tokens)
    print(total_is_correct, len(processed_data)-total_is_correct)


if __name__ == "__main__":
    main()