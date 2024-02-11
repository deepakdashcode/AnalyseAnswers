import csv
import google.generativeai as genai
import os
import threading


all_keys = open('api_keys.txt').read().split('\n')
length = len(all_keys)
ind = 0


def getOutput(prompt: str, all_keys: list, ind: int):
    genai.configure(api_key=all_keys[ind])
    print('api used = ', all_keys[ind])
    gemini_pro_model = genai.GenerativeModel('gemini-pro')
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
            temperature=0.1
        )
    )
    return response.text


def getResponse(ques: str, ans: str):
    global ind
    ind = (ind + 1) % length
    prompt = (f'I want you to help me evaluate the answers of my students and provide appropriate marks'
              f'The Question is\n'
              f'{ques}'
              f'\n'
              f'And the answer written is\n'
              f'{ans}'
              f'\n'
              f'The total marks are written above in brackets with the question\n'
              f'analyze it with respect to organizational behaviour if possible.\n'
              f'How much should he get. Simply Give me a number. After that explain the points where he could have '
              f'improved')
    return getOutput(prompt, all_keys, ind)


if __name__ == '__main__':
    print(all_keys)

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
    def get_list(key: str):
        evaluated_answers[key] = []
        for i in range(len(header)):
            evaluated_answers[key].append(getResponse(header[i], answers[key][i]))
        print(evaluated_answers[key])

    all_threads = []
    for k in answers.keys():
        t = threading.Thread(target=get_list, args=[k])
        all_threads.append(t)
        t.start()

    for thread in all_threads:
        thread.join()
    for key in evaluated_answers:
        file_name = key + ".md"
        details = f'REG NO: {key}\n\n'
        for i in range(len(header)):
            details += "**" + header[i].strip() + "**\n\n"
            details += answers[key][i] + '\n\n'
            details += evaluated_answers[key][i] + '\n\n'

        with open(file_name, 'w') as f:
            f.write(details)
        os.system(f'pandoc {file_name} -o {key}.pdf')
