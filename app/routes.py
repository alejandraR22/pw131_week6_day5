from flask import render_template, request, redirect, url_for, flash,  Blueprint
from flask_login import login_user, current_user, login_required
from app import app, db
from .models import User, Pokemon
from .forms import RegistrationForm, LoginForm, EditProfileForm
from werkzeug.security import generate_password_hash
import requests
from . import is_pokemon_collected

authentication_bp= Blueprint('authentication', __name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pokemon', methods=['GET', 'POST'])
def pokemon_form():
    if request.method == 'POST':
        pokemon_name = request.form['pokemon_name']
        if is_pokemon_collected(pokemon_name):
            return render_template('pokemon_form.html', error= "You already have this Pokemon in your collection")
        
        if len(current_user.pokemon_collection) >=5:
            return render_template('pokemon_form.html', error="You already have 5 or more Pokemon in your collection")

        name, stats, abilities, front_shiny = fetch_pokemon_data(pokemon_name)
        
        if name is not None:
            
            new_pokemon = Pokemon(name=pokemon_name, user_id=current_user.id)
            db.session.add(new_pokemon)
            db.session.commit()
            
            flash(f'Pokémon {pokemon_name} added to your collection!', 'success')
            return render_template('pokemon_details.html', name=name, stats=stats, abilities=abilities, front_shiny=front_shiny)
        else:
            return render_template('pokemon_form.html', error="Pokemon not found")

    return render_template('pokemon_form.html')

@authentication_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username=form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')

    return render_template('login.html', form=form)

@authentication_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()  

    if form.validate_on_submit(): 
        username = form.username.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already in use. Please choose a different username.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('authentication.login'))  

    return render_template('signup.html', form=form)

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

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('edit_profile'))
    
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        
    return render_template('edit_profile.html', form=form)



