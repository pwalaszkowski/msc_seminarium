import configparser
import json
import os
import requests
import shutil
import bleu
import rouge

from fpdf import FPDF
from datetime import datetime


class Config:
    """
    Base configuration class to load settings from config.ini.
    """

    def __init__(self, config_file='config.ini', environment='DEFAULT'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Load DEFAULT or specified environment settings
        self.env = self.config[environment]

    @property
    def MODEL(self):
        return self.env.get('MODEL', fallback='Model')

    def PROMPT(self):
        return self.env.get('PROMPT', fallback='Prompt')

    def MODEL_PATH(self):
        return self.env.get('MODEL_PATH', fallback='Model_Path')


class LMStudio:
    """
    A class to manage interactions with LM Studio via API and CLI.
    """
    def __init__(self, base_url='http://localhost:8080/v1/chat/completions'):
        self.base_url = base_url

    def send_message(self, input_text, system_message, model='local-model', temperature=0.7):
        """
        Sends a message to the LM Studio API and retrieves the response.

        :param input_text: User's input text
        :param system_message: System context message
        :param model: Model name
        :param temperature: Creativity level
        :return: Model's response as a string
        """
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': input_text}
            ],
            'temperature': temperature
        }

        try:
            response = requests.post(self.base_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content', 'No response received.').strip()
        except requests.exceptions.RequestException as e:
            print(f'Error during API call: {e}')
            return 'An error occurred while communicating with the model.'

    @staticmethod
    def run_cli_command(command):
        """
        Runs a CLI command for LM Studio.

        :param command: CLI command to execute
        :return: Return code of the command
        """
        rc = os.system(command)
        if rc != 0:
            raise Exception(f'Command failed with exit code {rc}')
        return rc

    def start_server(self):
        return self.run_cli_command('lms server start')

    def stop_server(self):
        return self.run_cli_command('lms server stop')

    def check_server_status(self):
        return self.run_cli_command('lms server status')

    def download_model(self, model_name):
        return self.run_cli_command(f'lms get {model_name}')

    def load_model(self, model_name):
        return self.run_cli_command(f'lms load {model_name}')

    def eject_model(self, model_name):
        return self.run_cli_command(f'lms unload {model_name}')

    @staticmethod
    def clear_directory(directory_path):
        """
        Clears the contents of a directory.

        :param directory_path: Path to the directory to be cleared
        """
        try:
            shutil.rmtree(directory_path, ignore_errors=True)
            os.makedirs(directory_path, exist_ok=True)
            print(f'Cleared contents of the directory: {directory_path}')
        except Exception as e:
            print(f'Error while clearing directory: {e}')

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
            print(f'Error checking directory: {e}')
            return False


def read_file_content(file_path):
    """
    Reads and returns the content of a file.

    :param file_path: Path to the file
    :return: Content of the file as a string
    """
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f'File not found: {file_path}')
        return None

def txt_to_pdf(txt_file, pdf_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)

    # Open the text file and add its content to the PDF
    with open(txt_file, 'r') as file:
        for line in file:
            pdf.multi_cell(120, 10, txt=line.strip())

    # Save the PDF
    pdf.output(pdf_file)
    print(f'PDF saved as: {pdf_file}')

def main():
    """
    Main function to manage dynamic conversations with LM Studio.
    """
    environment = 'DEFAULT'  # or 'testing', 'production'
    config = Config(environment=environment)

    lm_studio = LMStudio()

    # Start the server and load the model
    lm_studio.start_server()
    lm_studio.check_server_status()

    lm_studio.download_model(config.MODEL)
    lm_studio.load_model(config.MODEL)

    # Read system message from a file
    system_message = read_file_content('system_message.txt')
    if system_message is None:
        print('System message file is missing.')
        return

    # Ask a question

    model_response = lm_studio.send_message(config.PROMPT(), system_message)
    print(f'Model: {model_response}')

    # Generate timestamp and output file name
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    file_name = f'{config.MODEL.replace('/','_')}_{timestamp}'

    # Save output from model to txt file
    with open(os.path.join('output', file_name), 'w') as file:
        file.write(model_response)

    print(f'Model output has been saved to {file_name}.')

    # Convert txt to pdf
    pdf_file_path = os.path.join('output', f'{file_name}.pdf')
    txt_to_pdf(os.path.join('output', file_name), pdf_file_path)

    # Clean up: Unload the model and stop the server
    lm_studio.eject_model(config.MODEL)
    lm_studio.stop_server()

    # Optional: Clear downloaded models
    model_directory = config.MODEL_PATH().replace('\\', '/')

    lm_studio.clear_directory(model_directory)
    if lm_studio.is_directory_empty(model_directory):
        print('Model directory is successfully cleared.')
    else:
        print('Model directory is not empty.')

    print('Running BLEU calculation')
    bleu.bleu_calculation(pdf_file_path)

    print('Running ROUGE calculation')
    rouge.rouge_calculation(pdf_file_path)

if __name__ == '__main__':
    main()
