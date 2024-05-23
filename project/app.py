import datetime
import json
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)
app.secret_key = 'zhangdawei620323'

# Set up database connection
db = SQL("sqlite:///hhyy.db")

# Using some code from Finance
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET"])
def index():
    try:
        username = session['username']
    except KeyError:
        username = "Guest"

    if username != "Guest":
        recent_quizzes = db.execute("""SELECT * FROM quizzes WHERE "user_id" = ?
            ORDER BY datetime DESC LIMIT 10""", session["user_id"])
        length = len(recent_quizzes)

        try:
            quiz_stats = db.execute("""SELECT SUM("questions") AS 'questions', SUM("correct") AS 'correct' FROM quizzes WHERE "user_id" = ?
                GROUP BY user_id""", session["user_id"])[0]
            total_questions = quiz_stats["questions"]
            total_correct = quiz_stats["correct"]
            quiz_average = round(float(total_correct) / float(total_questions) * 100, 2)
        except IndexError:
            quiz_average = None

        return render_template("index.html", username=username, recent_quizzes=recent_quizzes, length=length, quiz_average=quiz_average)
    else:
        return render_template("index.html", username=username)


@app.route("/vocab-quiz", methods=["GET", "POST"])
def vocab_initiation():
    if request.method == "POST":
        # Get format from the user
        format = request.form.get("format")
        if format == "english_chinese":
            questions = 'english'
            answers = 'chinese'
            other = 'pinyin'
            session['quiz_type'] = "English to Chinese"
        else:
            questions = 'chinese'
            answers = 'english'
            other = 'pinyin'
            session['quiz_type'] = "Chinese to English"

        session['questions'] = questions
        session['answers'] = answers
        session['other'] = other

        # Get question count, pinyin display preference, and difficulty from the user
        try:
            question_count = int(request.form.get("question_count"))
        except TypeError:
            question_count = 3
        display_other = request.form.get("other")
        if not display_other:
            display_other = 'No'
        difficulty = request.form.get("difficulty")
        if difficulty == "Easy":
            muliple_choice_count = 3
        elif difficulty == "Hard":
            muliple_choice_count = 5
        else:
            muliple_choice_count = 4

        # Get a list of vocabulary to use for the quiz.
        vocab = get_all_vocab()

        # Generate the quiz.
        quiz = generate_random_quiz(vocab, question_count, muliple_choice_count)

        # Select a correct answer for each question
        correct_answers = []
        for question in quiz:
            # Assign position [0] as the correct answer, then shuffle the answers so that the correct answer isn't always A.
            correct_answer = question[0]
            correct_answers.append(correct_answer)
            random.shuffle(question)

        letters = ['A', 'B', 'C', 'D' , 'E']

        session['correct_answers'] = correct_answers
        session['question_count'] = question_count

        return render_template("quiz.html", quiz=quiz, correct_answers=correct_answers, question_count=question_count, display_other=display_other, \
                            muliple_choice_count=muliple_choice_count, questions=questions, answers=answers, other=other, letters=letters)

    else:
        question_count = [i for i in range(1, 11)]
        other = ['Yes', 'No']
        difficulty = ['Easy', 'Normal', 'Hard']
        return render_template("vocab.html", question_count=question_count, difficulty=difficulty, other=other)


