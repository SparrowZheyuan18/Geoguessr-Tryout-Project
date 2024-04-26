import json
import base64
import math
from tqdm import tqdm
from configuration import LLM


data_path = "data/processed_data.jsonl"
inference_path = "experiments/gpt4v_inference.jsonl"
inference_with_reasoning_path = "experiments/gpt4v_inference_with_reasoning.jsonl"

initial_prompt = "depends on the details in this image, please determine where it is. You don't have to be exactly correct, just make a guess. Return me only a location, with format like [lat, lng]."


def encode_image(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')
    

def dump_jsonl(objects, file_name):
    out_file = open(file_name, "w")
    for obj in objects:
        tmp = out_file.write(json.dumps(obj, ensure_ascii=False) + "\n")
        out_file.flush()


def call_gpt(model, prompt, visual=False, url=None):
    if visual:
        response = LLM.chat.completions.create(
            model=model,
            messages=[
                {'role': 'user', 'content': [{'type': 'text', 'text': prompt}, {'type': 'image_url', 'image_url': {"url": url}}]}
            ]
        )
        return response
    response = LLM.chat.completions.create(
        model=model,
        messages=[
            {'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}
        ]
    )
    return response  


def load_data(path):
    with open(path, 'r') as f:
        data = [json.loads(line) for line in f]
    return data


def inference(with_reasoning=False):
    data = load_data(data_path)
    data = [row for row in data if row["is_correct"]]
    for item in tqdm(data):
        answer = item["location"]
        reasoning = item["paraphrased_transcript"]
        model = "gpt-4-vision-preview"
        base64_image = encode_image(f'data/{item["image_path"]}')
        prompt = initial_prompt
        if with_reasoning:
            prompt = f"{reasoning} {prompt}"
        response = call_gpt(model, prompt, visual=True, url=f"data:image/jpeg;base64,{base64_image}")
        guess = response.choices[0].message.content
        yield {
            "reasoning": reasoning,
            "answer": answer,
            "guess": guess,
            "reasoning": reasoning,
            "model": model,
            "image_path": item["image_path"]
        }


def haversine_distance(guess, answer):
    '''
    guess and answer are both:
    [lat, lng]
    '''
    lat1, lon1 = guess
    lat2, lon2 = answer
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * (math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance


def parse_guess(guess):
    guess = guess.replace("[", "").replace("]", "").split(",")
    return [float(guess[0]), float(guess[1])]


def evaluation():
    data = load_data(inference_with_reasoning_path)
    total_distance = 0
    for item in tqdm(data):
        guess = parse_guess(item["guess"])
        answer = item["answer"]
        reasoning = item["reasoning"]
        model = item["model"]
        image_path = item["image_path"]
        distance = haversine_distance(guess, [answer["lat"], answer["lng"]])
        total_distance += distance
        yield {
            "haversine_distance": distance,
            "guess": guess,
            "answer": answer,
            "reasoning": reasoning,
            "model": model,
            "image_path": image_path
        }
    print(f"Average distance: {total_distance / len(data)}")


if __name__ == "__main__":
    dump_jsonl(inference(), inference_path)
    dump_jsonl(evaluation(), "experiments/gpt4v_inference_evaluated.jsonl")
    dump_jsonl(inference(with_reasoning=True), inference_with_reasoning_path)
    dump_jsonl(evaluation(), "experiments/gpt4v_inference_with_reasoning_evaluated.jsonl")
