from flask import Flask, request, render_template, redirect, url_for
from db import Database
import uuid

app = Flask(__name__)
db = Database(app)

@app.teardown_appcontext
def close_connection(exception):
    db.close_connection(exception)

@app.route('/')
def index():
    questions = db.get_questions()
    return render_template('index.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    user_id = str(uuid.uuid4())  # uniq bir kullanıcı kimliği oluşturalım
    user_answers = request.form.to_dict()
    score, wrong_answers, correct_answers, total_questions = db.get_score(user_id, user_answers)
    highest_score = db.get_highest_score(user_id)
    return redirect(url_for('result', score=score, correct_answers=correct_answers, wrong_answers=wrong_answers, total_questions=total_questions, highest_score=highest_score))

@app.route('/result')
def result():
    score = request.args.get('score', 0, type=float)
    correct_answers = request.args.get('correct_answers', 0, type=int)
    wrong_answers = request.args.get('wrong_answers', 0, type=int)
    total_questions = request.args.get('total_questions', 0, type=int)
    highest_score = request.args.get('highest_score', 0, type=float)
    return render_template('result.html', score=score, correct_answers=correct_answers, wrong_answers=wrong_answers, total_questions=total_questions, highest_score=highest_score)

if __name__ == '__main__':
    app.run(debug=True)
