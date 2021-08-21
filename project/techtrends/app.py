import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

import logging
import sys

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:

        ## log line
        app.logger.info('A non-existing article was accessed.')

        return render_template('404.html'), 404
    else:

        post_title = post[2]

        ## log line
        app.logger.info('Article "{}" was retrieved.'.format(post_title))

        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():

    ## log line
    app.logger.info('"About Us" page was retrieved.')

    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            ## log line
            app.logger.info('Article "{}" was created.'.format(title))

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the Healthcheck endpoint
@app.route('/healthz')
def healthz():

    response = app.response_class(
            response = json.dumps({"result":"OK - healthy"}),
            status = 200,
            mimetype = 'application/json'
            )

    return response

@app.route('/metrics')
def metrics():

    connection = get_db_connection()
    
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM posts')
    
    post_count = cursor.fetchone()[0]
    db_connection_count = 1

    connection.close()
    
    response = app.response_class(
            response=json.dumps({"db_connection_count":db_connection_count,"post_count":post_count}),
            status=200,
            mimetype='application/json'
            )

    return response

# start the application on port 3111
if __name__ == "__main__":

    ## stream logs to app.log file
    logging.basicConfig(
            format='%(levelname)s:%(name)s %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            handlers=[
            ##    logging.FileHandler('app.log'),
                logging.StreamHandler(),],
            level=logging.DEBUG)

    app.run(host='0.0.0.0', port='3111', debug=False)
