from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default="user")
    # role can be 'admin' or 'user'

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    issued_books = db.relationship(
        "IssueBook",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    author = db.Column(db.String(150), nullable=False)

    isbn = db.Column(db.String(50), unique=True)

    category = db.Column(db.String(100))

    quantity = db.Column(db.Integer, nullable=False)

    available = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    issued_books = db.relationship(
        "IssueBook",
        backref="book",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Book {self.title}>"


class IssueBook(db.Model):
    __tablename__ = "issue_books"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    issue_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    due_date = db.Column(db.DateTime, nullable=False)

    return_date = db.Column(db.DateTime)

    fine = db.Column(db.Integer, default=0)

    status = db.Column(
        db.String(20),
        default="Issued"
    )
    # Issued / Returned

    def __repr__(self):
        return f"<IssueBook User:{self.user_id} Book:{self.book_id}>"
