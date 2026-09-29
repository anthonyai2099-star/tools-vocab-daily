import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r"\{id:'([^']+)',word:'([^']+)',phonetic:'([^']+)',meaning:'([^']+)',pos:'([^']*)',theme:'([^']+)'\}"
entries = re.findall(pattern, content)

seen = set()
unique = []
for e in entries:
    if e[1].lower() not in seen:
        seen.add(e[1].lower())
        unique.append(e)

print(f'Total unique: {len(unique)}')

with open('../tools-vocab-daily-mini/utils/vocab.js', 'w', encoding='utf-8') as out:
    out.write('const BUILT_IN_VOCAB = [\n')
    for id_, word, phonetic, meaning, pos, theme in unique:
        out.write(f"  {{id:'{id_}',word:'{word}',phonetic:'{phonetic}',meaning:'{meaning}',pos:'{pos}',theme:'{theme}'}},\n")
    out.write('];\n\nmodule.exports = { BUILT_IN_VOCAB };\n')

print('Done')
