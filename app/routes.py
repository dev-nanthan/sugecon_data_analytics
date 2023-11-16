from flask import render_template, url_for, redirect, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .extensions import db
from .models import User
from .data_process import filter_data
import os

def init_routes(app):
    # Handle Landing Page
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return redirect(url_for('login'))

    # Authenticated home view
    @app.route('/home')
    @login_required
    def home():
        username = current_user.username
        return render_template('home.html', username=username)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            try:
                # Extract Username and Email
                username = request.form['username']
                email = request.form['email']
                
                # Extract password and hash it
                password = request.form['password']
                confirm_password = request.form['confirm_password']
                
                # Check if Username pre-exists                
                existing_user = User.query.filter_by(username=username).first()
                
                # Validate Pass code Confirmation
                if existing_user:
                    flash('Username already exists.')
                    return redirect(url_for('signup'))
                
                elif password == confirm_password:
   
                    new_user = User(username=username, email=email)
                    new_user.set_password(password)
                    
                    db.session.add(new_user)
                    db.session.commit()
                    
                    flash('Successfully registered! Please log in.')
                    return redirect(url_for('login'))
                else:
                    flash('Confirm Password do not match.')
                    return redirect(url_for('signup'))
                
            except Exception as e:
                # If there is any error, flash a message to the user
                flash(str(e))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            # Extract the username and password from form data
            username = request.form['username']
            password = request.form['password']
            
            # Use username to find user 
            user = User.query.filter_by(username=username).first()
            if user :
                # Validate password
                if user.check_password(password):
                    login_user(user)
                    return redirect(url_for('home'))
                else:
                    flash('Invalid password')
            else:
                flash('User Not Found')
        return render_template('login.html')


    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/get_data', methods=['GET'])
    def get_data():
        # Extracting date and time range from request
        start_date = request.args.get('start_date')
        start_time = float(request.args.get('start_time'))
        end_date = request.args.get('end_date')
        end_time = float(request.args.get('end_time'))

        # Filter the data using data_process module
        filtered_df = data_process.filter_data(start_date, start_time, end_date, end_time)

        # Convert the filtered data to JSON
        result = filtered_df.to_json(orient="records")
        return jsonify(result)
  
    @app.route('/contact')
    def contact_us():
        return render_template('contact.html', active_page='contact_us')

    # Error handler
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error=str(e)), 500

    # Command to create the database tables
    @app.cli.command('create-db')
    def create_db():
        """Create the database."""
        db.create_all()
        print("Database Tables created.")
        
    # Command to Clear the database
    @app.cli.command('clear-db')
    def clear_db():
        """Clear the database."""
        db.drop_all()
        print("Database Tables are Cleared.")