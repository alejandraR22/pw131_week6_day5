from . import auth_bp as auth
from ..forms import LoginForm,RegistrationForm,EditProfileForm
from datetime import datetime
from ..models import User,db
from flask import flash,redirect,url_for,render_template,request
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('site.index'))
        else:
            flash(f'Login failed. Please check your username and password.', 'danger')

    return render_template('login.html', form=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data 
        last_name = form.last_name.data
        email = form.email.data

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash(f'Username already in use. Please choose a different username.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                password=hashed_password,
                first_name=first_name, 
                last_name=last_name,
                email=email,
                date_created=datetime.utcnow(),
                pokemon_collection=None  
            )

            db.session.add(new_user)
            db.session.commit()

            flash(f'Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f'You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/edit_profile', methods=['GET', 'POST'])
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

        flash(f'Profile updated successfully!', 'success')
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email

    return render_template('edit_profile.html', form=form)

@auth.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

