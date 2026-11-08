#!/usr/bin/env python3
"""由 data/ 產生 mini-english.md。

用法：python build.py

資料夾結構：
    data/spec.md        規格本文（手寫），含 {{PLACEHOLDER}}
    data/*.tsv          詞表與附錄資料
    tools/count_1w.txt  Google Web Trillion Word Corpus 詞頻（只用於報告）

產出的 mini-english.md 內的「附錄：完整詞表」是唯一的權威詞表，
check.py、prompts/system.md、lexicon.tsv 都從那裡讀取。
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from morph import forms_of, third, ing, ed, compar, plural

HERE = Path(__file__).parent
DATA = HERE / 'data'

CATS = ['pron', 'gram', 'num', 'time', 'place', 'nature', 'verb', 'adj', 'noun', 'social', 'abstr']
CAT_NAMES = {
    'pron': '代詞・指示', 'gram': '語法（功能詞）', 'num': '數量・比例', 'time': '時間',
    'place': '方位・地點', 'nature': '自然・天氣', 'verb': '動作', 'adj': '性質',
    'noun': '事物', 'social': '社交・人', 'abstr': '抽象概念',
}

# ── IPA ─────────────────────────────────────────────────────────────────────
ARPA = {
    'AA': 'ɑ', 'AE': 'æ', 'AH': 'ʌ', 'AO': 'ɔ', 'AW': 'aʊ', 'AY': 'aɪ',
    'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð', 'EH': 'ɛ', 'ER': 'ɝ', 'EY': 'eɪ',
    'F': 'f', 'G': 'ɡ', 'HH': 'h', 'IH': 'ɪ', 'IY': 'iː', 'JH': 'dʒ', 'K': 'k',
    'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'OW': 'oʊ', 'OY': 'ɔɪ',
    'P': 'p', 'R': 'ɹ', 'S': 's', 'SH': 'ʃ', 'T': 't', 'TH': 'θ', 'V': 'v',
    'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ', 'UH': 'ʊ', 'UW': 'uː',
}
# 功能詞與多音字：指定最常用的一個讀音（General American）
IPA_OVERRIDE = {
    'the': 'ðə', 'a': 'ə', 'an': 'ən', 'of': 'əv', 'to': 'tuː', 'and': 'ænd',
    'for': 'fɔːr', 'can': 'kæn', 'as': 'æz', 'was': 'wəz', 'were': 'wɜːr',
    'I': 'aɪ', 'at': 'æt', 'in': 'ɪn', 'is': 'ɪz', 'it': 'ɪt', 'on': 'ɑn',
    'or': 'ɔːr', 'not': 'nɑːt', 'no': 'noʊ', 'do': 'duː', 'does': 'dʌz',
    'did': 'dɪd', 'have': 'hæv', 'has': 'hæz', 'had': 'hæd', 'will': 'wɪl',
    'would': 'wʊd', 'could': 'kʊd', 'should': 'ʃʊd', 'may': 'meɪ', 'might': 'maɪt',
    'must': 'mʌst', 'that': 'ðæt', 'this': 'ðɪs', 'there': 'ðɛr', 'their': 'ðɛr',
    'them': 'ðɛm', 'they': 'ðeɪ', 'we': 'wiː', 'you': 'juː', 'he': 'hiː',
    'she': 'ʃiː', 'my': 'maɪ', 'by': 'baɪ', 'why': 'waɪ', 'one': 'wʌn', 'eye': 'aɪ',
    'said': 'sɛd', 'been': 'bɪn', 'being': 'biːɪŋ', 'read': 'ɹiːd', 'live': 'lɪv',
    'close': 'kloʊs', 'lead': 'liːd', 'wind': 'wɪnd', 'tear': 'tɪr', 'bow': 'baʊ',
    'row': 'ɹoʊ', 'sow': 'soʊ', 'object': 'ˈɑːbdʒɛkt', 'minute': 'ˈmɪnɪt',
    'second': 'ˈsɛkənd', 'schedule': 'ˈskɛdʒuːl', 'clothes': 'kloʊðz',
    'English': 'ˈɪŋɡlɪʃ', 'Chinese': 'ˈtʃaɪniːz', 'bus': 'bʌs', 'women': 'ˈwɪmɪn',
    'people': 'ˈpiːpəl', 'water': 'ˈwɔːtər', 'money': 'ˈmʌni', 'money.': 'ˈmʌni',
    'other': 'ˈʌðər', 'mother': 'ˈmʌðər', 'father': 'ˈfɑːðər', 'brother': 'ˈbrʌðər',
    'together': 'təˈɡɛðər', 'because': 'bɪˈkɔːz', 'again': 'əˈɡɛn',
    'business': 'ˈbɪznəs', 'few': 'fjuː', 'new': 'nuː', 'use': 'juːz',
    'used': 'juːzd', 'beautiful': 'ˈbjuːtɪfəl', 'idea': 'aɪˈdiːə', 'area': 'ˈɛriːə',
    'ocean': 'ˈoʊʃən', 'usual': 'ˈjuːʒuəl', 'vision': 'ˈvɪʒən', 'fever': 'ˈfiːvər',
    'product': 'ˈprɑːdəkt', 'profit': 'ˈprɑːfɪt', 'police': 'pəˈliːs',
}


def arpa_to_ipa(phones):
    out = []
    for i, p in enumerate(phones):
        base = p.rstrip('012')
        stress = p[len(base):]
        if base == 'AH':
            out.append('ʌ' if stress in ('1', '2') else 'ə')
        elif base == 'IY' and stress == '0':
            out.append('i')          # 非重讀的長母音變短音
        elif base == 'UW' and stress == '0':
            out.append('u')
        elif base == 'ER':
            out.append('ɝ' if stress == '1' else 'ɚ')
        else:
            out.append(ARPA[base])
    # 重音符號：主重音 ˈ，次重音 ˌ（放在該音節的音節起始輔音之前）
    VOWELS = set('AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW'.split())
    marks = []
    for i, p in enumerate(phones):
        base = p.rstrip('012')
        stress = p[len(base):]
        if base in VOWELS and stress in ('1', '2'):
            j = i
            while j - 1 >= 0 and phones[j - 1].rstrip('012') not in VOWELS:
                j -= 1
            marks.append((j, 'ˈ' if stress == '1' else 'ˌ'))
    for i, m in sorted(marks, reverse=True):
        out.insert(i, m)
    return ''.join(out)


def load_ipa():
    try:
        import cmudict
    except ImportError:
        print('⚠️  沒有裝 cmudict，IPA 會留空（pip install cmudict）', file=sys.stderr)
        return {}
    d = cmudict.dict()
    out = {}
    for w, prons in d.items():
        out[w] = arpa_to_ipa(prons[0])
    return out


# ── 詞表 ─────────────────────────────────────────────────────────────────────
def load_words():
    words = []
    for cat in CATS:
        path = DATA / f'{cat}.tsv'
        lines = path.read_text(encoding='utf-8').splitlines()
        for line in lines[1:]:
            if not line.strip():
                continue
            w, level, pos, zh = line.split('\t')
            words.append(dict(word=w, cat=cat, level=level, pos=pos, zh=zh))
    return words


def load_irregular():
    out = {}
    lines = (DATA / 'irregular.tsv').read_text(encoding='utf-8').splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split('\t')
        out[parts[0]] = parts[1:]
    return out


def load_table(name):
    lines = (DATA / name).read_text(encoding='utf-8').splitlines()
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:] if l.strip()]


# ── 例子 ─────────────────────────────────────────────────────────────────────
EXAMPLES = {
    'go': 'go to work', 'come': 'come home', 'eat': 'eat rice', 'drink': 'drink water',
    'sleep': 'sleep at night', 'read': 'read a book', 'write': 'write a letter',
    'say': 'say hello', 'tell': 'tell me', 'ask': 'ask a question', 'see': 'see a doctor',
    'look': 'look at the map', 'watch': 'watch a movie', 'hear': 'hear music',
    'give': 'give me the key', 'take': 'take a bus', 'get': 'get a coffee',
    'put': 'put it on the table', 'make': 'make dinner', 'buy': 'buy food',
    'sell': 'sell fruit', 'pay': 'pay the bill', 'open': 'open the door',
    'close': 'close the window', 'start': 'start work', 'stop': 'stop the car',
    'wait': 'wait for the bus', 'work': 'work in an office', 'play': 'play with a child',
    'study': 'study English', 'learn': 'learn a new word', 'teach': 'teach students',
    'help': 'help my friend', 'use': 'use a computer', 'find': 'find my keys',
    'lose': 'lose my phone', 'keep': 'keep the book', 'send': 'send an email',
    'bring': 'bring water', 'move': 'move to a new city', 'change': 'change my job',
    'grow': 'grow flowers', 'live': 'live in a big city', 'die': 'die young',
    'meet': 'meet my friend', 'visit': 'visit my parents', 'drive': 'drive to work',
    'ride': 'ride a bike', 'fly': 'fly to another country', 'cook': 'cook dinner',
    'wash': 'wash my hands', 'clean': 'clean the room', 'cut': 'cut the bread',
    'wear': 'wear a coat', 'feel': 'feel happy', 'hurt': 'hurt my back',
    'want': 'want water', 'try': 'try again', 'like': 'like this book',
    'love': 'love my family', 'hate': 'hate cold weather', 'begin': 'begin a new job',
    'finish': 'finish my work', 'choose': 'choose a chair', 'decide': 'decide to go',
    'hope': 'I hope so', 'wish': 'wish you a good day', 'remember': 'remember her name',
    'forget': 'forget the time', 'know': 'know the answer', 'think': 'I think so',
    'happen': 'what happened?', 'become': 'become a teacher', 'stay': 'stay at home',
    'leave': 'leave the room', 'arrive': 'arrive on time', 'return': 'return home',
    'call': 'call a friend', 'sing': 'sing a song', 'dance': 'dance with music',
    'swim': 'swim in the sea', 'jump': 'jump high', 'climb': 'climb the mountain',
    'fall': 'fall down', 'push': 'push the door', 'pull': 'pull the door',
    'throw': 'throw the ball', 'catch': 'catch the ball', 'win': 'win the game',
    'rest': 'rest a little', 'raise': 'raise your hand', 'share': 'share the food',
    'follow': 'follow me', 'lead': 'lead the group', 'hit': 'hit the ball',
    'enter': 'enter the room', 'pass': 'pass the salt', 'empty': 'empty the box',
    'ring': 'the phone rings', 'spend': 'spend money', 'allow': 'allow me to go',
    'include': 'include the price', 'believe': 'believe me', 'explain': 'explain it again',
    'describe': 'describe the room', 'support': 'support a friend',
    'build': 'build a house', 'protect': 'protect your family', 'seem': 'seem easy',
    'appear': 'appear at the door', 'exist': 'does it exist?', 'provide': 'provide food',
    'receive': 'receive a letter', 'accept': 'accept the food', 'understand': 'I understand',
    'talk': 'talk to a friend', 'reach': 'reach the shop', 'repeat': 'repeat the word',
    'check': 'check the time', 'order': 'order the food', 'expect': 'I expect rain',
    'agree': 'I agree', 'count': 'count the money', 'join': 'join the game',
    'dream': 'have a dream', 'marry': 'marry a friend', 'taste': 'taste the food',
    'smell': 'smell the coffee', 'touch': 'touch the wall', 'paint': 'paint the wall',
    'draw': 'draw a picture', 'feed': 'feed the child', 'hang': 'hang the coat',
    'spread': 'spread the map', 'cover': 'cover the table', 'fill': 'fill the cup',
    'lock': 'lock the door', 'knock': 'knock at the door', 'wave': 'wave goodbye',
    'point': 'point to the door', 'smile': 'smile at me', 'laugh': 'laugh together',
    'cry': 'cry a little', 'shout': 'shout for help', 'sign': 'sign your name',
    'print': 'print a photo', 'copy': 'copy the message', 'save': 'save money',
    'add': 'add some water', 'show': 'show me', 'cause': 'cause a problem',
    'prepare': 'prepare dinner', 'continue': 'continue to work', 'notice': 'I notice a noise',
    'travel': 'travel by train', 'translate': 'translate the words',
    'behave': 'behave well', 'heal': 'heal fast', 'borrow': 'borrow a book',
    'lend': 'lend me money', 'rent': 'rent a room', 'deliver': 'deliver the food',
    'offer': 'offer help', 'affect': 'affect the price', 'increase': 'increase the price',
    'decrease': 'decrease the price', 'complete': 'complete the work',
    'compare': 'compare the 2', 'discuss': 'discuss the plan', 'refuse': 'refuse the offer',
    'avoid': 'avoid the busy road', 'prevent': 'prevent a fire', 'improve': 'improve the quality',
    'develop': 'develop a plan', 'produce': 'produce food', 'create': 'create a story',
    'destroy': 'destroy the old house', 'manage': 'manage a group', 'depend': 'depend on the weather',
    'remain': 'remain at home', 'contain': 'contain water', 'require': 'require much time',
    'serve': 'serve food', 'press': 'press the light', 'pour': 'pour the water',
    'boil': 'boil the water', 'matter': 'it does not matter', 'sound': 'sound good',
    'cross': 'cross the road', 'fit': 'it fits me',
    'person': 'a person who helps', 'thing': 'a thing to eat', 'place': 'a place to eat',
    'kind': 'a kind of music', 'way': 'a way to say it', 'part': 'a part of the work',
    'piece': 'a piece of bread', 'group': 'a group of people', 'system': 'a simple system',
    'tool': 'a tool for cutting', 'machine': 'a machine that washes clothes',
    'material': 'a material for building', 'language': 'a language for talking',
    'word': 'a new word', 'letter': 'a letter to a friend', 'number': 'a phone number',
    'shape': 'a round shape', 'size': 'the size of the room', 'level': 'a high level of English',
    'degree': 'a high degree', 'reason': 'the reason why', 'result': 'the result of the work',
    'problem': 'a big problem', 'question': 'a hard question', 'answer': 'the answer',
    'idea': 'a good idea', 'plan': 'a plan for the week', 'example': 'an example of it',
    'fact': 'a true fact', 'truth': 'the truth', 'job': 'a good job',
    'work': 'work at home', 'rule': 'a simple rule', 'law': 'the law of the country',
    'company': 'a big company', 'program': 'a radio program', 'game': 'a fun game',
    'sport': 'a popular sport', 'ball': 'a red ball', 'player': 'a good player',
    'class': 'a class of students', 'end': 'the end of the day', 'life': 'a good life',
    'feeling': 'a good feeling', 'control': 'control the price', 'health': 'good health',
    'pain': 'a little pain', 'art': 'a school for art', 'music': 'music I like',
    'story': 'a long story', 'meeting': 'a work meeting',
    'house': 'my house', 'home': 'at home', 'room': 'a small room', 'door': 'open the door',
    'window': 'the window', 'floor': 'the top floor', 'wall': 'a white wall',
    'road': 'a long road', 'street': 'a busy street', 'way': 'on the way',
    'corner': 'the corner of the street', 'side': 'on the other side', 'city': 'a big city',
    'town': 'a small town', 'country': 'my country', 'world': 'around the world',
    'shop': 'a small shop', 'store': 'a big store', 'station': 'the train station',
    'school': 'go to school', 'office': 'a small office', 'bank': 'the bank on the street',
    'park': 'in the park', 'north': 'the north side', 'south': 'the south side',
    'east': 'the east side', 'west': 'the west side', 'left': 'on the left',
    'right': 'on the right', 'front': 'in front of the door', 'inside': 'inside the house',
    'outside': 'outside the house', 'map': 'read a map', 'bus stop': 'at the bus stop',
    'top': 'on the top', 'line': 'stand in line', 'ticket': 'a bus ticket',
    'bus': 'take the bus', 'train': 'take the train', 'plane': 'take the plane',
    'car': 'my car', 'bike': 'ride a bike',
    'weather': 'the weather today', 'sun': 'the sun is hot', 'moon': 'the moon at night',
    'sky': 'a blue sky', 'cloud': 'a white cloud', 'rain': 'it is going to rain',
    'snow': 'snow in winter', 'wind': 'strong wind', 'sea': 'the sea is big',
    'river': 'a long river', 'tree': 'a tall tree', 'flower': 'a yellow flower',
    'plant': 'a green plant', 'animal': 'a small animal', 'dog': 'a big dog',
    'cat': 'a black cat', 'bird': 'a small bird', 'fish': 'many fish',
    'earth': 'the earth', 'fire': 'a big fire', 'wood': 'a piece of wood',
    'oil': 'much oil', 'gas': 'the gas in the car', 'air': 'clean air',
    'land': 'dry land', 'field': 'a green field', 'farm': 'a small farm',
    'light': 'turn on the light', 'glass': 'a glass of water', 'paper': 'a piece of paper',
    'food': 'good food', 'rice': 'eat rice', 'meat': 'meat and rice',
    'milk': 'a glass of milk', 'tea': 'a cup of tea', 'coffee': 'a cup of coffee',
    'fruit': 'a sweet apple', 'apple': 'a red apple', 'sugar': 'too much sugar',
    'salt': 'a little salt', 'lunch': 'eat lunch', 'dinner': 'make dinner',
    'head': 'my head', 'hair': 'long hair', 'eye': 'big eyes', 'ear': '2 ears',
    'nose': 'a small nose', 'mouth': 'open your mouth', 'tooth': 'clean your teeth',
    'arm': 'my arm', 'hand': 'wash your hands', 'leg': 'my leg', 'foot': 'my foot',
    'heart': 'my heart', 'face': 'wash your face', 'body': 'a healthy body',
    'shirt': 'a white shirt', 'pants': 'new pants', 'dress': 'a nice dress',
    'shoes': 'new shoes', 'hat': 'a big hat', 'table': 'on the table',
    'chair': 'a small chair', 'bed': 'go to bed', 'cup': 'a cup of tea',
    'knife': 'a sharp knife', 'bottle': 'a water bottle', 'box': 'a small box',
    'bag': 'a heavy bag', 'book': 'a good book', 'pen': 'write with a pen',
    'key': 'the key to the door', 'picture': 'a nice picture', 'medicine': 'take medicine',
    'phone': 'my phone', 'computer': 'my computer', 'letter': 'write a letter',
    'message': 'a short message', 'bill': 'pay the bill', 'money': 'much money',
    'price': 'the price of food', 'card': 'a bank card',
    'hello': 'say hello', 'hi': 'say hi', 'goodbye': 'say goodbye', 'bye': 'say bye',
    'thanks': 'say thanks', 'thank': 'thank you', 'please': 'please sit down',
    'sorry': 'I am sorry', 'welcome': 'welcome to my home', 'name': 'my name',
    'friend': 'a good friend', 'family': 'my family', 'mother': 'my mother',
    'father': 'my father', 'parent': 'my parents', 'brother': 'my brother',
    'sister': 'my sister', 'child': 'a small child', 'son': 'my son',
    'daughter': 'my daughter', 'husband': 'my husband', 'wife': 'my wife',
    'baby': 'a small baby', 'teacher': 'a good teacher', 'student': 'a young student',
    'doctor': 'see a doctor', 'nurse': 'the nurse is here', 'worker': 'a hard worker',
    'customer': 'a new customer', 'person': 'a kind person', 'man': 'a young man',
    'woman': 'a young woman', 'people': 'many people', 'member': 'a team member',
    'English': 'I speak English', 'Chinese': 'I speak Chinese',
    'time': 'a long time', 'year': 'last year', 'month': 'next month',
    'week': 'next week', 'day': 'a good day', 'hour': 'one hour',
    'minute': '5 minutes', 'morning': 'in the morning', 'afternoon': 'in the afternoon',
    'evening': 'in the evening', 'night': 'at night', 'today': 'today',
    'tomorrow': 'tomorrow', 'yesterday': 'yesterday', 'tonight': 'tonight',
    'weekend': 'this weekend', 'birthday': 'my birthday', 'holiday': 'a long holiday',
    'date': 'today is the date', 'clock': 'look at the clock', 'early': 'get up early',
    'late': 'come late', 'ago': '2 days ago',
    'good': 'a good day', 'bad': 'a bad day', 'big': 'a big house',
    'small': 'a small room', 'long': 'a long road', 'short': 'a short story',
    'tall': 'a tall man', 'high': 'a high price', 'low': 'a low price',
    'old': 'an old man', 'new': 'a new job', 'young': 'a young woman',
    'hot': 'hot water', 'cold': 'cold weather', 'warm': 'a warm room',
    'cool': 'cool water', 'wet': 'wet clothes', 'dry': 'dry air',
    'easy': 'an easy question', 'hard': 'a hard question', 'difficult': 'a difficult question',
    'simple': 'a simple answer', 'important': 'an important thing',
    'different': 'different from me', 'wrong': 'the wrong answer',
    'true': 'a true story', 'false': 'a false story', 'real': 'a real story',
    'nice': 'a nice day', 'fine': 'fine, thanks', 'free': 'free food',
    'busy': 'a busy day', 'happy': 'a happy child', 'sad': 'a sad story',
    'angry': 'an angry man', 'tired': 'very tired', 'hungry': 'I am hungry',
    'thirsty': 'I am thirsty', 'sick': 'a sick child', 'healthy': 'a healthy body',
    'strong': 'a strong man', 'weak': 'a weak man', 'heavy': 'a heavy bag',
    'fast': 'a fast car', 'slow': 'a slow bus', 'beautiful': 'a beautiful day',
    'afraid': 'afraid at night', 'fun': 'a fun game', 'interesting': 'an interesting story',
    'possible': 'it is possible', 'clear': 'a clear answer', 'ready': 'I am ready',
    'sure': 'I am sure', 'rich': 'a rich family', 'poor': 'a poor family',
    'sweet': 'sweet tea', 'soft': 'a soft bed', 'wide': 'a wide road',
    'deep': 'a deep river', 'full': 'a full cup', 'brown': 'brown bread',
    'black': 'a black cat', 'white': 'a white shirt', 'red': 'a red apple',
    'blue': 'a blue sky', 'green': 'green tea', 'yellow': 'a yellow flower',
    'orange': 'an orange cat', 'pink': 'a pink flower', 'special': 'a special day',
    'safe': 'a safe place', 'careful': 'be careful', 'kind': 'a kind man',
    'correct': 'the correct answer', 'certain': 'a certain fact', 'dirty': 'dirty clothes',
    'I': 'I am a student', 'we': 'we are good friends', 'they': 'they are at home',
    'he': 'he is my brother', 'she': 'she is my sister', 'it': 'it is a good day',
    'this': 'this is my book', 'that': 'that is my house', 'these': 'these are my books',
    'those': 'those are my friends', 'who': 'who is that?', 'what': 'what is that?',
    'which': 'which one do you want?', 'somebody': 'somebody is here',
    'something': 'something is wrong', 'everyone': 'everyone is here',
    'nobody': 'nobody knows', 'nothing': 'nothing happened',
    'number': 'my phone number', 'half': 'half of the work', 'whole': 'the whole day',
    'double': 'double the price', 'percent': '10 percent',
    'am': 'I am ready', 'is': 'he is ready', 'are': 'you are ready',
    'was': 'he was late', 'were': 'they were late', 'be': 'be careful',
    'do': 'do your work', 'does': 'he does his work', 'did': 'did you call?',
    'have': 'have a good day', 'has': 'he has a car', 'had': 'I had a car',
    'will': 'I will go', 'would': 'I would go', 'can': 'I can swim',
    'could': 'I could swim', 'shall': 'shall we go?', 'should': 'you should go',
    'may': 'you may go', 'might': 'it might rain', 'must': 'you must go',
    'not': 'do not go', 'no': 'no water', 'yes': 'yes, I do',
    'than': 'taller than my brother', 'as': 'as fast as you', 'if': 'if it rains',
    'because': 'because I am busy', 'so': 'so I go home', 'and': 'you and I',
    'or': 'tea or coffee', 'but': 'but I am busy', 'when': 'when I arrive',
    'while': 'while I work', 'before': 'before I go', 'after': 'after I go',
    'until': 'until tomorrow', 'since': 'since last year', 'therefore': 'therefore I go',
    'also': 'also my friend', 'too': 'me too', 'very': 'very good',
    'quite': 'quite good', 'really': 'really good', 'just': 'just now',
    'still': 'still here', 'only': 'only one', 'even': 'even at night',
    'almost': 'almost finished', 'already': 'already finished', 'always': 'always at home',
    'never': 'never at home', 'often': 'often at home', 'sometimes': 'sometimes at home',
    'usually': 'usually at home', 'again': 'say it again', 'soon': 'soon',
    'now': 'right now', 'then': 'and then', 'yet': 'not yet', 'here': 'come here',
    'there': 'over there', 'up': 'go up', 'down': 'go down', 'out': 'go out',
    'off': 'turn it off', 'over': 'come over', 'under': 'under the table',
    'away': 'go away', 'back': 'come back', 'together': 'do it together',
    'less': 'less money', 'least': 'at least one', 'enough': 'enough time',
    'first': 'the first day', 'last': 'the last day', 'next': 'the next day',
    'every': 'every day', 'of': 'a cup of tea', 'in': 'in the room',
    'on': 'on the table', 'at': 'at the door', 'to': 'go to school',
    'for': 'for me', 'with': 'with my friend', 'from': 'from my home',
    'by': 'by bus', 'about': 'about the work', 'above': 'above the door',
    'below': 'below the table', 'across': 'across the road', 'around': 'around the corner',
    'behind': 'behind the door', 'between': 'between 2 people',
    'among': 'among my friends', 'into': 'into the room', 'onto': 'onto the table',
    'through': 'through the door', 'during': 'during the day',
    'against': 'against the wall', 'beside': 'beside the door', 'toward': 'toward the door',
    'without': 'without water', 'near': 'near my home', 'like': 'like my mother',
    'well': 'I am well', 'maybe': 'maybe tomorrow', 'little': 'a little water',
    'okay': 'okay, thanks', 'actually': 'actually I like it', 'whether': 'I do not know whether',
    'unless': 'unless it rains', 'instead': 'instead of that', 'every': 'every morning',
}


def example_for(w, pos):
    if w in EXAMPLES:
        return EXAMPLES[w]
    kinds = pos.split('/')
    if 'v' in kinds:
        return f'to {w}'
    if 'adj' in kinds:
        return f'very {w}'
    if 'adv' in kinds:
        return f'very {w}'
    if 'n' in kinds:
        return f'the {w}'
    return f'（{w}）'


# ── 產生 ─────────────────────────────────────────────────────────────────────
def build_tables(words, irr, ipa):
    out = []
    summary = []
    total_c = total_e = 0
    for cat in CATS:
        ws = [x for x in words if x['cat'] == cat]
        c = [x for x in ws if x['level'] == 'C']
        e = [x for x in ws if x['level'] == 'E']
        total_c += len(c)
        total_e += len(e)
        summary.append((CAT_NAMES[cat], len(c), len(e)))
        out.append(f'\n### 2.{CATS.index(cat)+1} {CAT_NAMES[cat]}（核心 {len(c)} ＋ 擴充 {len(e)} ＝ {len(ws)}）\n')
        out.append('| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |')
        out.append('|---|---|---|---|---|---|---|')
        for x in ws:
            w = x['word']
            i = ipa.get(w.lower(), '')
            if w in IPA_OVERRIDE:
                i = IPA_OVERRIDE[w]
            forms = forms_of(w, x['pos'], irr)
            ex = example_for(w, x['pos']).replace('|', '\\|')
            out.append(f"| {w} | /{i}/ | {'核心' if x['level']=='C' else '擴充'} | {x['pos']} | {x['zh']} | {forms} | {ex} |")
    head = ['| 類別 | 核心 | 擴充 | 合計 |', '|---|---:|---:|---:|']
    for name, nc, ne in summary:
        head.append(f'| {name} | {nc} | {ne} | {nc+ne} |')
    head.append(f'| **合計** | **{total_c}** | **{total_e}** | **{total_c+total_e}** |')
    return '\n'.join(head), '\n'.join(out)


def build_appendix(words):
    out = []
    for lvl, label in (('C', '核心層'), ('E', '擴充層')):
        for cat in CATS:
            ws = [x['word'] for x in words if x['cat'] == cat and x['level'] == lvl]
            if not ws:
                continue
            out.append(f'# {label}｜{CAT_NAMES[cat]}')
            out.extend(ws)
    return '\n'.join(out)


def build_lexicon():
    """把 data/lexicon_part*.tsv 加上 data/core_words.txt 組成 lexicon.tsv。"""
    parts = []
    for path in sorted(DATA.glob('lexicon_part*.tsv')):
        parts += [l for l in path.read_text(encoding='utf-8').splitlines()
                  if l.strip() and not l.startswith('English\tMini-English')]
    seen, rows = set(), []
    for line in parts:
        f = [x.strip() for x in line.split('\t')]
        while len(f) < 4:
            f.append('')
        if f[0].lower() in seen:
            continue
        seen.add(f[0].lower())
        rows.append(f)
    # 表內的常用詞也放進詞典，讓學習者可以當字典用
    core = (DATA / 'core_words.txt').read_text(encoding='utf-8').split()
    for w in core:
        if w.lower() in seen:
            continue
        seen.add(w.lower())
        rows.append([w, w, '本詞', ''])
    out = HERE / 'lexicon.tsv'
    with out.open('w', encoding='utf-8') as f:
        f.write('English\tMini-English\t方式\t說明\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    return len(rows)


def main():
    words = load_words()
    irr = load_irregular()
    ipa = load_ipa()
    summary, tables = build_tables(words, irr, ipa)
    appendix = build_appendix(words)
    affix = load_table('affix.tsv')
    head = load_table('head.tsv')
    replace = load_table('replace.tsv')
    phrasal = (DATA / 'phrasal.tsv').read_text(encoding='utf-8').splitlines()

    affix_rows = ['| 字首／字尾 | 類型 | 意思 | 例子 |', '|---|---|---|---|']
    for a in affix:
        affix_rows.append(f"| `{a['affix']}` | {a['kind']} | {a['meaning']} | {a['examples']} |")

    head_rows = ['| 類頭 | 中文 |', '|---|---|']
    for h in head:
        head_rows.append(f"| {h['head']} | {h['zh']} |")

    replace_rows = ['| 英文（不在核心層、常用） | Mini-English 說法 |', '|---|---|']
    for r in replace:
        replace_rows.append(f"| {r['word']} | {r['replace']} |")

    irr_rows = ['| 原形 | 不規則形式 |', '|---|---|']
    for k, v in irr.items():
        irr_rows.append(f"| {k} | {' / '.join(v)} |")

    # prompts/system.md：把完整詞表放進提示詞
    forbidden = '\n'.join(f"- `{r['word']}` → {r['replace']}" for r in replace)
    ptext = (DATA / 'prompt.md').read_text(encoding='utf-8')
    ptext = ptext.replace('{{WORDLIST}}', appendix)
    ptext = ptext.replace('{{FORBIDDEN}}', forbidden)
    ptext = ptext.replace('{{N}}', str(len(words)))
    ptext = ptext.replace('{{NCORE}}', str(sum(1 for w in words if w['level'] == 'C')))
    ptext = ptext.replace('{{NEXT}}', str(sum(1 for w in words if w['level'] == 'E')))
    n_lex = build_lexicon()
    (HERE / 'prompts' / 'system.md').write_text(
        '# 系統提示詞：Mini-English\n\n'
        '> 把下面「---」之間的內容整段放進 LLM 的系統提示詞（system prompt）。\n'
        '> 任務的寫法見 [tasks.md](tasks.md)。\n\n---\n\n' + ptext.strip() + '\n\n---\n', encoding='utf-8')

    text = (DATA / 'spec.md').read_text(encoding='utf-8')
    text = text.replace('{{SUMMARY}}', summary)
    text = text.replace('{{TABLES}}', tables)
    text = text.replace('{{APPENDIX}}', appendix)
    text = text.replace('{{AFFIX}}', '\n'.join(affix_rows))
    text = text.replace('{{HEAD}}', '\n'.join(head_rows))
    text = text.replace('{{REPLACE}}', '\n'.join(replace_rows))
    text = text.replace('{{IRREGULAR}}', '\n'.join(irr_rows))
    text = text.replace('{{PHRASAL}}', '\n'.join(phrasal))
    (HERE / 'mini-english.md').write_text(text, encoding='utf-8')
    print(f'✅ mini-english.md：{len(words)} 詞（核心 {sum(1 for w in words if w["level"]=="C")}'
          f' ＋ 擴充 {sum(1 for w in words if w["level"]=="E")}）')
    print(f'✅ lexicon.tsv：{n_lex} 列')


if __name__ == '__main__':
    main()
