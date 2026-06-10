from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import datetime, timedelta

from config import Config
from models import db, User, Book, IssueBook

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

FINE_PER_DAY = app.config["BOOK_FINE_PER_DAY"]

#============================================
#User Loader
#============================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#============================================
#HOME ROUTE
#============================================

@app.route("/")
def index():
    return render_template("index.html")

#===========================================
#REGISTRATION ROUTE
#===========================================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:
            flash("Username or Email already exists.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            role="user"
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful.")
        return redirect(url_for("login"))

    return render_template("register.html")

#==========================================
#LOGIN ROUTE
#==========================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):
            login_user(user)

            flash("Login Successful.")

            if user.role == "admin":
                return redirect(
                    url_for("admin_dashboard")
                )

            return redirect(
                url_for("user_dashboard")
            )

        flash("Invalid Username or Password.")

    return render_template("login.html")

#==============================
#LOGOUT ROUTE
#==============================
@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully.")

    return redirect(url_for("login"))

#===============================
#ADMIN DASHBOARD
#===============================

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        flash("Access Denied.")
        return redirect(url_for("index"))

    total_books = Book.query.count()

    total_users = User.query.filter_by(
        role="user"
    ).count()

    issued_books = IssueBook.query.filter_by(
        status="Issued"
    ).count()

    return render_template(
        "admin_dashboard.html",
        total_books=total_books,
        total_users=total_users,
        issued_books=issued_books
    )


#==================================
#USER DASHBOARD
#==================================

@app.route("/user/dashboard")
@login_required
def user_dashboard():

    books = Book.query.all()

    my_books = IssueBook.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "user_dashboard.html",
        books=books,
        my_books=my_books
    )


#====================================
#VIWE ALL BOOKS
#====================================

@app.route("/books")
@login_required
def books():

    all_books = Book.query.all()

    return render_template(
        "books.html",
        books=all_books
    )

#====================================
#SEARCH BOOKS
#====================================

@app.route("/search")
@login_required
def search_books():

    keyword = request.args.get("keyword")

    books = Book.query.filter(
        Book.title.contains(keyword)
    ).all()

    return render_template(
        "books.html",
        books=books
    )

#============================
#ADD BOOKS
#============================
@app.route("/books/add", methods=["GET", "POST"])
@login_required
def add_book():

    if current_user.role != "admin":
        flash("Access Denied.")
        return redirect(url_for("index"))

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        isbn = request.form["isbn"]
        category = request.form["category"]
        quantity = int(request.form["quantity"])

        existing_book = Book.query.filter_by(
            isbn=isbn
        ).first()

        if existing_book:
            flash("Book with this ISBN already exists.")
            return redirect(url_for("add_book"))

        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            quantity=quantity,
            available=quantity
        )

        db.session.add(book)
        db.session.commit()

        flash("Book Added Successfully.")
        return redirect(url_for("books"))

    return render_template("add_book.html")

#=========================
#EDIT BOOK
#=========================

