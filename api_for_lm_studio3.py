import requests
import json

# Configuration for LM Studio API
class LMStudioConfig:
    def __init__(self):
        self.base_url = "http://localhost:8080/v1/chat/completions"

# Function to read file content
def read_file_content(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

# Function to send a conversation request to LM Studio
def initiate_conversation(input_text, system_message, config):
    payload = {
        "model": "local-model",  # Replace with the correct model name
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": input_text}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(config.base_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")
        return "An error occurred while communicating with the model."

def main():
    # Instantiate configuration
    config = LMStudioConfig()

    # Read system message from file
    system_message = read_file_content("system_message.txt")
    if system_message is None:
        return

    # Conversation loop
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'bye', 'end']:
            print("Exiting the conversation.")
            break

        model_response = initiate_conversation(user_input, system_message, config)
        print("Model Response: ", model_response)

if __name__ == "__main__":
    main()