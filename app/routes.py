from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash
import requests
from . import db
from .models import User, Pokemon
from .forms import RegistrationForm, LoginForm, EditProfileForm, PokemonForm
from app import app

valid_pokemon_names = ['Pikachu', 'Charizard', 'Bulbasaur', 'Squirtle', 'Eevee'] 
authentication_bp = Blueprint('authentication', __name__)

@authentication_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
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

@authentication_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return render_template(url_for('authentication.login'))
    

@authentication_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data

        if form.password.data:
            hashed_password = generate_password_hash(form.password.data)
            current_user.password = hashed_password

        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('authentication.edit_profile'))

    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email

    return render_template('edit_profile.html', form=form)

@authentication_bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('authentication.login'))
   

@authentication_bp.route('/pokemon', methods=['GET', 'POST'])
@login_required
def pokemon_form():
    form = PokemonForm()

    if form.validate_on_submit():
        pokemon_name = form.name.data

        if is_pokemon_collected(pokemon_name):
            flash("You already have {pokemon_name} Pokémon in your collection", 'danger')
            return redirect(url_for('authentication.pokemon_form'))

        if len(current_user.pokemon_collection) >= 5:
            flash("You already have 5 or more Pokémon in your collection", 'danger')
            return redirect(url_for('authentication.pokemon_form'))

        name, stats, abilities, front_shiny = fetch_pokemon_data(pokemon_name)

        if name is not None:
            new_pokemon = Pokemon(name=pokemon_name, user_id=current_user.id)
            db.session.add(new_pokemon)
            db.session.commit()

            flash(f'Pokémon {pokemon_name} added to your collection!', 'success')
            return render_template('pokemon_details.html', name=name, stats=stats, abilities=abilities, front_shiny=front_shiny)

        else:
            flash("Pokemon not found", 'danger')

    return render_template('pokemon_form.html', form=form)

@authentication_bp.route('/list_pokemon')
@login_required
def list_pokemon():
    pokemon_collection = Pokemon.query.filter_by(user_id=current_user.id).all()
    return render_template('list_pokemon.html', pokemon_collection=pokemon_collection)

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
        flash(f'Pokémon {pokemon_name} not found!', 'danger')
        return None, None, None, None

@authentication_bp.route('/is_vaild_pokemon_name/<name>', methods=['GET'])
def is_valid_pokemon_name(name):
        return str(name.capitalize() in valid_pokemon_names)
        
@app.route('/add_pokemon', methods=['GET', 'POST'])
@login_required
def add_pokemon():
    form = PokemonForm()

    if form.validate_on_submit():
        pokemon_name = form.name.data.strip()

        if pokemon_name not in valid_pokemon_names:
            flash("Invalid Pokémon name.", 'danger')
        elif len(current_user.pokemon_collection) >= 5:
            flash("You already have 5 or more Pokémon in your collection.", 'danger')
        else:
            new_pokemon = Pokemon(name=pokemon_name, user_id=current_user.id)

            db.session.add(new_pokemon)
            db.session.commit()

            flash(f'Pokémon {pokemon_name} added to your collection!', 'success')

            return redirect(url_for('pokemon_details', pokemon_id=new_pokemon.id))

    return render_template('add_pokemon.html', form=form)


@app.route('/remove_pokemon/<int:pokemon_id>', methods=['POST'])
@login_required
def remove_pokemon(pokemon_id):
    pokemon = Pokemon.query.get_or_404(pokemon_id)

    if pokemon.user_id != current_user.id:
        flash("You can't remove a Pokémon that doesn't belong to you!", 'danger')
        return redirect(url_for('list_pokemon'))

    try:
        db.session.delete(pokemon)
        db.session.commit()

        flash('Pokémon removed from your collection!', 'success')
        return redirect(url_for('list_pokemon'))
    except Exception as e:
        db.session.rollback() 
        flash('An error occurred while removing the Pokémon. Please try again later.', 'danger')
        return redirect(url_for('list_pokemon'))
    
@authentication_bp.route('/users', methods=['GET'])
@login_required
def list_users():
    other_users = User.query.filter(User.id != current_user.id).all()
    return render_template('list_users.html', users=other_users)

@authentication_bp.route('/attack_user/<int:user_id>', methods=['GET'])
@login_required
def attack_user(user_id):
    user_to_attack = User.query.get(user_id)
    return render_template('attack_user.html', user=user_to_attack)

@authentication_bp.route('/battle/<int:user_id>', methods=['POST'])
@login_required
def battle(user_id):
    selected_pokemon_id = request.form.get('selected_pokemon')
    attack_power = int(request.form.get('attack_power'))

    user_pokemon = Pokemon.query.get(selected_pokemon_id)
    opponent = User.query.get(user_id)

    if not user_pokemon or not opponent:
        flash('Invalid battle request.', 'danger')
        return redirect(url_for('home'))

    opponent_pokemon = opponent.pokemon_collection[0]  
    damage = attack_power - opponent_pokemon.defense

    if damage > 0:
        flash('You won the battle!', 'success')
        user_wins = current_user.wins + 1
        opponent_losses = opponent.losses + 1
    elif damage < 0:
        flash('You lost the battle.', 'danger')
        user_wins = current_user.wins
        opponent_losses = opponent.losses + 1
    else:
        flash('It\'s a tie!', 'info')
        user_wins = current_user.wins
        opponent_losses = opponent.losses

    user_pokemon.hp -= damage
    opponent_pokemon.hp -= damage
    current_user.wins = user_wins
    opponent.losses = opponent_losses

    db.session.commit()

    return redirect(url_for('authentication.battle_result', user_id=user_id))

@authentication_bp.route('/battle_result/<int:user_id>')
@login_required
def battle_result(user_id):
    opponent = User.query.get(user_id)
    opponent_pokemon = opponent.pokemon_collection[0]

    return render_template('battle_result.html', opponent=opponent, opponent_pokemon=opponent_pokemon)

