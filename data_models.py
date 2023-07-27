from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    def __repr__(self):
        return f"Author(id={self.id}, name='{self.name}', birth_date='{self.birth_date}', date_of_death='{self.date_of_death}')"

    def __str__(self):
        return f"Author: {self.name}, Birth Date: {self.birth_date}, Date of Death: {self.date_of_death}"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer)
    # Foreign Key 
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def __repr__(self):
        return f"Book(id={self.id}, isbn='{self.isbn}', title='{self.title}', publication_year={self.publication_year}, author_id={self.author_id})"
    
    def __str__(self):
        return f"Book: {self.title}, ISBN: {self.isbn}, Publication Year: {self.publication_year}, Author ID: {self.author_id}"

# if __name__ == '__main__':
#     # Import your Flask app here to ensure the db instance is attached to it
#     from app import app

#     # Initialize the SQLAlchemy extension with the Flask app
#     db.init_app(app)

#     # Create the database tables
#     with app.app_context():
#         db.create_all()