import csv
import google.generativeai as genai
import os

api_key = 'AIzaSyDLXFmeoDjcXgcItt0PaoUE0y9-oKXG4tI'
genai.configure(api_key=api_key)

gemini_pro_model = genai.GenerativeModel('gemini-pro')

def getOutput(prompt: str):
    response = gemini_pro_model.generate_content(
        prompt,
        safety_settings=[
            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
             'threshold': 'block_none'
             },
            {'category': 'HARM_CATEGORY_HATE_SPEECH',
             'threshold': 'block_none'
             },
            {'category': 'HARM_CATEGORY_HARASSMENT',
             'threshold': 'block_none'
             },
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
             'threshold': 'block_none'
             }
        ],
        generation_config=genai.types.GenerationConfig(
            temperature=0.3
        )
    )
    return response.text


def getResponse(ques: str, ans: str):
    prompt = (f'I want you to help me evaluate the answers of my students and provide appropriate marks'
              f'The Question is\n'
              f'{ques}'
              f'\n'
              f'And the answer written is\n'
              f'{ans}'
              f'\n'
              f'The total marks are written above in brackets with the question\n'
              f'Be a little liberal with the markings, and also analyze it with respect to organizational behaviour if possible\n'
              f'How much should he get. Simply Give me a number. After that explain the points where he could have improved')
    return getOutput(prompt)


file = open('sample.csv')
csvreader = csv.reader(file)
header = []
header = next(csvreader)
print(header)

answers = {}
for row in csvreader:
    answers[row[-3]] = []
    l = len(row)
    for i in range(-4, -l, -1):
        answers[row[-3]].append(row[i])

    answers[row[-3]].reverse()

evaluated_answers = {}
print(answers)
header.pop(0)
header.pop()
header.pop()
header.pop()
print(header)
for key in answers:
    evaluated_answers[key] = []
    for i in range(len(header)):
        evaluated_answers[key].append(getResponse(header[i], answers[key][i]))

print(evaluated_answers)

for key in evaluated_answers:
    file_name = key + ".md"
    details = f'REG NO: {key}\n\n'
    for i in range(len(header)):
        details += "**" + header[i].strip() + "**\n\n"
        details += answers[key][i] + '\n\n'
        details += evaluated_answers[key][i] + '\n\n'

    with open(file_name, 'w') as f:
        f.write(details)
    # os.system(f'pandoc {file_name} -o {key}.pdf')
