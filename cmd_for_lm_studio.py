import json
import os
import requests
import shutil

# Configuration for LM Studio API
class LMStudioConfig:
    def __init__(self):
        self.base_url = "http://localhost:8080/v1/chat/completions"


def read_file_content(file_path):
    """
    Reading a txt file from file_path, this is a welcome message
    - file_path: file to be read.

    Returns:
    - None
    """
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


def initiate_conversation(input_text, system_message, config):
    """
    Function to send a conversation request to LM Studio
    :param input_text:
    :param system_message:
    :param config:
    Returns:
    -
    """
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

def server_start():
    """
    Wrapper function for LM Studio CLI to start server
    Returns:
    - return code
    """
    rc = os.system("lms server start")
    if rc != 0:
        raise Exception(f"Command failed with exit code {rc}")
    return rc


def server_stop():
    """
    Wrapper function for LM Studio CLI to stop server
    Returns:
    - return code
    """
    rc = os.system("lms server stop")
    if rc != 0:
        raise Exception(f"Command failed with exit code {rc}")
    return rc


def server_status():
    """
    Wrapper function for LM Studio CLI to check server status
    - return code
    """
    rc = os.system("lms server status")
    if rc != 0:
        raise Exception(f"Command failed with exit code {rc}")
    return rc


def download_model(model_name):
    """
    Wrapper function for LM Studio CLI to download model
    - model_name: LLM to be downloaded.
    - return code
    """
    rc = os.system(f"lms get {model_name}")
    if rc != 0:
        raise Exception(f"Command failed with exit code {rc}")
    return rc


def load_model(model_name):
    """
    Wrapper function for LM Studio CLI to load model
    - model_name: LLM to be loaded.
    - return code
    """
    rc = os.system(f"lms load {model_name}")
    if rc != 0:
        raise Exception(f"Command failed with exit code {rc}")
    return rc


def eject_model(model_name):
    """
    Wrapper function for LM Studio CLI to eject model
    - model_name: LLM to be ejected.
    - return code
    """
    rc = os.system(f"lms unload {model_name}")
    if rc != 0:
        raise Exception(f"Command failed with exit code {rc}")
    return rc

def remove_downloaded_models(directory_path):
    """
    Removes all contents of a directory by deleting and recreating it.

    Parameters:
    - directory_path: Path to the directory to be cleared.

    Returns:
    - None
    """
    try:
        # Delete the entire directory and its contents
        shutil.rmtree(directory_path, ignore_errors=True)
        # Recreate the empty directory
        os.makedirs(directory_path, exist_ok=True)
        print(f"Cleared all contents of the directory: {directory_path}")
    except Exception as e:
        print(f"Error while clearing directory: {e}")


def main():
    """
    Main Function
    """
    config = LMStudioConfig()
    server_start()
    server_status()
    download_model("qwen2-0.5b-instruct")
    load_model("qwen2-0.5b-instruct")

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

    eject_model("qwen2-0.5b-instruct")
    server_stop()

    # TODO: Temporary hardcoded path
    base_path = r"C:\Users\pwala"
    sub_path = ".cache"
    sub_sub_path = "lm-studio"
    final_folder = "models"
    full_path = os.path.join(base_path, sub_path, sub_sub_path, final_folder)
    remove_downloaded_models(full_path)

    try:
        # Check if the directory exists
        if not os.path.exists(full_path):
            print(f"Directory does not exist: {full_path}")
            return False

        # Check if the directory is empty
        return not any(os.scandir(full_path))  # Scans for any files or subdirectories
    except Exception as e:
        print(f"Error checking directory: {e}")
        return False


if __name__ == "__main__":
    main()
