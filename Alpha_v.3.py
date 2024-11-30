from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, date
import pyttsx3
import sqlite3


# Initialize the text-to-speech engine
engine = pyttsx3.init()

# List voices and set preferred voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Example: Select the second voice (change the index as needed)
engine.setProperty('rate', 140)  # Adjust the speech rate
engine.setProperty('volume', 1.0)  # Adjust volume (0.0 to 1.0)

# Database setup
def create_connection():
    connection = None
    try:
        connection = sqlite3.connect("chatbot_db.sqlite")
    except sqlite3.Error as e:
        print(f"Error: {e}")
        exit(23)
    return connection

# Create table if it doesn't exist
def create_table(conn):
    sql_create_table = '''CREATE TABLE IF NOT EXISTS conversation_history (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_message TEXT NOT NULL,
                          ai_response TEXT NOT NULL,
                          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'''
    try:
        cursor = conn.cursor()
        cursor.execute(sql_create_table)
    except sqlite3.Error as e:
        print(f"Error: {e}")

# Prepare the template and model
template = """
You are a friendly and witty chatbot. Answer the question below in a friendly and witty manner.
Here is the conversation history: {context}
Question: {question}
Answer:
"""

model = OllamaLLM(model="wizardlm-uncensored")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def speak(text):
    engine.say(text)
    engine.runAndWait()

def fetch_conversation_history(conn, limit=10):
    sql_select_recent = '''SELECT user_message, ai_response FROM conversation_history ORDER BY timestamp DESC LIMIT ?'''
    context = ""
    try:
        cursor = conn.cursor()
        cursor.execute(sql_select_recent, (limit,))
        rows = cursor.fetchall()
        for row in reversed(rows):
            context += f"User: {row[0]}\nAI: {row[1]}\n"
    except sqlite3.Error as e:
        print(f"Error: {e}")
    return context

def get_bot_name(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT ai_response FROM conversation_history WHERE user_message LIKE '%what is your name%' ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()
    if result:
        return result[0].split()[-1]
    return "Chatbot"

def check_and_greet_user(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(timestamp) FROM conversation_history")
    result = cursor.fetchone()
    current_date = date.today()
    if result is None or (result[0] is not None and result[0].split()[0] < current_date.isoformat()):
        return "Good morning! Ready for a new day?"
    else:
        return "Welcome back! Continuing from where we left off."

def handle_conversation():
    conn = create_connection()
    create_table(conn)
    context = fetch_conversation_history(conn)
    bot_name = get_bot_name(conn)
    print(f"Welcome to the AI Chatbot! Type 'EXIT' to quit. My name is {bot_name}.")

    # for greeting user
    initial_response = check_and_greet_user(conn)
    print("CHATBOT: ", initial_response)
    speak(initial_response)

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        result = chain.invoke({"context": context, "question": user_input})
        response_text = result if isinstance(result, str) else "I couldn't process that. Let's try again."

        print(f"{bot_name}: ", response_text)
        speak(response_text)

        # Insert conversation into the database
        sql_insert_conversation = '''INSERT INTO conversation_history (user_message, ai_response) VALUES (?, ?)'''
        try:
            cursor = conn.cursor()
            cursor.execute(sql_insert_conversation, (user_input, response_text))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error: {e}")

        # Update context with the latest exchange
        context += f"User: {user_input}\nAI: {response_text}\n"

        # Keep only the latest 10 exchanges
        context_lines = context.split('\n')
        if len(context_lines) > 20:  # Each exchange has two lines
            context = '\n'.join(context_lines[-20:])

    conn.close()  # Close the database connection

if __name__ == "__main__":
    handle_conversation()