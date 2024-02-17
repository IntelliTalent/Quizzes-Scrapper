# from flask import Flask, request, jsonify
import json
import random

# app = Flask(__name__)

with open("context_skills_mapping.json", "r") as f:
    context_skills_mapping = json.load(f)

with open("quizzes_dataset.json", "r") as f:
    quiz_dataset = json.load(f)


quiz_data_by_context = {}
for question in quiz_dataset:
    context = question["context"]
    if context not in quiz_data_by_context:
        quiz_data_by_context[context] = []
    quiz_data_by_context[context].append(question)


def get_top_matching_contexts(skills_array, number_of_context=10):
    context_match_count = {}
    for context, matched_skills in context_skills_mapping.items():
        match_count = sum(1 for skill in skills_array if skill in matched_skills)
        context_match_count[context] = match_count
    sorted_contexts = sorted(context_match_count.items(), key=lambda x: x[1], reverse=True)
    return [context for context, _ in sorted_contexts[:number_of_context]]


def generate_random_questions(contexts, num_questions_per_context=20):
    selected_questions = []

    for context in contexts:
        if context not in quiz_data_by_context:
            continue
        context_questions = quiz_data_by_context[context]
        selected_questions.extend(random.sample(context_questions, min(num_questions_per_context, len(context_questions))))

    return selected_questions

# @app.route("/get_top_matching_contexts", methods=["POST"])
# def top_matching_contexts():
#     data = request.json
#     skills_array = data.get("skills_array")
#     if skills_array is None:
#         return jsonify({"error": "'skills_array' parameter is required."}), 400
#     number_of_context = data.get("number_of_context", 10)
#     result = get_top_matching_contexts(skills_array, number_of_context)
#     return jsonify(result)

# @app.route("/generate_questions", methods=["POST"])
# def generate_questions():
#     data = request.json
#     context = data.get("context")
#     num_questions = data.get("num_questions")
#     if context is None or num_questions is None:
#         return jsonify({"error": "Both 'context' and 'num_questions' are required parameters."}), 400
#     random_questions = generate_random_questions(context, num_questions)
#     return jsonify(random_questions)

if __name__ == '__main__':
    skills_array = ['backend development', 'Node.js', 'Express.js', 'JavaScript', 'MySQL']  # Replace with your array of skills
    top_matching_contexts = get_top_matching_contexts(skills_array)
    print("Top matching contexts:")
    for context in top_matching_contexts:
        print(f"Context: {context}")
    questions = generate_random_questions(top_matching_contexts)
    print(questions)
