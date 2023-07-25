from flask import Flask, render_template, request
import requests
from post import Post
import smtplib
import os

MY_EMAIL = os.environ["MY_EMAIL"]
PASSWORD = os.environ["PASSWORD"]

app = Flask(__name__)
BLOG_POSTS_API = "https://api.npoint.io/1fd6513ca420610e88d8"


def send_email(name, email, phone, message):

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL,
                            to_addrs=MY_EMAIL,
                            msg=f"Subject:Send from my blog\n\nName:{name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
                            )


posts = requests.get(BLOG_POSTS_API).json()
all_posts = []
for post in posts:
    post_object = Post(post["id"], post["title"], post["subtitle"], post["body"])
    all_posts.append(post_object)


@app.route("/")
def home():
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


@app.route('/post/<int:num>')
def blog(num):
    requested_post = None
    for blog_post in all_posts:
        if blog_post.id == num:
            requested_post = blog_post
    return render_template('post.html', post=requested_post)


if __name__ == "__main__":
    app.run(debug=True)
