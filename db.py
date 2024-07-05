import sqlite3
from flask import g

class Database:
    def __init__(self, app):
        self.app = app
        self.DATABASE = 'quiz.db'
        self.init_db()
        
    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(self.DATABASE)
        return db

    def close_connection(self, exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    def init_db(self):
        with self.app.app_context():
            db = self.get_db()
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    option1 TEXT NOT NULL,
                    option2 TEXT NOT NULL,
                    option3 TEXT NOT NULL,
                    option4 TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_answer TEXT NOT NULL,
                    correct_answer TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    highest_score REAL NOT NULL
                )
            ''')
            
            cursor.execute("SELECT COUNT(*) FROM questions")
            count = cursor.fetchone()[0]
            if count == 0:
                sql_insert_data = """INSERT INTO questions (question, option1, option2, option3, option4, answer) VALUES 
                                ('Aşağıdakilerden hangisi bir programlama dilidir?', 'HTML', 'CSS', 'Python', 'SQL', 'Python'),
                                ('Hangisi bir veritabanı yönetim sistemidir?', 'MySQL', 'MongoDB', 'Oracle', 'Hepsi', 'Hepsi'),
                                ('Makine öğrenmesi hangi alana aittir?', 'Yapay Zeka', 'Veri Bilimi', 'Veritabanı', 'Hepsi', 'Hepsi'),
                                ('Görüntü işleme ne işe yarar?', 'Görüntüleri analiz etmek', 'Görüntüleri düzenlemek', 'Görüntüleri sıkıştırmak', 'Hepsi', 'Hepsi'),
                                ('NLP ne anlama gelir?', 'Natural Language Processing', 'Natural Language Program', 'Natural Language Processor', 'Natural Language', 'Natural Language Processing')"""
                cursor.execute(sql_insert_data)
            
            db.commit()
        
    def get_questions(self):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM questions')
        questions = cursor.fetchall()
        return questions
    
    def insert_result(self, user_id, user_answer, correct_answer):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO results (user_id, user_answer, correct_answer) VALUES (?, ?, ?)', (user_id, user_answer, correct_answer))
        db.commit()

    def update_highest_score(self, user_id, score):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT highest_score FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO users (id, highest_score) VALUES (?, ?)', (user_id, score))
        else:
            highest_score = result[0]
            if score > highest_score:
                cursor.execute('UPDATE users SET highest_score = ? WHERE id = ?', (score, user_id))
        db.commit()
    
    def get_highest_score(self, user_id):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT highest_score FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if result is None:
            return 0
        return result[0]

    def get_score(self, user_id, user_answers):
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, answer FROM questions')
        questions = cursor.fetchall()
        
        correct_answers = 0
        total_questions = len(questions)
        
        for question_id, correct_answer in questions:
            user_answer = user_answers.get(f'question{question_id}', None)
            if user_answer is None:
                user_answer = ''  # Kullanıcı cevap vermemişse boş bir string olarak işaretleyelim
                
            self.insert_result(user_id, user_answer, correct_answer)
            
            if user_answer == correct_answer:
                correct_answers += 1
        
        if total_questions == 0:
            score = 0.0
        else:
            score = correct_answers / total_questions * 100
        
        wrong_answers = total_questions - correct_answers
        self.update_highest_score(user_id, score)
        
        return score, wrong_answers, correct_answers, total_questions

