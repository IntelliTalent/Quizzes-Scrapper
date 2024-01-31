import requests
from bs4 import BeautifulSoup, NavigableString
from typing import Dict, List, Union
import re
import json
import os
from urllib.parse import urlparse, urlunparse
from time import sleep



# Scraped 14555 questions from 1362 pages
# Scraped 3728 questions from 65 pages
# Scraped 7325 questions from 100 pages

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



MCQ_PATH = "./javatpoint-mcq"

def write_questions_to_json(pageQuestions, filename):
    filename = os.path.join(MCQ_PATH, filename)
    with open(filename, 'w') as f:
        json.dump(pageQuestions, f, default=lambda o: o.__dict__, indent=4)



def scrap_links_from_javaguide(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = {}
    h3_links = soup.find_all('article', class_='post-outer-container')

    a_elements = []
    for h3 in h3_links:
        a_elements.extend(h3.find_all('a', href=True))

    unique_href = set()

    for a in a_elements:
        href = a['href']
        if href.startswith('#'):
            continue

        parsed = urlparse(href)
        parsed = parsed._replace(fragment="")
        href = urlunparse(parsed)

        if bool(parsed.netloc) and bool(parsed.scheme):
            link_text = a.text.strip()
            if href not in unique_href:
                unique_href.add(href)
                links[link_text] = href


    try:
        next_link_div = soup.find('div', id='blog-pager')
        next_link = next_link_div.find('a', class_='blog-pager-older-link')['href']
    except Exception as e:
        print(f"Failed to find next link with error {e}")
        next_link = None

    return links, next_link

def scrap_questions_from_javaguide(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        with open('waer.txt', 'w') as f:
            f.write(str(soup))

        questions:Question = []
        questions_div = soup.find('div', class_='post-body entry-content float-container')

        with open('waer.txt', 'w') as f:
            f.write(str(questions_div))

        ps = soup.find_all('h2')
        for question in ps:
            try:
                options_ol = question.find_next_sibling('ol', class_='pointsa')
                options = options_ol.find_all('li')
                answer_area = question.find_next_sibling('div', class_='testanswer')
                p_elements = answer_area.find_all('p')
                answer = p_elements[0] if len(p_elements) > 0 else None
                explanation = p_elements[1] if len(p_elements) > 1 else None

                code_block_area = question.find_next_sibling('div', class_='codeblock')
                code_block = code_block_area.find('textarea', class_='xml') if code_block_area else None
                code_block = code_block.text.strip() if code_block else None

                question_text = re.sub(r'^\d+\.\s*', '', question.text.strip())
                options_text = [option.text.strip() for option in options]
                answer_text = re.sub(r'^Answer:\s*\(\w+\)\s*', '', answer.text.strip()) if answer else None
                explanation_text = explanation.text.strip().replace('Explanation:', '', 1) if explanation else None

                questions.append(Question(question_text, options_text, answer_text, explanation_text, code_block))
            except Exception as e:
                print(f"Failed to extract question with error {e}")
                continue

        return questions
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        return None


def scrap_javaguide():
    url = "https://www.javaguides.net/search/label/MCQ?&max-results=1000000"
    all_links = set()
    no_more_links = False

    links = {}
    while(not no_more_links):
        new_links, next_url = scrap_links_from_javaguide(url)
        links.update(new_links)
        current_size = len(all_links)
        all_links.update(new_links.values())
        new_links_count = len(all_links) - current_size
        print(f"Found {new_links_count} new links")
        if new_links_count == 0 or next_url is None:
            no_more_links = True
        else:
            url = next_url


    number_of_pages = 0
    number_of_questions = 0

    while links:
        sleep(.3)
        try:
            print("\n\n")
            key, value = links.popitem()
            print(f"Scraping {key} from {value} the total number of links left is {len(links)}")
            questions = scrap_questions_from_javaguide(value)
            filename = key + ".json"
            new_links = scrap_links_from_javaguide(value)

            print("Found the following links: ", len(new_links))

            for keyyy, valueee in new_links.items():
                if keyyy not in all_links:
                    all_links[keyyy] = valueee
                    links[keyyy] = valueee

            if(len(questions) == 0):
                print(f"Failed to scrapeee {key} from {value}")
                continue

            number_of_pages += 1
            number_of_questions += len(questions)
            print(f"Scraped {key} and wrote to {filename} successfully with {len(questions)} questions")
            write_questions_to_json(questions, filename)
        except Exception as e:
            print(f"Failed to scrape {key} from {value} with error {e}")
            continue

    print(f"Scraped {number_of_questions} questions from {number_of_pages} pages")




if __name__ == "__main__":
    scrap_javaguide()
