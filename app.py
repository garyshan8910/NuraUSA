from flask import Flask, redirect, render_template
from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Admin'

@app.route("/")
def hello():
  return render_template('index.html')

@app.route("/login", methods = ['GET', 'POST'])
def login():
  form = LoginForm()
  if form.is_submitted():
        msg = "username={}, password={}, remember_me={}".format(
            form.username.data,
            form.password.data,
            form.remember_me.data
        )
        print(msg)
        return redirect('/')
  return render_template('login.html', form = form)

if __name__ == "__main__":
  app.run()
