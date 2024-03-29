from flask import Flask, render_template, session, request, redirect, url_for
from flask_pymongo import PyMongo
import bcrypt
import random

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/triviati"
mongo = PyMongo(app)

@app.route('/')
def index():
    if 'username' in session:

        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})

        if login_user:
            if login_user['role'] == "user":
                return render_template('user_categories.html')
            else:
                return render_template('admin_home.html')
    
    return render_template('user_login.html')

#user routes
@app.route('/user_categories')
def categories():
    return render_template('user_categories.html')

@app.route('/user_editar_perfil')
def edit_profile():
    return render_template('user_editar_perfil.html')

@app.route('/user_login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'email' : request.form['email']})

    if login_user:
        if request.form['pass'].encode('utf-8') == login_user['password'].encode('utf-8'):
            session['username'] = login_user['username']

            #check if user is admin
            if login_user['role'] == "user":
                session['score'] = login_user['score']

            return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/user_logout')
def logout():
    session.pop('username')

    #check if user logout
    if 'score' in session:
        session.pop('score')


    return redirect(url_for('index'))


@app.route('/user_olvido_contrasenia')
def forgot_password():
    return render_template('user_olvido_contrasenia.html')

@app.route('/user_question', methods=['POST'])
def questions():

    questions = mongo.db.questions
    possible_questions = questions.find({'category' : 'ciencia'})
    
    index = random.randint(0,possible_questions.count() - 1)

    #select random question
    question = possible_questions[index]

    return render_template('user_question.html', question=question)

@app.route('/answer_question', methods=['POST'])
def answer_question():
    answer = request.form['answer']
    split = answer.split("-")

    questions = mongo.db.questions
    question = questions.find_one({'question': split[0]})

    users = mongo.db.users
    login_user = users.find_one({'username' : session['username']})

    if question:
        if question['correct'] == int(split[1]):
            #correct answer
            print("el usuario ha respondido correctamente")
            login_user['score'] += question['points']
            session['score'] += question['points']
            users.save(login_user)
            
    possible_questions = questions.find({'category' : 'ciencia'})
    #select random question

    index = random.randint(0,possible_questions.count() - 1)

    next_question = possible_questions[index]

    return render_template('user_question.html', question=next_question)


@app.route('/user_register')
def register():
    return render_template('user_register.html')

@app.route('/user_reglas')
def rules():
    return render_template('user_reglas.html')



#admin routes
@app.route('/admin_categoria')
def admin_categories():
    return render_template('admin_categoria.html')

@app.route('/admin_cuentas')
def admin_accounts():
    return render_template('admin_cuentas.html')

@app.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')

@app.route('/admin_olvido_contrasenia')
def admin_forgot_password():
    return render_template('admin_olvido_contrasenia.html')

@app.route('/admin_premio_actualizar')
def admin_update_prize():
    return render_template('admin_premio_actualizar.html')

@app.route('/admin_premio_instantaneo')
def admin_instant_prize():
    return render_template('admin_premio_instantaneo.html')

@app.route('/admin_premio_ranking')
def admin_ranking_prize():
    return render_template('admin_premio_ranking.html')

@app.route('/admin_question')
def admin_question():
    return render_template('admin_question.html')


if __name__ == "__main__":
    app.secret_key = 'mysecret'
    app.run(debug = True)