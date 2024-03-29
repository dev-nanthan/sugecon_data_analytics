from flask import render_template, url_for, redirect, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .extensions import db
from .models import User, Site
from .data_process import filter_data
import os
import csv

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
        # Extracting date range from request
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Handle cases where dates might be empty
        if not start_date or not end_date:
            return jsonify({"error": "Start date and end date are required."}), 400
    
        # Filter the data using data_process module
        filtered_df = filter_data(start_date, end_date)

        # Convert the filtered data to JSON
        result = filtered_df.to_json(orient="records")
        return jsonify(result)
    
    @app.route('/get_sites', methods=['GET'])
    def get_sites():
        sites = Site.query.all()
        print("getting sites list:", sites)
        return jsonify([{'site_id': site.site_id, 'short_name': site.short_name, 'full_name': site.full_name, 'file_name': site.file_name} for site in sites])
        
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
        
        # Get the sites.csv dir
        current_dir = os.getcwd()
        sites_csv_path = os.path.join(current_dir, 'data', 'sites.csv') 
    
        with open(sites_csv_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                # Assuming the CSV columns are in the order: site_id, short_name, full_name, file_name
                site = Site(site_id=int(row[0]), short_name=row[1], full_name=row[2], file_name=row[3])
                db.session.add(site)
            
            db.session.commit()
        
    # Command to Clear the database
    @app.cli.command('clear-db')
    def clear_db():
        """Clear the database."""
        db.drop_all()
        print("Database Tables are Cleared.")