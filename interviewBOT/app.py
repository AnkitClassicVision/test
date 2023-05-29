from flask import Flask, render_template, request, redirect, url_for
import requests
from flask import send_from_directory
import os
import openai
import csv

from config import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY
answer =''

app = Flask(__name__)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/position', methods=['POST'])
def position():
    position_type = request.form['position_type']
    if position_type == 'new':
        return render_template('new_position.html')
    else:
        return redirect(url_for('index'))  # Redirect to index or handle existing positions

@app.route('/generate', methods=['POST'])
def generate():
    position = request.form['position']
    company_size = request.form['company_size']
    company_industry = request.form['company_industry']
    company_description = request.form['company_description']

    promptM = f"Based on the strata for Elliott Jaques, please create the 3-7 key deliverables for a {position} position for a {company_description} in {company_industry}. Create 2-5 behavior-based questions for each deliverable that is appropriate for the job level of a quality analyst to find if a candidate meets the strata requirements for the deliverable. For each deliverable, highlight which strata is required and the estimated time horizon."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": 'you are an expert on strat by Elliott Jaques and a world class hiring manager'},
            {"role": "user", "content": promptM}
        ]
    )
    answer = response
    result = response.choices[0].message.content

    if len(result) > 0:
        generated_text = result
    else:
        generated_text = "Error: Unable to generate content. Please try again."

    # Parse the generated text to extract the required information
    parsed_data = parse_generated_text(generated_text)

    # Write the parsed data to a CSV file
    with open('output.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Deliverable', 'Strata', 'Time Horizon', 'Behavior-Based Question 1', 'Behavior-Based Question 2', 'Behavior-Based Question 3', 'Behavior-Based Question 4', 'Behavior-Based Question 5'])
        for row in parsed_data:
            csv_writer.writerow(row)

    return render_template('result.html', result=generated_text)

def parse_generated_text(text):
    # This function should parse the generated text and return the required data
    # You can modify this function as needed based on the actual text format
    parsed_data = []

    # Example: (Replace this with the actual logic to parse the generated text)
    deliverables = text.split("\n\n")
    for deliverable in deliverables:
        deliverable_parts = deliverable.split("\n")
        
        if len(deliverable_parts) < 4:  # If there are not enough parts, skip this deliverable
            continue
        
        deliverable_title = deliverable_parts[0]
        strata = deliverable_parts[1]
        time_horizon = deliverable_parts[2]
        questions = deliverable_parts[3:]
        parsed_data.append([deliverable_title, strata, time_horizon] + questions)

    return parsed_data
@app.route('/generate_score', methods=['POST'])
def generate_score():
    resume_text = request.form['resume_text']
    result = request.form['result']
    
    prompt = f"Compare the following resume to the generated result for the position:\n\n{result}\n\nResume:\n{resume_text}\n\nPlease provide a score from 0 to 100 for each deliverable and the overall score from 0 to 100. Also, give reasons for the scores."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": 'you are an expert on strat by Elliott Jaques and a world class hiring manager'},
            {"role": "assistant","content": answer},
            {"role": "user", "content": prompt},
            
        ]
    )


    #score_result = response.choices[0].text.strip()
    score_result = response.choices[0].message.content
    return render_template('score.html', score_result=score_result)
    
if __name__ == '__main__':
    app.run(debug=True)