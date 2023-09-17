TOKEN: str = ""

from django.conf import settings
import os
import openai
import tiktoken

openai.organization = "org-8yzZe9BYEPIKAPLq9PIXoWHK"
openai.api_key = settings.OPENAI_API_KEY

MODEL: str = "gpt-3.5-turbo"
ENCODING: str = "cl100k_base"

def chat_to_gpt3(chat: str,
                 model_name: str = MODEL):
    chat_completion = openai.ChatCompletion.create(
        max_tokens = 120,
        model=model_name, 
        messages=[
            {"role": "user", "content": chat}
        ]
    )
    if len(chat_completion.choices) > 0:
        return chat_completion.choices[0].message.content
    else:
        return None


def num_tokens_from_string(string: str, 
                           encoding_name: str = ENCODING, 
                           model_name: str = MODEL) -> int:
    if encoding_name:
        encoding = tiktoken.get_encoding(encoding_name)
    elif model_name:
        encoding = tiktoken.encoding_for_model(model_name)
    else:
        raise ValueError("Must specify either encoding_name or model_name")
    
    num_tokens = len(encoding.encode(string))
    return num_tokens

print(num_tokens_from_string("Hello, world!"))