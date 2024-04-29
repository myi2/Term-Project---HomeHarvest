from flask import Flask, render_template_string, request, send_file, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime
import os
import pandas as pd
from homeharvest import scrape_property

app = Flask(__name__)
app.config['SECRET_KEY'] = 'klk'

class PropertyForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=20)])
    municipality = StringField('Municipality', validators=[DataRequired(), Length(min=2, max=50)])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=50)])
    listing_type = SelectField('Listing Type', choices=[('for_sale', 'For Sale'), ('for_rent', 'For Rent'), ('pending', 'Pending')])
    past_days = IntegerField('Past Days', validators=[DataRequired()])
    submit = SubmitField('Scrape Properties')

def scrape_and_save_detailed(municipality, state, listing_type, past_days, user_name):
    directory = os.path.join(current_app.root_path, 'scraped_data')
    if not os.path.exists(directory):
        os.makedirs(directory)
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_name}_{current_timestamp}.csv"
    file_path = os.path.join(directory, filename)
    properties = scrape_property(location=f"{municipality}, {state}", listing_type=listing_type, past_days=past_days)
    properties.to_csv(file_path, index=False)
    return file_path

def scrape_and_save_simple(location, listing_type, past_days, user_name):
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_name}_{current_timestamp}.csv"
    properties = scrape_property(location, listing_type, past_days)
    properties.to_csv(filename, index=False)
    return filename

@app.route('/', methods=['GET', 'POST'])
def home():
    form = PropertyForm(request.form)
    if request.method == 'POST' and form.validate():
        user_name = form.name.data.replace(" ", "_")  # Ensure user_name is extracted and formatted correctly
        filename = scrape_and_save_detailed(
            municipality=form.municipality.data,
            state=form.state.data,
            listing_type=form.listing_type.data,
            past_days=form.past_days.data,
            user_name=user_name  # Pass user_name to the function
        )
        return send_file(filename, as_attachment=True)
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <title>Scrape Properties</title>
   <style>
       body {
           font-family: Arial, sans-serif;
           background-color: #f2f2f2;
           margin: 0;
           padding: 0;
       }
       .container {
           max-width: 600px;
           margin: 50px auto;
           background-color: #fff;
           padding: 20px;
           border-radius: 8px;
           box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
       }
       h1, h2 {
           text-align: center;
           color: #333;
       }
       form {
           margin-top: 20px;
       }
       p, li {
           margin-bottom: 15px;
       }
       label {
           font-weight: bold;
       }
       input[type="text"], input[type="number"], select {
           width: 100%;
           padding: 8px;
           border-radius: 5px;
           border: 1px solid #ccc;
       }
       input[type="submit"] {
           width: 100%;
           padding: 10px;
           background-color: #4CAF50;
           color: white;
           border: none;
           border-radius: 5px;
           cursor: pointer;
           font-size: 16px;
       }
       input[type="submit"]:hover {
           background-color: #45a049;
       }
       .info-section {
           margin-top: 30px;
       }
   </style>
</head>
<body>
<div class="container">
   <h1>Enter Details to Scrape Properties</h1>
   <form method="post">
       {{ form.hidden_tag() }}
       <p>
           <label for="name">Your Name:</label><br>
           {{ form.name(size=20) }}
       </p>
       <p>
           <label for="municipality">Municipality:</label><br>
           {{ form.municipality(size=20) }}
       </p>
       <p>
           <label for="state">State:</label><br>
           {{ form.state(size=20) }}
       </p>
       <p>
           <label for="listing_type">Listing Type:</label><br>
           {{ form.listing_type() }}
       </p>
       <p>
           <label for="past_days">Past Days:</label><br>
           {{ form.past_days(size=20) }}
       </p>
       <p>
           {{ form.submit() }}
       </p>
   </form>
   <div class="info-section">
       <h2>About the Project</h2>
       <p>
           The Big Idea: We aim to develop a Python-based web scraper that collects real estate listings from various websites. By inputting search criteria such as location, price range, and desirable home features (e.g., number of bedrooms, bathrooms, and square footage), users will receive tailored home recommendations. Our MVP will provide a straightforward list of homes that match the specified criteria, while our stretch goals include creating a user-friendly web interface and integrating with mapping APIs for enhanced location-based searches.
       </p>
       <p>Team: Adrien Schaal & Moises Yi</p>
       <h2>Learning Objectives & Implementation Plan</h2>
       <ul>
           <li>Learn to construct and deploy a Python-based web scraper.</li>
           <li>Acquire skills in data cleaning and manipulation.</li>
           <li>Investigate machine learning algorithms for home recommendations.</li>
           <li>Explore Python libraries such as Beautiful Soup, Scrapy, and Selenium.</li>
           <li>Develop scraping logic to systematically extract home listings.</li>
           <li>(Stretch Goals) Design a simple web interface using Flask or Django.</li>
       </ul>
       <h2>Project Schedule & Collaboration Plan</h2>
       <p>
           We plan to divide the workload based on individual interests and skill sets, using GitHub for version control and communicating through Slack. The schedule includes initiating scraping, expanding capabilities, developing recommendation logic, and (for stretch goals) beginning web interface development.
       </p>
       <h2>Risks and Limitations</h2>
       <p>
           Challenges include potential changes in website layouts, managing large data volumes, and adhering to legal and ethical web scraping practices. We aim to comply with website terms of service and user data privacy.
       </p>
   </div>
</div>
</body>
</html>

    ''', form=form)

if __name__ == "__main__":
    app.run(debug=True)
    


