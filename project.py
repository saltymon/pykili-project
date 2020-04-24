import pymorphy2, nltk, os.path, string, csv
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


def count(pos_list, parameters):
    VERB_NOUN = 0
    VERB_ADVB = 0
    GRND_NOUN = 0
    GRND_ADVB = 0
    NOUN_NOUN = 0
    ADJF_NOUN = 0
    for i, pos in enumerate(pos_list):
        if pos == 'VERB' or pos == 'INFN' or pos == 'GRND':
            parameters['VERB'] += 1
        elif pos == 'NOUN':
            parameters['NOUN'] += 1
        elif pos == 'ADJF':
            parameters['ADJF'] += 1
        elif pos == 'NPRO':
            parameters['NPRO'] += 1
        elif pos == 'PRCL':
            parameters['PRCL'] += 1
        if i < len(pos_list) - 1:
            near_pos = pos_list[i + 1]
            if (pos == 'VERB' and near_pos == 'NOUN') or (pos == 'NOUN' and near_pos == 'VERB'):
                VERB_NOUN += 1
            elif (pos == 'VERB' and near_pos == 'ADVB') or (pos == 'ADVB' and near_pos == 'VERB'):
                VERB_ADVB += 1
            elif (pos == 'GRND' and near_pos == 'NOUN') or (pos == 'NOUN' and near_pos == 'GRND'):
                GRND_NOUN += 1
            elif (pos == 'GRND' and near_pos == 'ADVB') or (pos == 'ADVB' and near_pos == 'GRND'):
                GRND_ADVB += 1
            elif pos == 'NOUN' and near_pos == 'NOUN':
                NOUN_NOUN += 1
            elif pos == 'ADJF' and near_pos == 'NOUN':
                ADJF_NOUN += 1
    for key in parameters:
        if key != 'DYN' and key != 'SENTLEN':
            parameters[key] = parameters[key] / len(pos_list)
    parameters['DYN'] = (VERB_NOUN + VERB_ADVB + GRND_NOUN + GRND_ADVB)/(NOUN_NOUN + ADJF_NOUN)


def sent_count(sentences, parameters):
    tokens = 0
    for sentence in sentences:
        sentence = sentence.translate(str.maketrans('', '', string.punctuation))
        tokens += len(nltk.word_tokenize(sentence))
    parameters['SENTLEN'] = tokens / len(sentences)


def award(parameters):
    points = {
        'FIC' : 0,
        'PUB' : 0,
        'SCI' : 0,
        'DOC' : 0,
    }
    genres = list(points)
    csv_name = 'awards.csv'
    with open (csv_name, newline = '') as csv_f:
        reader = csv.DictReader(csv_f)
        for row in reader:
            prm_name = row['parameter']
            for genre in genres:
                if float(row[genre + '_down']) <= parameters[prm_name] <= float(row[genre + '_up']):
                    points[genre] += int(row[genre + '_award'])
                    # print(prm_name, parameters[prm_name], genre, row[genre + '_award'])
    for key, value in points.items():
        if value <= 2:
            points[key] = 0
    return points


def main():
    filename = input('Введите название файла с текстом: ')
    text = reader(filename)
    sentences = ru_sent_tokenize(text)
    tokens = tokenize(sentences)
    pos_list = pos_analyze(tokens)
    parameters = {
        'VERB' : 0.0,
        'NOUN' : 0.0,
        'ADJF' : 0.0,
        'NPRO' : 0.0,
        'PRCL' : 0.0,
        'DYN' : 0.0,
        'SENTLEN' : 0.0
    }
    count(pos_list, parameters)
    sent_count(sentences, parameters)
    points = award(parameters)
    sum_points = sum(points.values())
    percents = {}
    for key, value in points.items():
        num = round(value / sum_points * 100, 2)
        percents[key] = str(num) + '%'
    answer = ['Этот текст на ', percents['FIC'], ' относится к художественному стилю;\nна ', percents['PUB'],\
        ' – к публицистическому;\nна ', percents['SCI'], ' – к научному;\nна ', percents['DOC'], ' – к деловому.']
    print(''.join(answer))


if __name__ == '__main__':
    main()
