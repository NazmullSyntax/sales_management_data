from openai import OpenAI

# The client automatically picks up the OPENAI_API_KEY environment variable
client = OpenAI()

def run_chatbot():
    # Initialize chat history with a system instruction
    messages = [
        {"role": "system", "content": "You are a helpful, concise AI assistant."}
    ]

    print("AI Chatbot initialized! Type 'exit' or 'quit' to end the chat.\n")

    while True:
        user_input = input("You: ")
        
        # Exit condition
        if user_input.strip().lower() in ["exit", "quit"]:
            print("Bot: Goodbye!")
            break
            
        if not user_input.strip():
            continue

        # Append the user's message to conversation history
        messages.append({"role": "user", "content": user_input})

        try:
            # Generate response using GPT-4o-mini (cost-effective model)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )

            # Extract reply text
            bot_reply = response.choices[0].message.content
            print(f"\nBot: {bot_reply}\n")

            # Append the assistant's reply to memory
            messages.append({"role": "assistant", "content": bot_reply})

        except Exception as e:
            print(f"\nAn error occurred: {e}\n")

if __name__ == "__main__":
    run_chatbot()