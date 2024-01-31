import requests
from bs4 import BeautifulSoup, NavigableString
from typing import Dict, List, Union
import re
import json
import os
from urllib.parse import urlparse
from time import sleep


# Scraped 14555 questions from 1362 pages
# Scraped 3728 questions from 65 pagescv

class Question:
    def __init__(self, question, options, answer, explanation, codeblock=None):
        self.question = question
        self.options = options
        self.answer = answer
        self.explanation = explanation
        self.codeblock = codeblock


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


MCQ_PATH = "./github-mcq"


def extract_questions_answers(text):
    lines = text.split('\n')
    questions_answers: Question = []
    current_question = None
    for line in lines:
        if line.startswith('####'):
            if current_question is not None:
                questions_answers.append(current_question)
            current_question = {'question': re.sub(r'^#### Q\d+\. ', '', line).strip(), 'options': [], 'answer': None}
        elif line.startswith('- [ ]'):
            if current_question is not None:
                current_question['options'].append(re.sub(r'^- \[ \] ', '', line).strip())
        elif line.startswith('- [x]'):
            if current_question is not None:
                answer_option = re.sub(r'^- \[x\] ', '', line).strip()
                current_question['options'].append(answer_option)
                current_question['answer'] = answer_option
    if current_question is not None:
        questions_answers.append(Question(current_question['question'], current_question['options'], current_question['answer'], None))
    return questions_answers

def write_questions_to_json(pageQuestions, filename):
    file_path = os.path.join(MCQ_PATH, filename)
    with open(file_path, 'w', encoding="utf8") as f:
        json.dump(pageQuestions, f, default=lambda o: o.__dict__, indent=4)


def scrap_local_files():
    current_dir = os.getcwd()
    git_repo_path = os.path.join(current_dir, 'linkedin-skill-assessments-quizzes-main')
    items = os.listdir(git_repo_path)
    items = [item for item in items if not item.startswith('.')]
    questions_count = 0
    for item in items:
        try:
            directory = os.path.join(git_repo_path, item)
            if os.path.isdir(directory):
                files = os.listdir(directory)
                file = min((f for f in files if not f.startswith('im')), key=len, default=min(files, key=len))
                file_path = os.path.join(directory, file)
                with open(file_path, 'r', encoding="utf8") as f:
                    content = f.read()
                questions = extract_questions_answers(content)
                questions_count += len(questions)
                write_questions_to_json(questions, item + '.json')
        except Exception as e:
            print(e)

    print(f"Scraped {questions_count} questions from {len(items)} pages")




if __name__ == "__main__":
    scrap_local_files()
