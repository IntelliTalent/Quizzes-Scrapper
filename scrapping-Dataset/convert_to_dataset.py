import os
import json
import re


root_dir = 'mcqs'


def read_jsons_in_folders():
    data = {}

    for dir_name, subdir_list, file_list in os.walk(root_dir):
        for fname in file_list:
            if fname.endswith('.json'):
                with open(os.path.join(dir_name, fname), 'r') as f:
                    filename_without_extension = os.path.splitext(fname)[0]
                    clean_fname = filename_without_extension.lstrip('0123456789')
                    data[clean_fname] = json.load(f)


    return data


def convert_to_dataset(data):
    dataset = []

    for fname, content in data.items():
        context_text = fname.strip('"').strip()

        for question in content:
            raw_answer_text = question.get('answer', None)
            raw_options_text = question.get('options', None)
            raw_question_text = question.get('question', None)

            if raw_answer_text and raw_options_text and raw_question_text:
                # Skip the question if any option contains 'images/'
                if any('images/' in option for option in raw_options_text):
                    continue

                question_text = re.sub('^[0-9.)*]+', '', raw_question_text).lstrip()
                options_text = [re.sub('`', '', option.lstrip()) for option in raw_options_text]
                answer_text = re.sub('^[A-Z]+[.)]+', '', raw_answer_text.lstrip().rstrip())
                explanation_text = question.get('explanation', None)
                code_block = question.get('codeblock', None)

                explanation_text = explanation_text.lstrip('Explanation:').lstrip() if explanation_text else None
                code_block = code_block.lstrip('Code:').lstrip() if code_block else None


                dataset.append({
                    'context': context_text,
                    'question': question_text,
                    'options': options_text,
                    'answer': answer_text,
                    'explanation': explanation_text,
                    'codeblock': code_block
                })

    return dataset



import pandas as pd

def print_unique_contexts(dataset):
    # Extract the 'context' values from the dataset
    contexts = [item['context'] for item in dataset]

    # Convert to a DataFrame and drop duplicates
    unique_contexts_df = pd.DataFrame(contexts, columns=['context']).drop_duplicates()

    # Write the DataFrame to a CSV file
    unique_contexts_df.to_csv('unique_contexts.csv', index=False)

if __name__ == "__main__":
    data = read_jsons_in_folders()
    dataset = convert_to_dataset(data)

    print(f"Total questions: {len(dataset)}")

    # Call the function to print unique contexts
    print_unique_contexts(dataset)

    with open('dataset.json', 'w') as f:
        json.dump(dataset, f, indent=4)
