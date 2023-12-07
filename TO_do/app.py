from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key
client = MongoClient('mongodb://localhost:27017/')
db = client['forum']

@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if request.method == 'POST':
        username = request.form['username']
        title = request.form['title']
        content = request.form['content']
        if username and title and content:  # Validate inputs
            db.content.insert_one({'username': username, 'title': title, 'content': content})
            flash('Task created successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please fill out all fields.', 'danger')
    return render_template('forum.html')

@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit(post_id):
    post = db.content.find_one({'_id': post_id})
    if request.method == 'POST':
        username = request.form['username']
        title = request.form['title']
        content = request.form['content']
        if username and title and content:
            db.content.update_one({'_id': post_id}, {'$set': {'username': username, 'title': title, 'content': content}})
            flash('Task updated successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please fill out all fields.', 'danger')
    return render_template('edit.html', post=post)

@app.route('/delete/<post_id>')
def delete(post_id):
    db.content.delete_one({'_id': post_id})
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    posts_per_page = 2
    query = request.args.get('query', '')
    filter_by = request.args.get('filter', 'title')
    search_regex = {'$regex': query, '$options': 'i'}
    if filter_by == 'username':
        search_regex = {'$regex': query, '$options': 'i'}
    elif filter_by == 'title':
        search_regex = {'$regex': query, '$options': 'i'}

    num_posts = db.content.count_documents({'$or': [{'title': search_regex}, {'content': search_regex}, {'username': search_regex}]})
    num_pages = (num_posts + posts_per_page - 1) // posts_per_page
    skip = (page - 1) * posts_per_page

    posts = db.content.find({'$or': [{'title': search_regex}, {'content': search_regex}, {'username': search_regex}]}).sort('_id', -1).skip(skip).limit(posts_per_page)
    return render_template('home.html', posts=posts, page=page, num_posts=num_posts, num_pages=num_pages, query=query, filter_by=filter_by)

if __name__ == '__main__':
    app.run(debug=False)
