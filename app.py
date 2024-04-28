from flask import Flask, render_template_string, request, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime
from homeharvest import scrape_property
import pandas as pd
import os
from flask import Flask, render_template_string, request, send_file, current_app

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace_with_a_secret_key'

class PropertyForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=20)])
    municipality = StringField('Municipality', validators=[DataRequired(), Length(min=2, max=50)])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=50)])
    listing_type = SelectField('Listing Type', choices=[('for_sale', 'For Sale'), ('for_rent', 'For Rent'), ('pending', 'Pending')])
    past_days = IntegerField('Past Days', validators=[DataRequired()])
    submit = SubmitField('Scrape Properties')


def scrape_and_save(municipality, state, listing_type, past_days, user_name):
    directory = os.path.join(current_app.root_path, 'scraped_data')
    if not os.path.exists(directory):
        os.makedirs(directory)
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_name}_{current_timestamp}.csv"
    file_path = os.path.join(directory, filename)  # Full path where the file will be saved
    properties = scrape_property(location=f"{municipality}, {state}", listing_type=listing_type, past_days=past_days)
    properties.to_csv(file_path, index=False)  # Save file to full path
    return file_path  # Return the full path for use in send_file


def scrape_and_save(location, listing_type, past_days, user_name):
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_name}_{current_timestamp}.csv"
    properties = scrape_property(location, listing_type, past_days)
    properties.to_csv(filename, index=False)
    return filename

@app.route('/', methods=['GET', 'POST'])
def home():
    form = PropertyForm(request.form)
    if request.method == 'POST' and form.validate():
        filename = scrape_and_save(
            f"{form.municipality.data}, {form.state.data}",
            form.listing_type.data,
            form.past_days.data,
            form.name.data.replace(" ", "_")
        )
        return send_file(filename, as_attachment=True)
    
    # HTML content defined directly in the return statement
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Scrape Properties</title>
    </head>
    <body>
        <h1>Enter Details to Scrape Properties</h1>
        <form method="post">
            {{ form.hidden_tag() }}
            <p>
                {{ form.name.label }}<br>
                {{ form.name(size=20) }}<br>
            </p>
            <p>
                {{ form.municipality.label }}<br>
                {{ form.municipality(size=20) }}<br>
            </p>
            <p>
                {{ form.state.label }}<br>
                {{ form.state(size=20) }}<br>
            </p>
            <p>
                {{ form.listing_type.label }}<br>
                {{ form.listing_type() }}<br>
            </p>
            <p>
                {{ form.past_days.label }}<br>
                {{ form.past_days(size=20) }}<br>
            </p>
            <p>{{ form.submit() }}</p>
        </form>
    </body>
    </html>
    ''', form=form)

if __name__ == "__main__":
    app.run(debug=True)
