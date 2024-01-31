import requests
from bs4 import BeautifulSoup, NavigableString
from typing import Dict, List, Union
import re
import json
import os
from urllib.parse import urlparse
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



def scrape_links(url, titles=[]):

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        div_elements = soup.find_all('div')

        links = {}
        for div in div_elements:
            h3_elements = div.find_all('h3')
            for h3 in h3_elements:
                if h3.text.strip() in titles:
                    ul = h3.find_next_sibling('ul')
                    if ul:
                        a_elements = ul.find_all('a', href=True)
                        for a in a_elements:
                            if ("mcq" in a.text.strip().lower()):
                                links[a.text.strip()] = a['href']
        return links
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        return None


def ExtractQuestions(soup)-> List[Question]:
    # Find the first <p> tag
    first_p = soup.find('p')

    # Remove the first <p> tag
    if first_p:
        first_p.decompose()

    pattern = r'<p>.*?<div class="collapseomatic_content".*?</div>'
    matches = re.findall(pattern, str(soup), re.DOTALL)

    questions: List[Question] = []

    for match in matches:
        try:
            soup = BeautifulSoup(match, 'html.parser')

            # Find the question text
            question_text = soup.find('p').contents[0].strip()

            # Remove the leading number from the question
            question_text = re.sub(r'^\d+\.\s', '', question_text)

            # Find all options
            options = soup.find('p').find_all('br')
            options_text = [option.next_sibling.strip() for option in options if re.match(r'^[a-z0-9]\)', option.next_sibling.strip())]

            # Find the answer and explanation
            answer_tag = soup.find('div', class_='collapseomatic_content')
            answer_text = answer_tag.contents[0].strip()
            answer_text = re.sub(r'^Answer:\s', '', answer_text)
            explanation_text = answer_tag.contents[2].strip()
            explanation_text = re.sub(r'^Explanation:\s', '', explanation_text)

            questions.append(Question(question_text, options_text, answer_text, explanation_text))
        except Exception as e:
            print(f"Failed to extract question with error {e}")
            continue

    return questions


def scrape_python_questions(url):
    # Send a GET request to the URL
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the question elements on the page
        entry_content = soup.find('div', class_='entry-content')

        questions = ExtractQuestions(entry_content)

        return questions
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        return None

def scrapPage(title, url) -> Dict[str, Union[str, List[Question]]]:
    questions = scrape_python_questions(url)
    return {"title": title, "questions": questions}

MCQ_PATH = "./javatpoint-mcq"

def write_questions_to_json(pageQuestions, filename):
    filename = os.path.join(MCQ_PATH, filename)
    with open(filename, 'w') as f:
        json.dump(pageQuestions, f, default=lambda o: o.__dict__, indent=4)


def get_links_from_dict_page(url):
    # Send a GET request to the URL
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the question elements on the page
        entry_content = soup.findAll('div', class_='sf-section')

        links = {}
        for content in entry_content:
            aaa = content.find_all('a', href=True)
            for a in aaa:
                links[a.text.strip()] = a['href']

        return links

    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        return None

def scrap_sanfoundry():
    url = "https://www.sanfoundry.com/"
    titles_matching = ["Competitive Exams Preparation", "Interview Preparation","Programming & IT MCQs", "Computer Science MCQs", ""]
    links = scrape_links(url, titles_matching)
    number_of_pages = 0
    number_of_questions = 0

    while links:
        try:
            print("\n\n")
            key, value = links.popitem()
            print(f"Scraping {key} from {value} the total number of links left is {len(links)}")

            pageQuestions = scrapPage(key, value)
            filename = pageQuestions['title'] + ".json"

            if(len(pageQuestions['questions']) == 0):
                print(f"Failed to scrape {key} from {value} we will try to get the links from the page")
                new_links = get_links_from_dict_page(value)
                if new_links:
                    print(f"Found {len(new_links)} links")
                    links.update(new_links)
                continue

            number_of_pages += 1
            number_of_questions += len(pageQuestions['questions'])
            print(f"Scraped {key} and wrote to {filename} successfully with {len(pageQuestions['questions'])} questions")
            write_questions_to_json(pageQuestions['questions'], filename)
        except Exception as e:
            print(f"Failed to scrape {key} from {value} with error {e}")
            continue
    print(f"Scraped {number_of_questions} questions from {number_of_pages} pages")




def scrap_links_from_javapoint(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = {}
    assss= soup.find_all('a', href=True)

    for a in assss:
        href = a['href']
        if href.startswith('#'):
            continue

        if 'tutorial' in href and not href.startswith('https:'):
            href = url + href

        parsed = urlparse(href)
        if bool(parsed.netloc) and bool(parsed.scheme) and href.startswith('https://www.javatpoint.com/'):
            href = href.replace('tutorial', 'mcq')
            link_text = a.text.strip()
            links[link_text] = href

    return links


def scrap_questions_from_javapoint(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        questions = []
        ps = soup.find_all('p', class_='pq')
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


def scrap_javapoint():
    url = "https://www.javatpoint.com/"
    all_links = scrap_links_from_javapoint(url)
    links = all_links.copy()
    number_of_pages = 0
    number_of_questions = 0

    while links:
        sleep(1)
        try:
            print("\n\n")
            key, value = links.popitem()
            print(f"Scraping {key} from {value} the total number of links left is {len(links)}")
            questions = scrap_questions_from_javapoint(value)
            filename = key + ".json"
            new_links = scrap_links_from_javapoint(value)

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
    scrap_javapoint()
