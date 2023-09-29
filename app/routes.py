from flask import render_template,request,redirect,url_for
from app import app
import requests 
import json 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pokemon', methods=['GET', 'POST'])
def pokemon_form():
    if request.method == 'POST':
        pokemon_name = request.form['pokemon_name']
        
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}")

        if response.status_code == 200:
            pokemon_data = json.loads(response.text)
            
            name = pokemon_data['name']
            stats = pokemon_data['stats']
            abilities = [ability['ability']['name'] for ability in pokemon_data['abilities']]
            front_shiny = pokemon_data['sprites']['front_shiny']
            
            return render_template('pokemon_details.html', name=name, stats=stats, abilities=abilities, front_shiny=front_shiny)
        else:
            return render_template('pokemon_form.html', error="Pokemon not found")

    return render_template('pokemon_form.html')
