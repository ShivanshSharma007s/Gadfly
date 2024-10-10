from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import logging
import PyPDF2
import re

# Initialize Flask app
app = Flask(__name__)

# Use your API key directly
GEMINI_API_KEY = "(Private_key)"
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
    system_instruction="Assume the role of Socrates in this conversation. I, the user, will be your student, and I want to learn about data structures and algorithms through the Socratic method. Respond with brief, 2-6 sentence answers, followed by a guiding question. If I ask unrelated questions, steer me back to the topic. Limit responses to a maximum of 5 levels of questioning, and if I don't understand, advise me to study further. Detect the user's language and continue the conversation in that language.Also give refrence from dsa.pdf. If I choice one topic then continue in that topic only make the flow userfriendly"
)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load PDF content into memory
def load_pdf_content(file_path):
    content = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            content += page.extract_text() or ""  # Ensure it handles None types
    return content

# Load DSA content from PDF
dsa_content = load_pdf_content("dsa.pdf")

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

    # Use regular expressions to find the most relevant content
    matches = re.findall(r'(.{0,250})\b' + re.escape(user_input) + r'\b(.{0,250})', dsa_content, re.IGNORECASE)
    if matches:
        # Combine snippets around the keyword
        pdf_response = " ".join([match[0] + user_input + match[1] for match in matches])
    else:
        pdf_response = "I'm sorry, I can't provide information on that topic. Please ask about data structures and algorithms."

    # Use chat session for Socratic dialogue with PDF context
    chat_session = model.start_chat(history=[])
    # Combine PDF response with the user input for Socratic dialogue
    socratic_response = chat_session.send_message(f"{pdf_response}\n{user_input}").text.strip()
    
    logging.info(f"Model Response: {socratic_response}")  # Log model response
    return jsonify({"summary": socratic_response})

if __name__ == '__main__':
    app.run(debug=True)
