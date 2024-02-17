# %%
# !pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# !pip install transformers torch
# !pip install spacy

# %%
# !git clone https://github.com/Waer1/quizes-scrapper/

# %%
import spacy
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor
# !python3 -m spacy download en
# !python3 -m spacy download en_core_web_lg

# %%
# num_cores = os.cpu_count()
# print(f"Number of available CPU cores: {num_cores}")

# %%


# %%
skills_context_directory = './raw-data/'

skills_dataset = skills_context_directory +  'extracted_skills.txt'
context_dataset = skills_context_directory + 'contexts.csv'

unique_skills_dataset = 'unique_skills.csv'
unique_contexts_dataset = 'unique_context.csv'



# %%

# # Check if the unique_skills.csv file exists
# if os.path.exists(unique_skills_dataset):
#     # Load the existing unique skills dataset
#     unique_skills_df = pd.read_csv(unique_skills_dataset)
#     unique_skills_set = set(unique_skills_df['Skill'])
# else:
#     # Read the skills dataset
#     df = pd.read_csv(skills_dataset)

#     # Initialize an empty set to store unique skills
#     unique_skills_set = set()

#     # Load the pre-trained spaCy model
#     nlp = spacy.load('en_core_web_lg')

#     # Iterate over each row in the skills dataset
#     for skills_str in df['skills'].unique():
#         if pd.isna(skills_str):
#             continue

#         # Split skills based on commas and convert to lowercase
#         skills_list = [skill.strip().lower() for skill in skills_str.split(',')]

#         # Add each unique skill to the set
#         for skill in skills_list:
#             if skill not in unique_skills_set:
#                 unique_skills_set.add(skill)

#     # Convert the set of unique skills to a DataFrame
#     unique_skills_df = pd.DataFrame({'Skill': list(unique_skills_set)})

#     # Save the unique skills DataFrame to a CSV file
#     unique_skills_df.to_csv(unique_skills_dataset, index=False)

# # Print the total number of unique skills
# print("Total Unique Skills:", len(unique_skills_set))

# %%

# Check if the unique_skills.csv file exists
if os.path.exists(unique_skills_dataset):
    # Load the existing unique skills dataset
    unique_skills_df = pd.read_csv(unique_skills_dataset)
    unique_skills_set = set(unique_skills_df['skills'])
else:
    with open(skills_dataset, 'r') as file:
        skills = file.readlines()

    # Remove leading and trailing whitespaces and filter empty lines
    skills = [skill.strip() for skill in skills if skill.strip()]

    # Create a DataFrame from the list of skills
    unique_skills_set = pd.DataFrame({'skills': skills})

    # Save the unique skills DataFrame to a CSV file
    unique_skills_set.to_csv(unique_skills_dataset, index=False)

# Print the total number of unique skills
print("Total Unique Skills:", len(unique_skills_set))

# %%

# Check if the unique_contexts.csv file exists
if os.path.exists(unique_contexts_dataset):
    # Load the existing unique context dataset
    unique_contexts_df = pd.read_csv(unique_contexts_dataset)
    unique_contexts_set = set(unique_contexts_df['Context'])
else:
    # Read the context dataset
    contexts_df = pd.read_csv(context_dataset)

    # Initialize an empty set to store unique contexts
    unique_contexts_set = set()

    # Iterate over each row in the context dataset
    for context_str in contexts_df['Context']:
        if pd.isna(context_str):  # Skip nan values
            continue

        # Strip whitespaces and convert to lowercase
        context = context_str.strip().lower()

        # Add each unique context to the set
        if context not in unique_contexts_set:
            unique_contexts_set.add(context)

    # Convert the set of unique contexts to a DataFrame
    unique_contexts_df = pd.DataFrame({'Context': list(unique_contexts_set)})

    # Save the unique context DataFrame to a CSV file
    unique_contexts_df.to_csv(unique_contexts_dataset, index=False)

# Print the total number of unique contexts
print("Total Unique Contexts:", len(unique_contexts_set))


# %%
context_skills_mapping = {}

# %%
import concurrent.futures
import json
import spacy
import pandas as pd

# Load pre-trained spaCy model with word embeddings
nlp = spacy.load('en_core_web_lg')

context_skills_mapping = {}

# Function to process each context row and find related skills
def process_context(context_row):
    context_name = context_row.Context
    context_text = context_row.Context.lower()  # Adjust the column name to match your DataFrame

    context_skills = []
    num_matched_skills = 0  # Counter for matched skills in each iteration

    # Tokenize and embed context text
    context_doc = nlp(context_text)

    for skill in unique_skills_set:
        # Tokenize and embed skill text
        skill_doc = nlp(skill.lower())  # Convert to lowercase for consistency

        # Calculate similarity between context and skill embeddings
        similarity = context_doc.similarity(skill_doc)

        # Define a threshold for similarity
        threshold = 0.7

        # If similarity is above the threshold, consider the skill related to the context
        if similarity > threshold:
            context_skills.append(skill)
            num_matched_skills += 1

    return context_name, context_skills, num_matched_skills

# Create a ThreadPoolExecutor with 5 threads
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Submit each context row to the executor for processing
    future_to_row = {executor.submit(process_context, context_row): context_row for context_row in unique_contexts_df.itertuples()}
    print("waer is here")
    # Iterate over completed futures
    for future in concurrent.futures.as_completed(future_to_row):
        context_name, context_skills, num_matched_skills = future.result()
        context_skills_mapping[context_name] = context_skills
        print(f"Context: {context_name}, Matched Skills: {num_matched_skills}")

        # Write to JSON file after each step
        with open("context_skills_mapping.json", "w") as f:
            json.dump(context_skills_mapping, f)




# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%


# %%



