import google.generativeai as genai
import os

with open('key.txt', 'r') as file:
    key = file.read().strip()

genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = """Please generate a list of 80 words that are simple to draw and easy to guess for a Quick, Draw! style game. The words should be:

1. Nouns representing common objects, animals, or simple concepts
2. Easily recognizable and drawable within 20 seconds
3. Suitable for players of all ages
4. Diverse, covering different categories (e.g., animals, household items, nature, food)

Please provide them in a list string format, one word per line. Avoid overly complex or abstract concepts.

Example words to guide your output:
- cat
- dog


Remember to keep the words simple and universally recognizable. Adjust your creativity to balance between interesting choices and easily guessable items."""

generation_config = genai.GenerationConfig(
    temperature=0.6
)

response = model.generate_content(prompt)

raw_text = response.candidates[0].content.parts[0].text

lines = raw_text.split('\n')

#print(lines)
words = []

for word in lines[2:]:
    if word != '```':
        words.append(word[2:])
print(words)

with open('words.txt','w') as file:
    for word in words:
       file.write(word + '\n')