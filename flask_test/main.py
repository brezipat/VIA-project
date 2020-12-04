from flask import Flask, request, render_template

app = Flask(__name__)

# @app.route('/')
# def index():
#     return "This is the homepage"

@app.route('/tuna')
def tuna():
    return '<h2>Tuna is good</h2>'

@app.route('/profile/<username>')
def profile(username):
    return render_template("profile.html", username=username)

# @app.route('/profile/<username>')
# def profile(username):
#     return '<h2>Hello ' + username + '</h2>'

@app.route('/post/<int:post_id>')
def post(post_id):
    return '<h2>Post ID is ' + str(post_id) + '</h2>'

# @app.route('/')
# def index():
#     return "Method used: %s" % request.method

@app.route('/')
@app.route('/<user>')
def index(user=None):
    return render_template("user.html", user=user)

@app.route('/shopping')
def shopping():
    food = ["Cheese", "Tuna", "Beef"]
    return render_template("shopping.html", food=food)

@app.route('/bacon', methods=['GET', 'POST'])
def bacon():
    if request.method == "POST":
        return "You are using POST"
    elif request.method == "GET":
        return "You are probably using GET"

if __name__ == "__main__":
    app.run(debug=True)
