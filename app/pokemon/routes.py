from . import pokemon_bp as pokemon
from ..forms import LoginForm,RegistrationForm,EditProfileForm,PokemonForm
from ..models import User,db,Pokemon
from flask import flash,redirect,url_for,render_template,request
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash
import requests

valid_pokemon_names = ['Pikachu', 'Charizard', 'Bulbasaur', 'Squirtle', 'Eevee']

def is_pokemon_collected(user, pokemon_name):
    return Pokemon.query.filter_by(user_id=user.id, name=pokemon_name).first() is not None

@pokemon.route('/pokemon', methods=['GET', 'POST'])
@login_required
def pokemon_form():
    form = PokemonForm()

    if form.validate_on_submit():
        pokemon_name = form.name.data

        if is_pokemon_collected(pokemon_name):
            flash(f"You already have {pokemon_name} Pokémon in your collection", 'danger')
            return redirect(url_for('pokemon.pokemon_form'))

        if len(current_user.pokemon_collection) >= 5:
            flash(f"You already have 5 or more Pokémon in your collection", 'danger')
            return redirect(url_for('pokemon.pokemon_form'))

        name, stats, abilities, front_shiny = fetch_pokemon_data(pokemon_name)

        if name is not None:
            new_pokemon = Pokemon(name=pokemon_name, user_id=current_user.id)
            db.session.add(new_pokemon)
            db.session.commit()

            flash(f'Pokémon {pokemon_name} added to your collection!', 'success')
            return render_template('pokemon_details.html', name=name, stats=stats, abilities=abilities, front_shiny=front_shiny)

        else:
            flash(f"Pokemon not found", 'danger')

    return render_template('pokemon_form.html', form=form)

def is_pokemon_collected(user, pokemon_name):
    return Pokemon.query.filter_by(user_id=user.id, name=pokemon_name).first() is not None

@pokemon.route('/list_pokemon')
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
    
@pokemon.route('/is_vaild_pokemon_name/<name>', methods=['GET'])
def is_valid_pokemon_name(name):
        return str(name.capitalize() in valid_pokemon_names)
        
@pokemon.route('/add_pokemon', methods=['GET', 'POST'])
@login_required
def add_pokemon():
    form = PokemonForm()

    if form.validate_on_submit():
        pokemon_name = form.name.data.strip()

        if pokemon_name not in valid_pokemon_names:
            flash(f"Invalid Pokémon name.", 'danger')
        elif len(current_user.pokemon_collection) >= 5:
            flash(f"You already have 5 or more Pokémon in your collection.", 'danger')
        else:
            new_pokemon = Pokemon(name=pokemon_name, user_id=current_user.id)

            db.session.add(new_pokemon)
            db.session.commit()

            flash(f'Pokémon {pokemon_name} added to your collection!', 'success')

            return redirect(url_for('pokemon_details', pokemon_id=new_pokemon.id))

    return render_template('add_pokemon.html', form=form)

@pokemon.route('/remove_pokemon/<int:pokemon_id>', methods=['POST'])
@login_required
def remove_pokemon(pokemon_id):
    pokemon = Pokemon.query.get_or_404(pokemon_id)

    if pokemon.user_id != current_user.id:
        flash(f"You can't remove a Pokémon that doesn't belong to you!", 'danger')
        return redirect(url_for('list_pokemon'))

    try:
        db.session.delete(pokemon)
        db.session.commit()

        flash(f'Pokémon removed from your collection!', 'success')
        return redirect(url_for('list_pokemon'))
    except Exception as e:
        db.session.rollback() 
        flash(f'An error occurred while removing the Pokémon. Please try again later.', 'danger')
        return redirect(url_for('list_pokemon'))
    
@pokemon.route('/users', methods=['GET'])
@login_required
def list_users():
    other_users = User.query.filter(User.id != current_user.id).all()
    return render_template('list_users.html', users=other_users)

@pokemon.route('/attack_user/<int:user_id>', methods=['GET'])
@login_required
def attack_user(user_id):
    user_to_attack = User.query.get(user_id)
    return render_template('attack_user.html', user=user_to_attack)

@pokemon.route('/battle/<int:user_id>', methods=['POST'])
@login_required
def battle(user_id):
    selected_pokemon_id = request.form.get('selected_pokemon')
    attack_power = int(request.form.get('attack_power'))

    user_pokemon = Pokemon.query.get(selected_pokemon_id)
    opponent = User.query.get(user_id)

    if not user_pokemon or not opponent:
        flash(f'Invalid battle request.', 'danger')
        return redirect(url_for('home'))

    opponent_pokemon = opponent.pokemon_collection[0]  
    damage = attack_power - opponent_pokemon.defense

    if damage > 0:
        flash(f'You won the battle!', 'success')
        user_wins = current_user.wins + 1
        opponent_losses = opponent.losses + 1
    elif damage < 0:
        flash(f'You lost the battle.', 'danger')
        user_wins = current_user.wins
        opponent_losses = opponent.losses + 1
    else:
        flash(f'It\'s a tie!', 'info')
        user_wins = current_user.wins
        opponent_losses = opponent.losses

    user_pokemon.hp -= damage
    opponent_pokemon.hp -= damage
    current_user.wins = user_wins
    opponent.losses = opponent_losses

    db.session.commit()

    return redirect(url_for('pokemon.battle_result', user_id=user_id))

@pokemon.route('/battle_result/<int:user_id>')
@login_required
def battle_result(user_id):
    opponent = User.query.get(user_id)
    opponent_pokemon = opponent.pokemon_collection[0]

    return render_template('battle_result.html', opponent=opponent, opponent_pokemon=opponent_pokemon)

