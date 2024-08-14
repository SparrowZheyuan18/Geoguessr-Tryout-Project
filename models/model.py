from llm import inference, inference_with_img
import json
from tqdm import tqdm
import re
import math
from retry import retry


test_path = "models/experiments_zi8gzag.jsonl"

class Extractor:
    '''
    Extractor: given an image, extract all useful clues from the image for geo-localization
    '''
    def __init__(self, model="gpt-4-vision-preview"):
        self.model = model

    def call_llm(self, sys_prompt, query, image_path):
        return inference_with_img(self.model, sys_prompt, query, image_path)

    def extract_with_llm(self, image): # use llm to extract clues
        sys_prompt = "You are a master of geography and culture. You can identify the most distinguished visual clues that can determine the location based on an image."
        query = "Please provide some of the visual clues that can mostly determine the location of this image."
        clues = self.call_llm(sys_prompt, query, image)
        return clues
    
    def extract_with_SFT_model(self, image): # use the finetuned model for extraction
        pass

    def extract_with_OCR(self, image):
        pass

    def extract_with_google_lens(self, image):
        pass


class Analyzer:
    '''
    Analyzer: given a list of clues, analyze them and give a proximate guess of the location
    '''
    def __init__(self, model="gpt-4-vision-preview", clues=[]):
        self.clues = clues
        self.model = model

    def call_llm(self, sys_prompt, query, image_path):
        return inference_with_img(self.model, sys_prompt, query, image_path)
    
    def browse_the_internet(self, query):
        pass

    def analyze_with_llm(self, image):
        sys_prompt = ""
        query = ""
        location = self.call_llm(sys_prompt, query, image)
        return location
    

class Validator:
    '''
    Validator: given a list of prediction candidates, find the final answer with the candidates
    '''
    def __init__(self, model="gpt-4-vision-preview", candidates=[], clues=""):
        self.candidates = candidates
        self.clues = clues
        self.model = model

    def use_overpass(self):
        pass

    @retry(tries=3, delay=2)
    def validate_with_llm(self, image):
        sys_prompt = "You are a master of geography and culture. You can determine the exact location (latitude and longitude) based on an image and extra information of it. If you are not sure, you can still make a guess anyway. You return only the answer formed in the format of (latitude, longitude)."
        clues_prompt = f"The visual clues are given below: {self.clues}\n" if self.clues!="" else ""
        query = clues_prompt + "Determine the exact location (latitude and longitude). If you are not sure, try your best to take a guess anyway. You don't have to be exactly correct. Only return a guess in the format of (latitude, longitude)."
        # print(query)
        answer = self.call_llm(sys_prompt, query, image_path=image)
        # print(answer)
        def parse_guess(guess):
            pattern = r'\(([^)]+),\s*([^)]+)\)'
            match = re.search(pattern, guess)
            if match:
                return [float(match.group(1)), float(match.group(2))]
            else:
                raise ValueError("The answer is not in the correct format.")
        
        answer = parse_guess(answer)
        return answer
    def call_llm(self, sys_prompt, query, image_path):
        return inference_with_img(self.model, sys_prompt, query, image_path)



def load_data(path):
    with open(path, 'r') as f:
        if path.endswith(".jsonl"):
            data = [json.loads(line) for line in f]
        else:
            data = json.load(f)
    return data


def dump_jsonl(objects, file_name):
    out_file = open(file_name, "w")
    for obj in objects:
        tmp = out_file.write(json.dumps(obj, ensure_ascii=False) + "\n")
        out_file.flush()


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


def main():
    # extractor = Extractor()
    # clues = extractor.extract_with_llm("data/combined.jpg")
    # print(clues)

    data = load_data("./data/processed_data_zi8gzag.jsonl")
    corrct = 0
    c_count = 0
    incorrect = 0
    i_count = 0

    for i, item in enumerate(tqdm(data[:])):
        print(f"==================start testing {i}====================")
        clues = item["paraphrased_transcript"]
        is_correct = item["is_correct"]
        correct_answer = [item["location"]["lat"], item["location"]["lng"]]
        validator = Validator(clues=clues)
        answer = validator.validate_with_llm(f"{item['image_path']}")
        validator_without_clues = Validator()
        answer_without_clues = validator_without_clues.validate_with_llm(f"{item['image_path']}")

        # def parse_guess(guess):
        #     pattern = r'\(([^)]+),\s*([^)]+)\)'
        #     match = re.search(pattern, guess)
        #     if match:
        #         return [float(match.group(1)), float(match.group(2))]
        #     else:
        #         return None
        
        # answer = parse_guess(answer)
        # answer_without_clues = parse_guess(answer_without_clues)

        distance_with_clues = haversine_distance(answer, correct_answer)
        distance_without_clues = haversine_distance(answer_without_clues, correct_answer)

        performance_gain = distance_without_clues - distance_with_clues

        best_guess = min(distance_with_clues, distance_without_clues)

        print("answer:", answer)
        print("correct_answer:", correct_answer)
        print("clue_is_correct:", is_correct)
        print("answer_without_clues:", answer_without_clues)

        if is_correct:
            c_count += 1
            corrct += performance_gain
        else:
            i_count += 1
            incorrect += performance_gain

        yield {
            "performance_gain": performance_gain,
            "is_correct": is_correct,
            "best_guess": best_guess,
            "clues": clues,
            "correct_answer": correct_answer,
            "answer": answer,
            "answer_without_clues": answer_without_clues
        }

    average_correct = corrct / c_count
    average_incorrect = incorrect / i_count
    print("average_correct:", average_correct)
    print("average_incorrect:", average_incorrect)


def calculate_score():
    data = load_data("experiments_zi8gzag.jsonl")
    corrct = 0
    c_count = 0
    incorrect = 0
    i_count = 0

    for item in data:
        is_correct = item["is_correct"]
        performance_gain = item["performance_gain"]
        if is_correct:
            c_count += 1
            corrct += performance_gain
        else:
            i_count += 1
            incorrect += performance_gain
    
    average_correct = corrct / c_count
    average_incorrect = incorrect / i_count
    print("average_correct:", average_correct)
    print("average_incorrect:", average_incorrect)


if __name__ == '__main__':
    # dump_jsonl(main(), test_path)
    calculate_score()