@app.route("/pinyin-quiz", methods=["GET", "POST"])
def pinyin_initiation():
    if request.method == "POST":
        # Get format from the user
        format = request.form.get("format")
        if format == "pinyin_chinese":
            questions = 'pinyin'
            answers = 'chinese'
            other = 'english'
            session['quiz_type'] = "Pinyin to Chinese"
        else:
            questions = 'chinese'
            answers = 'pinyin'
            other = 'english'
            session['quiz_type'] = "Chinese to Pinyin"

        session['questions'] = questions
        session['answers'] = answers
        session['other'] = other

        # Get question count, pinyin display preference, and difficulty from the user
        try:
            question_count = int(request.form.get("question_count"))
        except TypeError:
            question_count = 3
        display_other = request.form.get("other")
        if not display_other:
            display_other = 'No'
        char_count = request.form.get("chars")
        if not char_count:
            char_count = 2
        difficulty = request.form.get("difficulty")
        if difficulty == "Easy":
            muliple_choice_count = 3
        elif difficulty == "Hard":
            muliple_choice_count = 5
        else:
            muliple_choice_count = 4

        # Get a list of vocabulary to use for the quiz.
        vocab = get_fixed_vocab(char_count)

        # Generate the quiz.
        quiz = generate_random_quiz(vocab, question_count, muliple_choice_count)

        # Select a correct answer for each question
        correct_answers = []
        for question in quiz:
            # Assign position [0] as the correct answer, then shuffle the answers so that the correct answer isn't always A.
            correct_answer = question[0]
            correct_answers.append(correct_answer)
            random.shuffle(question)

        letters = ['A', 'B', 'C', 'D' , 'E']

        session['correct_answers'] = correct_answers
        session['question_count'] = question_count

        return render_template("quiz.html", quiz=quiz, correct_answers=correct_answers, display_other=display_other, \
                            muliple_choice_count=muliple_choice_count, questions=questions, answers=answers, other=other, letters=letters)

    if request.method == "GET":
        question_count = [i for i in range(1, 11)]
        other = ['Yes', 'No']
        characters = [i for i in range(1, 5)]
        difficulty = ['Easy', 'Normal', 'Hard']
        return render_template("pinyin.html", question_count=question_count, characters=characters, difficulty=difficulty, other=other)


@app.route("/quiz-submit", methods=["POST"])
def grade_quiz():

    user_answers = []
    score = 0
    for i in range(session['question_count']):
        question_name = 'question_' + str(i)
        answer = request.form.get(question_name)
        correct_vocab_id = session['correct_answers'][i]['id']
        try:
            # I asked the duck how to convert the return value of request.form.get() from str to dict.
            # need to be careful not to have any apostrophes in the vocab list in order for this to work. -db cleaned up to ensure this
            answer = json.loads(request.form.get(question_name).replace("'", '"'))
        except AttributeError:
            answer = None

        if answer == None:
            answer = "No Answer Provided"
        user_answers.append(answer)

        # Check to see whether the user has had any questions on this vocab word already
        if 'user_id' in session:
            existing_check = check_vocab(session["user_id"], correct_vocab_id)
            existing = len(existing_check)
            if existing > 0:
                seen = existing_check[0]["seen"] + 1
                correct = existing_check[0]["correct"]

        if answer != "No Answer Provided":
            if answer['id'] == correct_vocab_id:
                score += 1
                if 'user_id' in session:
                    if existing == 0 or existing == None:
                        record_vocab_result(session["user_id"], correct_vocab_id, 1)
                    elif existing > 0:
                        correct += 1
                        update_vocab_result(session["user_id"], correct_vocab_id, seen, correct)

            elif answer['id'] != correct_vocab_id:
                if 'user_id' in session:
                    if existing == 0 or existing == None:
                        record_vocab_result(session["user_id"], correct_vocab_id, 0)
                    elif existing > 0:
                        update_vocab_result(session["user_id"], correct_vocab_id, seen, correct)
        else:
            if 'user_id' in session:
                if existing == 0 or existing == None:
                    record_vocab_result(session["user_id"], correct_vocab_id, 0)
                elif existing > 0:
                    update_vocab_result(session["user_id"], correct_vocab_id, seen, correct)


    # Calculate quiz results
    number_correct = score / float(session['question_count']) * 100
    quiz_precent = round(number_correct, 2)
    number_correct_string = (f"{score}/{session['question_count']}")

    # Add the quize result to the results table if the user is logged in
    if 'user_id' in session:
        db.execute("""INSERT INTO quizzes (user_id, type, questions, correct, score, datetime)
                VALUES(?, ?, ?, ?, ?, ?)""", session["user_id"], session['quiz_type'], session['question_count'], score, quiz_precent, datetime.datetime.now())

    # show results page
    return render_template("results.html", correct_answers=session['correct_answers'], user_answers=user_answers, \
                           quiz_precent=quiz_precent, number_correct_string=number_correct_string, \
                            questions=session['questions'], answers=session['answers'], other=session['other'], quiz_type=session['quiz_type'])


