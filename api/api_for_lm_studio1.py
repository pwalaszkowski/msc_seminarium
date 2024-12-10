import openai

# Configuration for OpenAI API
openai.api_base = "http://localhost:8080/v1"
openai.api_key = "not-needed"

# Function to create a chat completion with a dynamic user prompt
def create_chat_completion(user_input, system_message):
    return openai.ChatCompletion.create(
        model="local-model",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
    )

def main():
    # Predefined system message
    system_message = (
    "The user name is Patryk. You are the assistant or chatbot and your name is IronMan."
    )

    # Chat loop
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'bye', 'end']:
            print("Exiting the chat.")
            break

        completion = create_chat_completion(user_input, system_message)
        print("Model Response: ", completion.choices[0].message.content)

if __name__ == "__main__":
    main()