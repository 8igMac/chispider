import json
import math

def related_word(category):
    # Parameters.
    max_word_length = 5
    min_word_frequency = 0.0001
    min_pmi = 1
    min_entropy = 3

    # Take input file.
    f = open('cna_news.json')
    articles = json.load(f)

    # Concat input string.
    input_text = ''
    article_count = 0
    for article in articles:
        if article['category'] == category:
            article_count += 1
            input_text += article['content']

    # Preprocess input string: eliminate non-Chinese character
    # NOTE: better syntax?
    # NOTE: should we preprocess before or after calculation?
    input_text = input_text.translate({i: None for i in range(ord('a'), ord('z') + 1)})
    input_text = input_text.translate({i: None for i in range(ord('A'), ord('Z') + 1)})  
    input_text = input_text.translate({i: None for i in range(ord('0'), ord('9') + 1)})  
    input_text = input_text.translate({
        ord('，'): None,
        ord('。'): None,
        ord('；'): None,
        ord('、'): None,
        ord('（'): None,
        ord('）'): None,
        ord('「'): None,
        ord('」'): None,
        ord(' '): None,
        ord('.'): None,
        ord('：'): None,
        ord('%'): None
    })  

    # Scan input text. For each entry, do a sliding window to extract new
    # words. For each word, record the count and the left/right word count.
    word_count = dict()
    word_left_char_count = dict()
    word_right_char_count = dict()

    for index in range(0, len(input_text) - max_word_length):
        for kmer in range(1, max_word_length):
            end = index + kmer

            word = input_text[index:end]
            left_char = input_text[index-1:index]
            right_char = input_text[end:end+1]

            if word in word_count:
                word_count[word] += 1

                if left_char in word_left_char_count[word]:
                    word_left_char_count[word][left_char] += 1
                else:
                    word_left_char_count[word][left_char] = 1

                if right_char in word_right_char_count[word]:
                    word_right_char_count[word][right_char] += 1
                else:
                    word_right_char_count[word][right_char] = 1
            else:
                word_count[word] = 1
                word_left_char_count[word] = dict()
                word_left_char_count[word][left_char] = 1
                word_right_char_count[word] = dict()
                word_right_char_count[word][right_char] = 1

    # For each word, calculate frequency
    frequency = dict()
    for word, count in word_count.items():
        frequency[word] = count / len(input_text)

    # For each word, calculate PMI.
    pmi = dict()
    for word, count in word_count.items():
        if len(word) >= 2:  # NOTE: eliminate single word
            mini = 1
            for i in range(1, len(word) - 1):
                if not word[:i] in frequency or not word[i:] in frequency:
                    continue  # NOTE: an ugly, temporary solution
                result = math.log(frequency[word] / (frequency[word[:i]] * frequency[word[i:]]))
                mini = min(mini, result)
            pmi[word] = mini

    # For each word, calculate left and right entropy, and take the minimun
    # as the overall entropy.
    entropy = dict()
    for word in word_left_char_count.keys():
        # calculate left entropy for word
        total = sum([x for x in word_left_char_count[word].values()])
        for char in word_left_char_count[word].keys():
            word_left_char_count[word][char] /= total

        left_entropy = sum([-1 * x * math.log(x) for x in word_left_char_count[word].values()])

        # calculate right entropy for word
        total = sum([x for x in word_right_char_count[word].values()])
        for char in word_right_char_count[word].keys():
            word_right_char_count[word][char] /= total

        right_entropy = sum([-1 * x * math.log(x) for x in word_right_char_count[word].values()])

        entropy[word] = min(left_entropy, right_entropy)

    # Release some memory
    word_count.clear()
    word_left_char_count.clear()
    word_right_char_count.clear()

    # # Debug
    # print([x for x in sorted(pmi.items(), key=lambda item: item[1]) if x[1] >= 0.7]

    # Filter out based on a threshold of frequency, PMI, and entropy.
    result = [word for word in pmi.keys() if  # NOTE: pmi has less key 
        frequency[word] >= min_word_frequency and
        pmi[word] >= min_pmi and
        entropy[word] >= min_entropy and 
        len(word) >= 2  # NOTE: eliminate single word.
    ]

    # Sort by frequency.
    result.sort(key=lambda word: frequency[word], reverse=True)

    # Output result
    print('Found {} related word in {} articles for category {}.'.format(
        len(result), article_count, category))
    print(result)

if __name__ == '__main__':
    related_word('科技')
    related_word('兩岸')
    related_word('社會')
    related_word('地方')
    related_word('娛樂')
    related_word('國際')
    related_word('運動')
    related_word('產經')
    related_word('重點新聞')
    related_word('生活')
    related_word('文化')
    related_word('政治')
    related_word('證券')