@app.route("/history", methods=["GET"])
def vocab_history():
    if 'user_id' in session:
        best = get_best_vocab(10)
        worst = get_worst_vocab(10)
        length = len(best)
        return render_template("history.html", best=best, worst=worst, length=length)
    else:
        return render_template("history.html")


# NOTE: THE /login and /logout code is modified from CS50 FINANCE to fit my needs for this app.
    # I hope this is alright, I fully understand what the code does/how it works and figured this was a pretty standard way to code a way to log in and out of a web app.
    # I have set it up with HTML so if there as issue with the login, it redirects back to the login page and tells the user what the problem was.
@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()
    if request.method == "POST":
        error = "Login Failed"
        # Ensure username and password were submitted
        if not request.form.get("username") or not request.form.get("password"):
            error_code = "Please Provide a Username and Password"
            return render_template("login.html", error=error, error_code=error_code)

        # Query database for username
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(user) != 1 or not check_password_hash(
            user[0]["hash"], request.form.get("password")
        ):
            error_code = "Invalid Username and/or Password"
            return render_template("login.html", error=error, error_code=error_code)

        # Remember which user has logged in
        session["user_id"] = user[0]["id"]
        session["username"] = user[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Clear the session and redirect to the homepage
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# NOTE: THE /register code is modified from my CS50 FINANCE submission to fit my needs for this app.
    # I have set it up with HTML so if there as issue with registration, it redirects back to the registration page and tells the user what the problem was.
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        error = "Registration Failed"

        # Ensure username was submitted
        if not user or not password:
            error_code = "Must Provide a Username/Password"
            return render_template("register.html", error=error, error_code=error_code)

        # Ensure password meets criteria
        elif not validate_password(password):
            error_code = "Invalid Password"
            return render_template("register.html", error=error, error_code=error_code)

        # Ensure password confirmation was submitted
        elif not confirmation:
            error_code = "Must Confirm Password"
            return render_template("register.html", error=error, error_code=error_code)

        # Ensure password and confirmation match
        elif password != confirmation:
            error_code = "Password Confirmation Did Not Match"
            return render_template("register.html", error=error, error_code=error_code)

        # register user if all checks are passed
        else:
            hash = generate_password_hash(password)
            try:
                db.execute("""INSERT INTO users (username, hash) VALUES(?, ?)""", user, hash)
            except ValueError:
                error_code = "That Username is Taken"
                return render_template("register.html", error=error, error_code=error_code)
            return redirect("/")

    else:
        # Direct to registration page
        return render_template("register.html")


# HTML Pages ^
############################################################################################################################################################
# Backend Functions v


# Pulls a list of vocab to use for quizzes, will return the entire list.
# Can use this list when giving away character count isn't a concern.
def get_all_vocab():
    vocab = db.execute(
        """SELECT id, chinese, pinyin, english, length FROM vocab""")
    return vocab


# Pulls a list of vocab to use for quizzes, will return words with a fixed amount of chinese characters.
# This will prevent Chinese -> Pinyin or Pinyin -> Chinese quizzes from giving away answers if the character count doesn't match in the multiple choice options.
def get_fixed_vocab(length):
    vocab = db.execute(
        """SELECT id, chinese, pinyin, english, length FROM vocab
        WHERE length = ?""", length)
    return vocab


# Function to generate a quiz of multiple choice questions, generated randomly
# Takes in a list of vocab and number of questions to include in the quiz.
def generate_random_quiz(vocab, question_count, muliple_choice_count):
    # Create quiz list for questions to be appended to as they are generated and a pool of numbers to pull correct answers from.
    quiz = []
    word_pool = list(range(0, (len(vocab) - 1)))
    for _ in range(question_count):
        # For each question, choose a number that will be fed to the vocab list to select the correct answer.
        # Then remove this number from the list so that words don't get repeated.
        correct = random.choice(word_pool)
        word_pool.remove(correct)
        correct = vocab[correct]
        # Generate a question with the correct answer already chosen, this function will add in incorrect answer options.
        quiz.append(generate_question(vocab, word_pool, correct, muliple_choice_count))
    return quiz


# Function to generate multiple choice questions with a customizable # of options per question, can be used to generate for any language format.
# Incorrect ansers in the question are generated randomly from other vocab words.
def generate_question(vocab, word_pool, correct, muliple_choice_count):
    # Initialize list of options for the multiple choice question, and add the correct answer to the list of options.
    question = []
    question.append(correct)
    # Generate incorrect answers and add them to the list of options, keeping the correct answer in position [0].
    incorrect_answers = random.sample(word_pool, (muliple_choice_count - 1))
    for answer in incorrect_answers:
        question.append(vocab[answer])
    return question


# Checks to see whether or not a user has seen a vocab word on a quiz before or not.
def check_vocab(user_id, vocab_id):
    existing_check = db.execute("""SELECT user_id, vocab_id, seen, correct FROM accuracy WHERE "user_id" = ? AND vocab_id = ?""", user_id, vocab_id)
    return existing_check


# Inserts vocab into accuracy table if this is the first time it's seen. Seen will = 1 since it's the first time, correct will be 1/0.
def record_vocab_result(user_id, vocab_id, result):
    db.execute("""INSERT INTO accuracy (user_id, vocab_id, seen, correct)
                VALUES(?, ?, ?, ?)""", user_id, vocab_id, 1, result)


# Updates accuracy table if this is not the first time the vocab word was seen.
def update_vocab_result(user_id, vocab_id, seen, correct):
    db.execute("""UPDATE accuracy SET seen = ?, correct = ?
                WHERE user_id = ? AND vocab_id = ?""", seen, correct, user_id, vocab_id)


# Get the users top n vocab words/phrases.
def get_best_vocab(n):
    best = db.execute(
        """SELECT vocab_id, chinese, pinyin, english, correct, seen, ROUND((CAST(correct AS FLOAT) / seen * 100), 2) as accuracy FROM accuracy
        JOIN vocab ON accuracy.vocab_id = vocab.id WHERE user_id = ? ORDER BY accuracy DESC, seen DESC, vocab.id ASC LIMIT ?""", session["user_id"], n)
    return best


# Get the users bottom n vocab words/phrases.
def get_worst_vocab(n):
    worst = db.execute(
        """SELECT vocab_id, chinese, pinyin, english, correct, seen, ROUND((CAST(correct AS FLOAT) / seen * 100), 2) as accuracy FROM accuracy
        JOIN vocab ON accuracy.vocab_id = vocab.id WHERE user_id = ? ORDER BY accuracy ASC, seen DESC, vocab.id ASC LIMIT ?""", session["user_id"], n)
    return worst


# Password validation with 4 character type requirements - also used in my CS50 Finance Submission
def validate_password(password):
    upper, lower, number, symbol = 0, 0, 0, 0
    symbols = ['?', '!', '@', '#', '$', '%', '&']
    for _ in password:
        if str.isupper(_):
            upper += 1
        if str.islower(_):
            lower += 1
        if str.isnumeric(_):
            number += 1
        if _ in symbols:
            symbol += 1
    if len(password) < 8 or upper == 0 or lower == 0 or number == 0 or symbol == 0:
        return False
    return True


# This function takes vocab that the user has given incorrect answers on the most, and generates a quiz on it.
# This way the user can practice words that they struggle with.
# NOTE: there is no front end functionality to support this function yet, but I feel I have spent enough time on the project and am ready to submit.
def generate_improvement_quiz(vocab, muliple_choice_count):
    # Create quiz list for questions to be appended to as they are generated and a pool of numbers to pull correct answers from.
    quiz = []
    word_pool = list(range(0, (len(vocab) - 1)))
    # Get a list of words the user struggles with, they will need to have already done some quizzes to support this!
    worst = get_worst_vocab()
    # Generate questions with these vocab words as the correct answer, removing them as options for incorrect answers as we go.
    for id in worst:
        word_id = int((id['vocab_id']))
        for word in vocab:
            if word_id == word['id']:
                correct = word
                word_pool.remove(word_id - 1)
                break
        quiz.append(generate_question(vocab, word_pool, correct, muliple_choice_count))
    return quiz


