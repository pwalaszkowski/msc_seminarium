import json
import os
import requests
import shutil

class LMStudio:
    """
    A class to manage interactions with LM Studio via API and CLI.
    """
    def __init__(self, base_url="http://localhost:8080/v1/chat/completions"):
        self.base_url = base_url

    def send_message(self, input_text, system_message, model="local-model", temperature=0.7):
        """
        Sends a message to the LM Studio API and retrieves the response.

        :param input_text: User's input text
        :param system_message: System context message
        :param model: Model name
        :param temperature: Creativity level
        :return: Model's response as a string
        """
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": input_text}
            ],
            "temperature": temperature
        }

        try:
            response = requests.post(self.base_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "No response received.").strip()
        except requests.exceptions.RequestException as e:
            print(f"Error during API call: {e}")
            return "An error occurred while communicating with the model."

    @staticmethod
    def run_cli_command(command):
        """
        Runs a CLI command for LM Studio.

        :param command: CLI command to execute
        :return: Return code of the command
        """
        rc = os.system(command)
        if rc != 0:
            raise Exception(f"Command failed with exit code {rc}")
        return rc

    def start_server(self):
        return self.run_cli_command("lms server start")

    def stop_server(self):
        return self.run_cli_command("lms server stop")

    def check_server_status(self):
        return self.run_cli_command("lms server status")

    def download_model(self, model_name):
        return self.run_cli_command(f"lms get {model_name}")

    def load_model(self, model_name):
        return self.run_cli_command(f"lms load {model_name}")

    def eject_model(self, model_name):
        return self.run_cli_command(f"lms unload {model_name}")

    @staticmethod
    def clear_directory(directory_path):
        """
        Clears the contents of a directory.

        :param directory_path: Path to the directory to be cleared
        """
        try:
            shutil.rmtree(directory_path, ignore_errors=True)
            os.makedirs(directory_path, exist_ok=True)
            print(f"Cleared contents of the directory: {directory_path}")
        except Exception as e:
            print(f"Error while clearing directory: {e}")

    @staticmethod
    def is_directory_empty(directory_path):
        """
        Checks if a directory is empty.

        :param directory_path: Path to the directory
        :return: True if the directory is empty, False otherwise
        """
        try:
            return not any(os.scandir(directory_path))
        except Exception as e:
            print(f"Error checking directory: {e}")
            return False


def read_file_content(file_path):
    """
    Reads and returns the content of a file.

    :param file_path: Path to the file
    :return: Content of the file as a string
    """
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

def main():
    """
    Main function to manage dynamic conversations with LM Studio.
    """
    lm_studio = LMStudio()

    # Start the server and load the model
    lm_studio.start_server()
    lm_studio.check_server_status()

    model_name = "qwen2-0.5b-instruct"
    lm_studio.download_model(model_name)
    lm_studio.load_model(model_name)

    # Read system message from a file
    system_message = read_file_content("system_message.txt")
    if system_message is None:
        print("System message file is missing.")
        return

    print("LM Studio is ready for conversation. Type 'exit' to quit.")

    # TODO: Workaround to pass the questions directly to model
    model_response = lm_studio.send_message("Brief Yourself", system_message)
    print(f"Model: {model_response}")

    # # Conversation loop
    # while True:
    #     user_input = input("User: ").strip()
    #     os.system("Brief yourself")
    #     if user_input.lower() in ["exit", "bye", "end"]:
    #         print("Exiting the conversation.")
    #         break
    #
    #     model_response = lm_studio.send_message(user_input, system_message)
    #     print(f"Model: {model_response}")

    # Clean up: Unload the model and stop the server
    lm_studio.eject_model(model_name)
    lm_studio.stop_server()

    # Optional: Clear downloaded models
    # TODO: Temporary hardcoded path
    base_path = r"C:\Users\pwala"
    sub_path = ".cache"
    sub_sub_path = "lm-studio"
    final_folder = "models"
    model_directory = os.path.join(base_path, sub_path, sub_sub_path, final_folder)

    lm_studio.clear_directory(model_directory)
    if lm_studio.is_directory_empty(model_directory):
        print("Model directory is successfully cleared.")
    else:
        print("Model directory is not empty.")

if __name__ == "__main__":
    main()
