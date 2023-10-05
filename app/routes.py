from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from app import app, db
from .models import User
import json
from werkzeug.security import generate_password_hash
import requests

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pokemon', methods=['GET', 'POST'])
def pokemon_form():
    if request.method == 'POST':
        pokemon_name = request.form['pokemon_name']

        name, stats, abilities, front_shiny = fetch_pokemon_data(pokemon_name)

        if name is not None:
            flash(f'Pokémon {pokemon_name} added to your collection!', 'success')
            return render_template('pokemon_details.html', name=name, stats=stats, abilities=abilities, front_shiny=front_shiny)
        else:
            return render_template('pokemon_form.html', error="Pokemon not found")

    return render_template('pokemon_form.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already in use. Please choose a different username.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

def fetch_pokemon_data(pokemon_name):
    api_url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}/'
    response = requests.get(api_url)
    if response.status_code == 200:
        pokemon_data = response.json()

        name = pokemon_data['name']
        stats = pokemon_data['stats']
        abilities = [ability['ability']['name'] for ability in pokemon_data['abilities']]
        front_shiny = pokemon_data['sprites']['front_shiny']
        return name, stats, abilities, front_shiny
    else:
        flash(f'Pokémon {pokemon_name} not found!', 'error')
        return None, None, None, None
