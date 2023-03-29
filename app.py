# Import necessary libraries
from flask import Flask, render_template, request
import subprocess

# Create the Flask app
app = Flask(__name__)

# Define the route for the main page
@app.route('/',methods=['GET', 'POST'])
def index():
    result_file = None

    if request.method == 'POST':
    # Get the text input from the form
        text_input = request.form['text_input']
    
    # Run the Python script with the text input as an argument
        result = subprocess.check_output(['python', 'F5_VIP_grapher.py', text_input])
    
    # the result HTML
        result_file = f'edges_{text_input}.html'
    
    # Return the HTML to the user
    return render_template('index.html', result_file=result_file)


# Run the Flask app
if __name__ == '__main__':
    app.run(port=8080,debug=True)
