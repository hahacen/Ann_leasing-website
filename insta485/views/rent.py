import pathlib
import uuid
import arrow
import flask
import insta485

@insta485.app.route('/rent/')
def rent():
    # Assuming the user is logged in and their username is stored in session
    logname = flask.session['username']

    # Connect to the database
    connection = insta485.model.get_db()

    # Get form data
    apartment = flask.request.form['apartment']
    price_range = flask.request.form['priceRange']
    name_in_post = flask.request.form['namePost']
    date = flask.request.form['date']
    descriptions = flask.request.form['descriptions']
    contact = flask.request.form['contact']

    # Handle file upload
    pictures = flask.request.files.getlist('pictures')
    picture_filenames = []
    for picture in pictures:
        # Ensure the file has a filename
        if picture.filename != '':
            # Save each picture
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
            picture_filenames.append(filename)

    # Insert post into the database
    query = '''
    INSERT INTO posts (owner, apartment, price, date, descriptions, contact, filename)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    for filename in picture_filenames:
        connection.execute(query, (logname, apartment, price_range, date, descriptions, contact, filename))

    # Commit the changes
    connection.commit()

    # Redirect to the target URL or the user's page if no target URL is provided
    target_url = flask.request.args.get('target', f"/users/{logname}/")
    return flask.redirect(target_url)