# Install and import OpenAI Python library

import openai

# Parameters
openai.api_type = "azure"
openai.api_base = "https://hkust.azure-api.net"
openai.api_version = "2023-05-15"
openai.api_key = "20e886f69a934a398438a44de9a34140" #put your api key here

# Function
def get_response(message, instruction):
    response = openai.ChatCompletion.create(
        engine = 'gpt-35-turbo',
        temperature = 1,
        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": message}
        ]
    )
    
    # print token usage
    print(response.usage)
    print(response)
    # return the response
    return response.choices[0]["message"]["content"]

get_response("What is the capital of France?", "You are a helpful assistant that answers questions about geography.")