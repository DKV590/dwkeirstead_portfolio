# CS50X FINAL PROJECT 2024
# HuaHaoYueYuan (花好月圆): A Chinese Vocab Practice Web App
By David Keirstead

#### Video Demo: https://www.youtube.com/watch?v=jlCQPKHETFM

#### Introduciton

For my final project I have developed a web application for personal use that allows a user to take quizzes generated off of a list of Chinese vocabulary words. For some background, my wife and parents-in-law are Chinese while I am American and grew up speaking pretty much only English Over the course of the last ~3 years I have been doing video chat Chinese lessons with my mother-in-law. Along the way I have been keeping a list in Excel of all of the vocab she has taught me, and some I have learned on my own. At this point it has grown to over 1,000 words and phrases. Before I took this course I had no idea that I’d be able to use this to create a website but as soon as I started CS50, I knew this is what I wanted to do for my final project!

I chose the name HuaHaoYueYuan (花好月圆) because it is an idiom that holds a special place in my heart. Literally it means "the flowers are in bloom, and the moon is full". In context it refers to a happy and harmonius time to spend with friends and family where the weather is nice and everything feels just right. My mother-in-law helped me write a speech to give to family members when I visited China with my wife for the second time in my life last summer.

#### Back End

For this project, I started by creating a SQL database of all the vocab words from my list, along with class dates. Later on, I added tables for users, and statistics on quizzes and vocab words for each user. The core backend functions for my website pull data from the SQL vocab table, and then create quizzes to be administered to the user. The vocab list can either consist of every single word/phrase, or of words/phrases containing a fixed number of characters (eg. all 4 characters).

Building on this, the generate_random_quiz  and generate_question functions take in the vocab list, a number of questions, and a number of options per question. For each question, they will choose a random vocab word to be the correct answer and generate other random words to be the incorrect answers. Finally, they will shuffle the order of the answers and append the question to the quiz.

The way the data is structured, a quiz is a list of questions, a question is a list of options, and each option is a dictionary containing an id, a Chinese definition, and English definition, a pinyin pronunciation, and a length (# of Chinese characters).

#### Front End

The website itself offers four different quiz formats: Chinese to English, English to Chinese, Chinese to Pinyin, and Pinyin to Chinese. For those unfamiliar, Pinyin literally means “spell out the sound” and is the standard method of Romanization for Mandarin Chinese.

For Chinese/English, users can select a format, a number of questions, a difficulty (number of options per question), and toggle the display of Pinyin on or off. For Chinese/Pinyin, users can select a format, a number of questions, number of characters for each question in the quiz, a difficulty (number of options per question), and toggle the display of English on or off. If the user fails to make any of these selections, there are default values programmed in. I chose to limit Chinese/Pinyin quizzes to a fixed number of characters as to not give away answers by having answer options with varying lengths. There is surely a way to do this that would allow each question to have a different character length, but for now it is fixed per quiz.

Once the user submits a quiz, the grade_quiz function checks each answer to see if they answered correctly and gives them a final score. Unanswered questions are considered incorrect If the user has chosen to create an account and log in, the function records their score, and whether or not they answered correctly for each vocab word that was chosen as a correct answer.  They will then be shown a results table with their answers, the correct answers, and whether or not they answered correctly for each question. If this page is refreshed, a duplicate quiz result will be recorded. This is something that I’d like to learn how to fix, but for now there is a messaging requesting that the user does not refresh the page.

This website can be used without logging in, however, logging allows answers to track their 10 most quiz scores and their overall weighted quiz average (quizzes with more questions carry more weight). They can also navigate to the vocab stats page to view which vocab words/phrases they do the best with, and which they struggle most with. This page shows how many times the user has seen each word in a quiz as the correct answer, and how many times they have answered correctly. In the future I would like to develop a page that allows users to take a quiz based on the words they struggle with so that they can improve.

#### Conclusion

I plan to use this website myself to practice my Chinese vocabulary and with a little polishing up, I’d love to fully implement it as an actual website to share with my family and friends who are also learning Chinese!



