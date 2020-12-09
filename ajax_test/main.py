from flask import request, Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
  if request.method == 'POST':
    rf = request.form
    print(rf)
    data = request.get_json()
    print(data)
    return render_template('page.html')
  if request.method == "GET":
    return render_template('page.html')

app.run(debug=True)