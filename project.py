import nltk, os.path, string, csv, re
from rusenttokenize import ru_sent_tokenize
from pymystem3 import Mystem
nltk.download('punkt')


def reader(filename):
    while not os.path.exists(filename):
        filename = input('Такого файла нет, попробуйте ещё раз: ')
    with open(filename, encoding='utf-8') as f:
        text = f.read()
    text = ''.join([line for line in text.split('\n') if line.strip() != ''])
    return text


def pos_analyze(text):
    m = Mystem()
    a = 'analysis'
    pos_list = []
    mystemmed = m.analyze(text)
    for record in mystemmed:
        if a in record and record[a]:
            gr = record[a][0]['gr']
            pos = re.split(',|=', gr)[0]
            pos_list.append(pos)
    return pos_list


def count(pos_list, parameters):
    V_S = 0
    V_ADV = 0
    S_S = 0
    A_S = 0
    for i, pos in enumerate(pos_list):
        if pos == 'V':
            parameters['V'] += 1
        elif pos == 'S':
            parameters['S'] += 1
        elif pos == 'A':
            parameters['A'] += 1
        elif pos == 'SPRO':
            parameters['SPRO'] += 1
        elif pos == 'PART':
            parameters['PART'] += 1
        if i < len(pos_list) - 1:
            near_pos = pos_list[i + 1]
            if (pos == 'V' and near_pos == 'S') or (pos == 'S' and near_pos == 'V'):
                V_S += 1
            elif (pos == 'V' and near_pos == 'ADV') or (pos == 'ADV' and near_pos == 'V'):
                V_ADV += 1
            elif pos == 'S' and near_pos == 'S':
                S_S += 1
            elif pos == 'A' and near_pos == 'S':
                A_S += 1
    for key in parameters:
        if key != 'DYN' and key != 'SENTLEN':
            parameters[key] = parameters[key] / len(pos_list)
    parameters['DYN'] = (V_S + V_ADV)/(S_S + A_S)


def sent_count(sentences, parameters):
    words = 0
    for sentence in sentences:
        sentence = sentence.translate(str.maketrans('', '', string.punctuation))
        words += len(nltk.word_tokenize(sentence))
    parameters['SENTLEN'] = words / len(sentences)


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
                if float(row[genre + '_down']) <= parameters[prm_name] <= float(row[genre + '_up']) and row[genre + '_award'] != '0':
                    points[genre] += int(row[genre + '_award'])
                    print(prm_name, parameters[prm_name], genre, row[genre + '_award'])
    for key, value in points.items():
        if value <= 2:
            points[key] = 0
    return points


def main():
    filename = input('Введите название файла с текстом в кодировке utf-8: ')
    text = reader(filename)
    sentences = ru_sent_tokenize(text)
    pos_list = pos_analyze(text)
    parameters = {
        'V' : 0.0,
        'S' : 0.0,
        'A' : 0.0,
        'SPRO' : 0.0,
        'PART' : 0.0,
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
