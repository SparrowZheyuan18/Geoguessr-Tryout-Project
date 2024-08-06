# -*- coding: utf-8 -*-Z

from openai import AzureOpenAI
import base64
from configuration import Config


LLM = AzureOpenAI(
    azure_endpoint=Config.MODEL.ENDPOINT,
    api_key=Config.MODEL.OPENAI_API_KEY,
    api_version=Config.MODEL.VERSION,
)

PROMPT = {
    "extracting_sys_prompt":""  
}


def inference_with_img(model, sys_prompt, query, image_path):
    llm = LLM

    def encode_image(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    base64_image = encode_image(image_path)
    url = f"data:image/jpeg;base64,{base64_image}"

    response = llm.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': [{'type': 'text', 'text': sys_prompt}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url
                        }
                    },
                    {
                        "type": "text",
                        "text": query,
                    },
                ],
            },
        ],
        max_tokens=4000
    )

    return response.choices[0].message.content


def inference(model, sys_prompt, query):
    llm = LLM

    response = llm.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': [{'type': 'text', 'text': sys_prompt}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query,
                    },
                ],
            },
        ],
        max_tokens=4000
    )

    return response.choices[0].message.content


if __name__ == '__main__':
    model = 'gpt-4-vision-preview'
    sys_prompt = 'The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.'
    query = 'Give me some visual clues that can determine the location of this image.'
    image_path = 'data/test.jpg'

    print(inference_with_img(model, sys_prompt, query, image_path))
    print(inference(model, sys_prompt, query))