@app.route("/books/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):

    if current_user.role != "admin":
        flash("Access Denied.")
        return redirect(url_for("index"))

    book = Book.query.get_or_404(id)

    if request.method == "POST":

        new_quantity = int(request.form["quantity"])

        issued_count = book.quantity - book.available

        if new_quantity < issued_count:
            flash(
                f"Quantity cannot be less than {issued_count}."
            )
            return redirect(
                url_for("edit_book", id=id)
            )

        book.title = request.form["title"]
        book.author = request.form["author"]
        book.isbn = request.form["isbn"]
        book.category = request.form["category"]

        book.available += (
            new_quantity - book.quantity
        )

        book.quantity = new_quantity

        db.session.commit()

        flash("Book Updated Successfully.")

        return redirect(url_for("books"))

    return render_template(
        "edit_book.html",
        book=book
    )

#============================
#DELETE BOOK
#============================

@app.route("/books/delete/<int:id>")
@login_required
def delete_book(id):

    if current_user.role != "admin":
        flash("Access Denied.")
        return redirect(url_for("index"))

    book = Book.query.get_or_404(id)

    issued = IssueBook.query.filter_by(
        book_id=id,
        status="Issued"
    ).count()

    if issued > 0:
        flash(
            "Cannot delete a book that is currently issued."
        )
        return redirect(url_for("books"))

    db.session.delete(book)
    db.session.commit()

    flash("Book Deleted Successfully.")

    return redirect(url_for("books"))

#===============================
#ISSUE BOOK
#===============================

@app.route("/issue/<int:book_id>")
@login_required
def issue_book(book_id):

    book = Book.query.get_or_404(book_id)

    if book.available <= 0:
        flash("Book Not Available.")
        return redirect(url_for("books"))

    already_issued = IssueBook.query.filter_by(
        user_id=current_user.id,
        book_id=book.id,
        status="Issued"
    ).first()

    if already_issued:
        flash("You already issued this book.")
        return redirect(url_for("books"))

    issue = IssueBook(
        user_id=current_user.id,
        book_id=book.id,
        due_date=datetime.utcnow() + timedelta(days=14)
    )

    book.available -= 1

    db.session.add(issue)
    db.session.commit()

    flash("Book Issued Successfully.")

    return redirect(url_for("user_dashboard"))

#======================================
#Return Book With Fine Calculation
#======================================

@app.route("/return/<int:issue_id>")
@login_required
def return_book(issue_id):

    issue = IssueBook.query.get_or_404(issue_id)

    if (
        issue.user_id != current_user.id
        and current_user.role != "admin"
    ):
        flash("Access Denied.")
        return redirect(url_for("index"))

    issue.return_date = datetime.utcnow()

    if issue.return_date > issue.due_date:

        days_late = (
            issue.return_date - issue.due_date
        ).days

        issue.fine = days_late * FINE_PER_DAY

    issue.status = "Returned"

    issue.book.available += 1

    db.session.commit()

    flash(
        f"Book Returned Successfully. Fine: ₹{issue.fine}"
    )

    return redirect(url_for("user_dashboard"))

#==================================
#VIEW USERS
#==================================
@app.route("/users")
@login_required
def users():

    if current_user.role != "admin":
        flash("Access Denied.")
        return redirect(url_for("index"))

    all_users = User.query.filter(
        User.role != "admin"
    ).all()

    return render_template(
        "users.html",
        users=all_users
    )

#================================
#DELETE USER
#================================

@app.route("/users/delete/<int:id>")
@login_required
def delete_user(id):

    if current_user.role != "admin":
        flash("Access Denied.")
        return redirect(url_for("index"))

    user = User.query.get_or_404(id)

    active_issues = IssueBook.query.filter_by(
        user_id=id,
        status="Issued"
    ).count()

    if active_issues > 0:
        flash(
            "User has issued books and cannot be deleted."
        )
        return redirect(url_for("users"))

    db.session.delete(user)
    db.session.commit()

    flash("User Deleted Successfully.")

    return redirect(url_for("users"))

#==================================
#CHANGE PASSWORD
#==================================

@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form["current_password"]

        new_password = request.form["new_password"]

        if not check_password_hash(
            current_user.password,
            current_password
        ):
            flash("Current Password is incorrect.")
            return redirect(
                url_for("change_password")
            )

        current_user.password = generate_password_hash(
            new_password
        )

        db.session.commit()

        flash("Password Changed Successfully.")

        return redirect(
            url_for("user_dashboard")
        )

    return render_template(
        "change_password.html"
    )

#=================================
#CREATE DEFAULT ADMIN ACCOUNT
#=================================

@app.before_request
def create_admin():

    admin = User.query.filter_by(
        username="Prajakta"
    ).first()

    if not admin:

        admin = User(
            username="Prajakta",
            email="admin@library.com",
            password=generate_password_hash(
                "Prajakta123"
            ),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

#===================================
#RUN APPLICATION
#===================================
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    if __name__ == "__main__":
     app.run()













