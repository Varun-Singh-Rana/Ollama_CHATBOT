from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import pyttsx3
import sqlite3
import sympy as sp

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# List voices and set preferred voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Example: Select the second voice (change the index as needed)
engine.setProperty('rate', 140)  # Adjust the speech rate
engine.setProperty('volume', 1.0)  # Adjust volume (0.0 to 1.0)

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

class ChatbotCore:
    def __init__(self):
        self.conn = self.create_connection()
        self.create_table(self.conn)
        self.context = self.fetch_conversation_history(self.conn)

    def create_connection(self):
        try:
            return sqlite3.connect("chatbot_db.sqlite")
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return None

    def create_table(self, conn):
        sql_create_table = '''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        try:
            cursor = conn.cursor()
            cursor.execute(sql_create_table)
        except sqlite3.Error as e:
            print(f"Error: {e}")

    def fetch_conversation_history(self, conn, limit=10):
        sql_select_recent = '''
            SELECT user_message, ai_response
            FROM conversation_history
            ORDER BY timestamp DESC
            LIMIT ?'''
        context = ""
        try:
            cursor = conn.cursor()
            cursor.execute(sql_select_recent, (limit,))
            rows = cursor.fetchall()
            for row in reversed(rows):  # Reverse to maintain chronological order
                context += f"User: {row[0]}\nAI: {row[1]}\n"
        except sqlite3.Error as e:
            print(f"Error: {e}")
        return context

    def get_response(self, user_message):
        # Check if user is asking for the date
        if "date" in user_message.lower():
            return self.get_current_date()

        # Check if user is asking a math question
        if self.is_math_question(user_message):
            return self.solve_math_question(user_message)

        # Use the AI model for other responses
        result = chain.invoke({"context": self.context, "question": user_message})
        response_text = result if isinstance(result, str) else "I couldn't process that."
        self.context += f"User: {user_message}\nAI: {response_text}\n"
        self.save_conversation(self.conn, user_message, response_text)
        return response_text

    def get_current_date(self):
        now = datetime.now()
        return f"Today's date is {now.strftime('%A, %d %B %Y')} and the time is {now.strftime('%H:%M:%S')}."

    def is_math_question(self, message):
        keywords = ["solve", "calculate", "compute", "math", "equation"]
        return any(keyword in message.lower() for keyword in keywords)

    def solve_math_question(self, message):
        try:
            # Extract the mathematical expression from the user's message
            expr = sp.sympify(message)
            solution = sp.solve(expr)
            return f"The solution to the equation is: {solution}"
        except (sp.SympifyError, ValueError):
            return "I couldn't understand the math question. Please provide a valid mathematical expression."

    def save_conversation(self, conn, user_message, ai_response):
        sql_insert = '''
            INSERT INTO conversation_history (user_message, ai_response)
            VALUES (?, ?)'''
        try:
            cursor = conn.cursor()
            cursor.execute(sql_insert, (user_message, ai_response))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error: {e}")

    def speak(self, text):
        engine.say(text)
        engine.runAndWait()