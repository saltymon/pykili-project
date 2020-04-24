import pymorphy2, nltk, os.path
from rusenttokenize import ru_sent_tokenize
nltk.download('punkt')


def reader(filename):
    while not os.path.exists(filename):
        filename = input('Такого файла нет, попробуйте ещё раз: ')
    with open(filename, encoding='utf-8') as f:
        text = f.read()
    return text


def tokenize(sentences):
    tokens = []
    for sentence in sentences:
        tokens.extend(nltk.word_tokenize(sentence))
    return tokens


def pos_analyze(tokens):
    morph = pymorphy2.MorphAnalyzer()
    pos_list = []
    for token in tokens:
        p = morph.parse(token)[0]
        pos_list.append(p.tag.POS)
    return pos_list


def main():
    filename = input('Введите название файла с текстом: ')
    text = reader(filename)
    sentences = ru_sent_tokenize(text)
    tokens = tokenize(sentences)
    pos_list = pos_analyze(tokens)
    
    answer = ['Этот текст на ', ' относится к художественному стилю;\nна ', ' – к публицистическому;\nна ', ' – к научному;\nна ', ' – к деловому.']
    print(''.join(answer))


if __name__ == '__main__':
    main()