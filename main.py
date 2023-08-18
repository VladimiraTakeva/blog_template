from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import requests
from post import Post
import smtplib
import os
import datetime

MY_EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("PASSWORD")

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor = CKEditor(app)
# BLOG_POSTS_API = "https://api.npoint.io/1fd6513ca420610e88d8"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


class MyForm(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    author_name = StringField("Author's name", validators=[DataRequired()])
    img_url = StringField('Blog Image URL', validators=[DataRequired(), URL()])
    body = CKEditorField('Blog Content')
    submit = SubmitField("Submit Post")


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


def send_email(name, email, phone, message):

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL,
                            to_addrs=MY_EMAIL,
                            msg=f"Subject:Send from my blog\n\nName:{name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
                            )


# posts = requests.get(BLOG_POSTS_API).json()
# all_posts = []
# for post in posts:
#     post_object = Post(post["id"], post["title"], post["subtitle"], post["body"])
#     all_posts.append(post_object)


@app.route("/")
def home():
    all_posts = db.session.query(BlogPost).all()
    posts = [post for post in all_posts]
    return render_template("index.html", all_posts=all_posts)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    is_post_request = False
    if request.method == "GET":
        return render_template("contact.html")
    if request.method == "POST":
        is_post_request = True
        data = request.form
        print(data["name"])
        print(data["email"])
        print(data["phone"])
        print(data["message"])
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template('contact.html', var=is_post_request)


@app.route('/post/<int:post_id>')
def blog(post_id):
    requested_post = None
    all_posts = db.session.query(BlogPost).all()
    for blog_post in all_posts:
        if blog_post.id == post_id:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route('/new-post', methods=['GET', 'POST'])
def create_new_post():
    form = MyForm()
    if request.method == "GET":
        return render_template('make-post.html', form=form)
    if request.method == "POST":
        x = datetime.datetime.now()
        new_blogpost = BlogPost(
            title=request.form.get("title"),
            subtitle=request.form.get("subtitle"),
            date=x.strftime("%B %d, %Y"),
            body=request.form.get("body"),
            author=request.form.get("author_name"),
            img_url=request.form.get("img_url")
        )
        db.session.add(new_blogpost)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/edit-post/<post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = MyForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body)
    if edit_form.validate_on_submit():

        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author_name.data
        post.body = edit_form.body.data

        db.session.commit()
        return redirect(url_for('blog', post_id=post_id))
    return render_template('make-post.html', is_edit=True, form=edit_form)


# TODO: delete_post() to remove a blog post from the database

@app.route('/delete/<post_id>')
def delete_post(post_id):

    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
