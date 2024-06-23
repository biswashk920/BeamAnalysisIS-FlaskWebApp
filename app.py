from flask import Flask
from routes import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a strong secret key

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
