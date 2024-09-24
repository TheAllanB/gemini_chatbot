from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for
import os
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session management

# Load environment variables
load_dotenv()

# Configure the API key for the Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the chat with the Gemini model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to get the response from Gemini
def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    # Combine all chunks into a single response string
    full_response = ''.join([chunk.text for chunk in response])
    return full_response

# Route to handle the home page and chat interaction
@app.route("/", methods=["GET", "POST"])
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == "POST" and "clear_chat" in request.form:
        session.pop('chat_history', None)  # Clear chat history
        return redirect(url_for('index'))  # Refresh the page

    if request.method == "POST" and "user_input" in request.form:
        user_input = request.form.get("user_input")
        if user_input:
            # Get the full response from Gemini
            response = get_gemini_response(user_input)

            # Append user input and bot response to the chat history
            session['chat_history'].append(("You", user_input))
            session['chat_history'].append(("Bot", response))

            # Update the session with the new chat history
            session.modified = True

        return redirect(url_for('index'))

    return render_template("index.html", chat_history=session['chat_history'])

if __name__ == "__main__":
    app.run(debug=True)
