import datetime
import random

from cs50 import SQL

# Set up database connection
db = SQL("sqlite:///hhyy.db")


def main():
    # Get a list of vocabulary to use for the quiz.
    vocab = get_all_vocab()
    # Choose how many questions will be on the quiz and how many multiple choice options each question will have.
    question_count = 10
    muliple_choice_count = 5

    # Select the format of the questions, answers, and other non-used format (to display all info after the question has been answered).
    formats = ['chinese', 'pinyin', 'english']
    question_format = formats[0]
    answer_format = formats[2]
    other_format = formats[1]

    # Generate the quiz and process it to the user.
    # quiz = generate_random_quiz(vocab, question_count, muliple_choice_count)
    quiz = generate_improvement_quiz(vocab, muliple_choice_count)
    process_quiz(quiz, question_count, question_format, answer_format, other_format)


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


# Function to generate a quiz of multiple choice questions.
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
        # Generate a question with the correct answer already chosen, this function will add in 4 incorrect answer options.
        quiz.append(generate_randomn_question(vocab, word_pool, correct, muliple_choice_count))
    return quiz


# Function to generate multiple choice questions with 5 options per question, can be used to generate for any language format.
def generate_randomn_question(vocab, word_pool, correct, muliple_choice_count):
    # Initialize list of options for the multiple choice question, and add the correct answer to the list of options.
    question = []
    question.append(vocab[correct])
    # Generate 4 incorrect answers and add them to the list of options, keeping the correct answer in position [0].
    incorrect_answers = random.sample(word_pool, (muliple_choice_count - 1))
    for answer in incorrect_answers:
        question.append(vocab[answer])
    return question


def generate_improvement_quiz(vocab, muliple_choice_count):
    # Create quiz list for questions to be appended to as they are generated and a pool of numbers to pull correct answers from.
    quiz = []
    word_pool = list(range(0, (len(vocab) - 1)))
    worst = get_worst_vocab()
    for id in worst:
        word_id = int((id['vocab_id']))
        for word in vocab:
            if word_id == word['id']:
                correct = word
                word_pool.remove(word_id - 1)
                break
        # Generate a question with the correct answer already chosen, this function will add in 4 incorrect answer options.
        quiz.append(generate_improvement_question(vocab, word_pool, correct, muliple_choice_count))
    return quiz


def generate_improvement_question(vocab, word_pool, correct, muliple_choice_count):
    # Initialize list of options for the multiple choice question, and add the correct answer to the list of options.
    question = []
    question.append(correct)
    # Generate 4 incorrect answers and add them to the list of options, keeping the correct answer in position [0].
    incorrect_answers = random.sample(word_pool, (muliple_choice_count - 1))
    for answer in incorrect_answers:
        question.append(vocab[answer])
    return question


# Prints quiz to the user once generated.
def process_quiz(quiz, question_count, Q, A, other):
    score = 0
    question_number = 1
    print(f"Vocab Quiz: {str.capitalize(Q)} to {str.capitalize(A)}")
    print("For each question, please input A, B, C, D, or E...")
    print("")
    correct_answers = []
    for question in quiz:
        # Assign position [0] as the correct answer, then shuffle the answers so that the correct answer isn't always A.
        correct_answer = question[0]
        correct_answers.append(correct_answer)
        random.shuffle(question)
        # Keep track of which question we're on.
        print(f"Question {question_number} of {question_count}")
        question_number += 1
        # Question text
        print(f"Select the correct {str.capitalize(A)} translation for the following {str.capitalize(Q)}: {correct_answer[Q]}")
        # Add A, B, C, D, E to prefix each answer choice.
        letter = 65
        for option in question:
            option["letter"] = chr(letter)
            letter += 1
            if option[Q] == correct_answer[Q]:
                option['correctness'] = 'correct'
            else:
                option['correctness'] = 'incorrect'
            print(f"{option['letter']}: {option[A]} {option['correctness']}")
        # Prompt user for answer.
        answer = str.upper(input("Answer: ")).strip()
        # Check if answer is correct.
        if answer == correct_answer["letter"]:
            # If correct, add to score and display all info about the answer.
            score += 1
            print(f"Correct! {correct_answer[Q]} / {correct_answer[A]} / {correct_answer[other]}")
            print("")
        else:
            # If incorrect, tell the user what the correct answer was and display all info about the correct answer.
            print(f"Incorrect!")
            print(f"Correct Answer was {correct_answer['letter']}: {correct_answer[Q]} / {correct_answer[A]} / {correct_answer[other]}")
            print("")
    print("Quiz Complete!")
    print(f"Score: {score}/{question_count}!")


def get_worst_vocab():
    worst = db.execute(
        """SELECT vocab_id, chinese, pinyin, english, correct, seen, ROUND((CAST(correct AS FLOAT) / seen * 100), 2) as accuracy FROM accuracy JOIN vocab ON accuracy.vocab_id = vocab.id
        WHERE user_id = ? ORDER BY accuracy ASC, seen DESC, vocab.id ASC LIMIT 10""", 1)
    return worst


if __name__ == "__main__":
    main()
