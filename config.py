import os

class Config:
    SECRET_KEY = "library_secret_key_2026"

    SQLALCHEMY_DATABASE_URI = "sqlite:///library.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BOOK_FINE_PER_DAY = 5
