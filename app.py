from flask import Flask, render_template, request, jsonify, url_for
import google.generativeai as genai
import logging

# Initialize Flask app
app = Flask(__name__)

# Use your API key directly
GEMINI_API_KEY = "(Private)"
genai.configure(api_key=GEMINI_API_KEY)

# Configure the model
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="For the prompts in this conversation, assume the role of Socrates. I will be your student, and I want to learn about data structure and algorithms using the Socratic method. If I try to ask any question unrelated to Data Structure and Algorithms, steer me back on course like Socrates would. Answer only up to 5 levels, and if I don't understand, tell me to study more like Socrates would."
)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help')
def help_page():
    return render_template('help.html')  # Render help.html from the templates folder

@app.route('/search', methods=['POST'])
def search():
    user_input = request.form['query']
    logging.info(f"User Input: {user_input}")  # Log user input

    try:
        # Use chat session for Socratic dialogue
        chat_session = model.start_chat(
            history=[]
        )
        response = chat_session.send_message(user_input)
        socratic_response = response.text.strip()
        logging.info(f"Model Response: {socratic_response}")  # Log model response
    except Exception as e:
        logging.error(f"Error during model generation: {e}")
        socratic_response = "There was an error processing your request. Please try again."

    return jsonify({"summary": socratic_response})

if __name__ == '__main__':
    app.run(debug=True)
