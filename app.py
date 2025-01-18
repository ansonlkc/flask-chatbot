from flask import Flask, request, jsonify, render_template, session
import requests
from flask_session import Session

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# OpenAI API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

# Maximum number of messages to keep in the conversation history
MAX_HISTORY = 10

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Retrieve user input
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Initialize or retrieve the conversation context
    if 'conversation' not in session:
        session['conversation'] = [{"role": "system", "content": "You are a helpful assistant."}]

    # Add the user's message to the conversation history
    session['conversation'].append({"role": "user", "content": user_message})

    # Ensure the history doesn't exceed the MAX_HISTORY limit
    if len(session['conversation']) > MAX_HISTORY:
        session['conversation'] = session['conversation'][-MAX_HISTORY:]

    try:
        # Prepare the API request payload
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "google/gemma-2-9b-it:free",
            "messages": session['conversation'],
        }

        # Make the API call
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()

        # Extract the assistant's reply
        response_data = response.json()
        assistant_reply = response_data['choices'][0]['message']['content']

        # Add the assistant's reply to the conversation history
        session['conversation'].append({"role": "assistant", "content": assistant_reply})

        # Save session changes
        session.modified = True

        # Return the assistant's reply
        return jsonify({"reply": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Clear the conversation history."""
    session.pop('conversation', None)
    return jsonify({"message": "Conversation reset."})

if __name__ == '__main__':
    app.run(debug=True)
