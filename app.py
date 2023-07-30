from flask import Flask, request, render_template, redirect, url_for
from data_models import db, Author, Book
from datetime import datetime
from sqlalchemy import or_
import os

import requests
# Create an instance of the Flask application after the imports.
app = Flask(__name__)

# the vsc doesn't recognize a simple app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite' so:

# Get the absolute path to the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the database file inside the 'data' folder
db_path = os.path.join(current_directory, 'data', 'library.sqlite')
print(db_path)

# Set the SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# Initialize the SQLAlchemy extension

db.init_app(app)


# fetch img by ISBN 
def get_book_cover(isbn):
    url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and data['items']:
            item = data['items'][0]
            if 'volumeInfo' in item and 'imageLinks' in item['volumeInfo']:
                return item['volumeInfo']['imageLinks'].get('thumbnail')
    return None

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == "POST":
        name = request.form['name']
        birth_date_str = request.form['birth_date']  # Get date as string
        date_of_death_str = request.form['date_of_death']  # Get date as string

        # Convert date strings to Python date objects
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

        # Create an instance of the author class
        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)

        try:
            # Add the new author to the database
            db.session.add(new_author)
            db.session.commit()
            success_message = "Author added successfully!"
        except Exception as e:
            # Handle any errors that occur during the database transaction
            db.session.rollback()
            success_message = "Failed to add author. Please try again."
            

        # Render the add_author.html template with the success message
        return render_template('add_author.html', success_message=success_message)

    else:
        # For GET requests
        return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == "POST":
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        # Create an instance of the book class
        new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
        try:
            # Add the new book to the database
            db.session.add(new_book)
            db.session.commit()
            success_message = "Book added successfully!"
        except Exception as e:
            # Handle any errors that occur during the database transaction
            db.session.rollback()
            success_message = "Failed to add book. Please try again ."

        # Render the add_book.html template with the success message
        return render_template('add_book.html', success_message=success_message, authors=Author.query.all())

    else:
        # For GET requests
        return render_template('add_book.html', authors=Author.query.all()) 

@app.route('/')
def home():
  search_query = request.args.get('search', '')
  # added sort 
  sort_by = request.args.get('sort_by', 'title') # deafult sort by title
  
  # get all the books from the db
  books = Book.query.all()
  #sort the books
#   print("Fetched Books:", books)

  if sort_by == 'title':
    books = Book.query.order_by(Book.title).all()
  elif sort_by == 'author':
    books = Book.query.join(Author).order_by(Author.name).all()

  author_names = {author.id: author.name for author in Author.query.all()}
  book_covers = {book.isbn: get_book_cover(book.isbn) for book in books}

  # If there is a search query, filter the books
  if search_query:
    books = Book.query.join(Author).filter(
            or_(Book.title.ilike(f'%{search_query}%'), Author.name.ilike(f'%{search_query}%'))
        ).order_by(sort_by).all()

  # Check if there are no books found with the search query
    if not books:
      error_message = "There are no books that match the search criteria"
      return render_template('home.html', books=books, author_names=author_names, book_covers=book_covers, error_message=error_message)
  
  return render_template('home.html', books = books, author_names = author_names, book_covers=book_covers) 


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
    else:
      print("error")

    return redirect(url_for('home'))


# details about a book by its id 
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    books = Book.query.all()
    book = Book.query.get(book_id)
    author_names = {author.id: author.name for author in Author.query.all()}
    book_covers = {book.isbn: get_book_cover(book.isbn) for book in books}
    if book:
        return render_template('book.html', book = book, author_names = author_names,book_covers=book_covers )
    else:
      error_msg = "Book not found"
      return render_template('book.html', error_msg = error_msg, book = book, author_names = author_names,book_covers=book_covers)
   


@app.route('/author/<int:author_id>')
def author_detail(author_id):
    author = Author.query.get(author_id)
    if author:
        books_by_author = Book.query.filter_by(author_id=author_id).all()
        return render_template('author.html', author=author, books_by_author=books_by_author)
    else:
        error_msg = "Author not found."
        return render_template('author.html', error_msg=error_msg, author=author, books_by_author=books_by_author)


#https://amadeussupreme-societyparking-5002.codio.io/add_author
if __name__ == '__main__':
    # Bind the server to all available network interfaces (0.0.0.0) and use the Codio provided port
    app.run(host='0.0.0.0', port=5002, debug=True)