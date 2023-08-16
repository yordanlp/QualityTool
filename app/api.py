from flask import request, jsonify, render_template, redirect, url_for, flash
from app import app, db
from app.models import School
from datetime import datetime

def validate_school_data(data):
    errors = []

    # Check for required fields
    required_fields = ['school_id', 'school_name', 'geolocation', 'internet_speed', 'provider']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"'{field}' is required and cannot be empty.")

    # Validate school_id
    if 'school_id' in data and not data['school_id'].strip():
        errors.append("school_id cannot be an empty string.")

    # Validate school_name
    if 'school_name' in data and not data['school_name'].strip():
        errors.append("school_name cannot be an empty string.")

    # Validate geolocation format (latitude,longitude)
    if 'geolocation' in data:
        try:
            lat, lon = map(float, data['geolocation'].split(","))
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                errors.append("Invalid geolocation values. Latitude must be between -90 and 90, and Longitude must be between -180 and 180.")
        except ValueError:
            errors.append("Geolocation format should be 'latitude,longitude'.")

    # Validate internet_speed as a positive number
    if 'internet_speed' in data:
        try:
            speed = float(data['internet_speed'])
            if speed <= 0:
                errors.append("Internet speed must be a positive number.")
        except ValueError:
            errors.append("Invalid format for internet_speed. It should be a number.")


    return errors


@app.route('/schools', methods=['POST'])
def add_school():
    data = request.json

    # Validate the received data
    validation_errors = validate_school_data(data)
    if validation_errors:
        return jsonify({"status": "error", "errors": validation_errors}), 400

    # Check if the school with the given school_id already exists
    existing_school = School.query.filter_by(school_id=data['school_id']).first()

    if existing_school:
        # Update the existing school's data
        existing_school.school_name = data['school_name']
        existing_school.geolocation = data['geolocation']
        existing_school.internet_speed = data['internet_speed']
        existing_school.provider = data['provider']
        existing_school.data_source = data.get('data_source', 'Unknown')
        existing_school.last_updated = datetime.utcnow()
        db.session.commit()
        return jsonify({"status": "success", "message": "Data updated successfully", "school_id": existing_school.school_id}), 200
    else:
        # Insert a new school record
        school = School(
            school_id=data['school_id'],
            school_name=data['school_name'],
            geolocation=data['geolocation'],
            internet_speed=data['internet_speed'],
            provider=data['provider'],
            data_source=data.get('data_source', 'Unknown')  # Default to 'Unknown' if not provided
        )
        db.session.add(school)
        db.session.commit()
        return jsonify({"status": "success", "message": "Data added successfully", "school_id": school.school_id}), 201


@app.route('/schools/<school_id>', methods=['GET'])
def get_school(school_id):
    school = School.query.filter_by(school_id=school_id).first()
    if not school:
        return jsonify({"status": "error", "message": "School not found"}), 404

    school_data = {
        "school_id": school.school_id,
        "school_name": school.school_name,
        "geolocation": school.geolocation,
        "internet_speed": school.internet_speed,
        "provider": school.provider,
        "last_updated": school.last_updated,
        "data_source": school.data_source
    }
    return jsonify(school_data), 200


@app.route('/submit_school', methods=['GET', 'POST'])
def submit_school():
    if request.method == 'POST':
        data = {
            'school_id': request.form['school_id'],
            'school_name': request.form['school_name'],
            'geolocation': request.form['geolocation'],
            'internet_speed': request.form['internet_speed'],
            'provider': request.form['provider'],
            'data_source': request.form['data_source']
        }

        # Call the add_school API internally or send a POST request
        validation_errors = validate_school_data(data)
        if validation_errors:
            return render_template('school_form.html', response=', '.join(validation_errors))
        else:
            # Check if the school with the given school_id already exists
            existing_school = School.query.filter_by(school_id=data['school_id']).first()

            if existing_school:
                # Update the existing school's data
                existing_school.school_name = data['school_name']
                existing_school.geolocation = data['geolocation']
                existing_school.internet_speed = data['internet_speed']
                existing_school.provider = data['provider']
                existing_school.data_source = data.get('data_source', 'Unknown')
                existing_school.last_updated = datetime.utcnow()
                db.session.commit()
            else:
                # Insert a new school record
                school = School(
                    school_id=data['school_id'],
                    school_name=data['school_name'],
                    geolocation=data['geolocation'],
                    internet_speed=data['internet_speed'],
                    provider=data['provider'],
                    data_source=data.get('data_source', 'Unknown')  # Default to 'Unknown' if not provided
                )
                db.session.add(school)
                db.session.commit()

            return render_template('school_form.html', response="Data added/updated successfully")

    return render_template('school_form.html', response=None)