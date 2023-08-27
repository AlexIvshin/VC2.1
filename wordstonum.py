
"""
function to form numeric multipliers for million, billion, thousand etc.
input: list of strings
return value: integer
"""

import re

russian_number_system = {
    'ноль': 0,
    'нуля': 0,
    'нулю': 0,
    'нулём': 0,
    'нуле': 0,
    'один': 1,
    'одна': 1,
    'единица': 1,
    'одного': 1,
    'одному': 1,
    'первый': 1,
    'первого': 1,
    'первое': 1,
    'первому': 1,
    'первым': 1,
    'первом': 1,
    'два': 2,
    'двух': 2,
    'двумя': 2,
    'две': 2,
    'второй': 2,
    'второе': 2,
    'второго': 2,
    'второму': 2,
    'вторым': 2,
    'втором': 2,
    'три': 3,
    'трёх': 3,
    'трём': 3,
    'тремя': 3,
    'третье': 3,
    'третья': 3,
    'третего': 3,
    'третий': 3,
    'четыре': 4,
    'четырёх': 4,
    'четвёртый': 4,
    'четырём': 4,
    'четвёртое': 4,
    'четвёртого': 4,
    'четырьмя': 4,
    'пять': 5,
    'пяти': 5,
    'пятью': 5,
    'пятое': 5,
    'пятого': 5,
    'пятый': 5,
    'шесть': 6,
    'шести': 6,
    'шестью': 6,
    'шестое': 6,
    'шестой': 6,
    'шестого': 6,
    'семь': 7,
    'семи': 7,
    'седьмое': 7,
    'седьмой': 7,
    'седьмого': 7,
    'восемь': 8,
    'восеми': 8,
    'восьмью': 8,
    'восьмое': 8,
    'восьмой': 8,
    'восьмого': 8,
    'девять': 9,
    'девяти': 9,
    'девятью': 9,
    'девятое': 9,
    'девятый': 9,
    'девятого': 9,
    'десять': 10,
    'десяти': 10,
    'десятью': 10,
    'десятое': 10,
    'десятый': 10,
    'десятого': 10,
    'одиннадцать': 11,
    'одиннадцатый': 11,
    'одиннадцатое': 11,
    'одиннадцатого': 11,
    'двенадцать': 12,
    'двенадцатый': 12,
    'двенадцатое': 12,
    'двенадцатого': 12,
    'тринадцать': 13,
    'тринадцатое': 13,
    'тринадцатый': 13,
    'тринадцатого': 13,
    'четырнадцать': 14,
    'четырнадцатый': 14,
    'четырнадцатое': 14,
    'четырнадцатого': 14,
    'пятнадцать': 15,
    'пятнадцатый': 15,
    'пятнадцатое': 15,
    'пятнадцатого': 15,
    'шестнадцать': 16,
    'шестнадцатый': 16,
    'шестнадцатое': 16,
    'шестнадцатого': 16,
    'семнадцать': 17,
    'семнадцатый': 17,
    'семнадцатое': 17,
    'семнадцатого': 17,
    'восемнадцать': 18,
    'восемнадцатый': 18,
    'восемнадцатое': 18,
    'восемнадцатог': 18,
    'девятнадцать': 19,
    'девятнадцатый': 19,
    'девятнадцатое': 19,
    'девятнадцатого': 19,
    'двадцать': 20,
    'двадцатый': 20,
    'двадцатое': 20,
    'двадцатого': 20,
    'тридцать': 30,
    'тридцатый': 30,
    'тридцатое': 30,
    'тридцатого': 30,
    'сорок': 40,
    'сороковый': 40,
    'пятьдесят': 50,
    'пятидесяеый': 50,
    'шестьдесят': 60,
    'шестьдесятый': 60,
    'семьдесят': 70,
    'восемьдесят': 80,
    'девяносто': 90,
    'сто': 100,
    "двести": 200,
    "триста": 300,
    "четыреста": 400,
    "пятьсот": 500,
    "шестьсот": 600,
    "семьсот": 700,
    "восемьсот": 800,
    "девятьсот": 900,
    'тысяча': 1000,
    'тысячи': 1000,
    'тысяче': 1000,
    'тысячу': 1000,
    'тысячей': 1000,
    'тысяч': 1000,
    'миллион': 1000000,
    'миллиона': 1000000,
    'миллиону': 1000000,
    'миллионом': 1000000,
    'миллионе': 1000000,
    'миллионов': 1000000,
    'миллиард': 1000000000,
    'миллиарда': 1000000000,
    'миллиарду': 1000000000,
    'миллиардом': 1000000000,
    'миллиарде': 1000000000,
    'миллиардов': 1000000000,
    'целых': '.',
    'целая': '.'
}


def number_formation(number_words):
    numbers = []
    for number_word in number_words:
        numbers.append(russian_number_system[number_word])
    if len(numbers) == 4:
        return (numbers[0] * numbers[1]) + numbers[2] + numbers[3]
    elif len(numbers) == 3:
        return numbers[0] + numbers[1] + numbers[2]
    elif len(numbers) == 2:
        return numbers[0] + numbers[1]
    else:
        return numbers[0]


def get_decimal_sum(decimal_digit_words):
    """
    function to convert post decimal digit words to numerial digits
    input: list of strings
    output: double
    """
    decimal_number_str = word_to_num(' '.join(decimal_digit_words))
    final_decimal_string = '0.' + str(decimal_number_str)
    return float(final_decimal_string)


def word_to_num(number_sentence):
    """
    function to return integer for an input `number_sentence` string
    input: string
    output: int or double or None
    """

    if type(number_sentence) is not str:
        raise ValueError("Type of input is not string! Please enter a valid number word"
                         " (eg. \'two million twenty three thousand and forty nine\')")

    number_sentence = number_sentence.replace('-', ' ')
    number_sentence = number_sentence.lower()  # converting input to lowercase

    if number_sentence.isdigit():  # return the number if user enters a number string
        return int(number_sentence)

    split_words = number_sentence.strip().split()  # strip extra spaces and split sentence into words

    clean_numbers = []
    clean_decimal_numbers = []
    other_words = []

    # removing and, & etc.
    for word in split_words:
        if word in russian_number_system:
            clean_numbers.append(word)
        else:
            other_words.append(word)

    if len(clean_numbers) == 0:
        return number_sentence

    # Error if user enters million, billion, thousand or decimal point twice
    if clean_numbers.count('тысяча') > 1 \
            or clean_numbers.count('миллион') > 1 \
            or clean_numbers.count('миллиард') > 1 \
            or clean_numbers.count('целых') > 1 \
            or clean_numbers.count('целая') > 1:
        raise ValueError("Redundant number word! Please enter a valid number word "
                         "(eg. two million twenty three thousand and forty nine)")

    # separate decimal part of number (if exists)
    if clean_numbers.count('целых') == 1:
        clean_decimal_numbers = clean_numbers[clean_numbers.index('целых') + 1:]
        clean_numbers = clean_numbers[:clean_numbers.index('целых')]
    if clean_numbers.count('целая') == 1:
        clean_decimal_numbers = clean_numbers[clean_numbers.index('целая') + 1:]
        clean_numbers = clean_numbers[:clean_numbers.index('целая')]

    if 'миллиард' in clean_numbers:
        billion_index = clean_numbers.index('миллиард')
    elif 'миллиарда' in clean_numbers:
        billion_index = clean_numbers.index('миллиарда')
    elif 'миллиарду' in clean_numbers:
        billion_index = clean_numbers.index('миллиарду')
    elif 'миллиардом' in clean_numbers:
        billion_index = clean_numbers.index('миллиардом')
    elif 'миллиарде' in clean_numbers:
        billion_index = clean_numbers.index('миллиарде')
    elif 'миллиардов' in clean_numbers:
        billion_index = clean_numbers.index('миллиардов')
    else:
        billion_index = -1

    if 'миллион' in clean_numbers:
        million_index = clean_numbers.index('миллион')
    elif 'миллиона' in clean_numbers:
        million_index = clean_numbers.index('миллиона')
    elif 'миллиону' in clean_numbers:
        million_index = clean_numbers.index('миллиону')
    elif 'миллионом' in clean_numbers:
        million_index = clean_numbers.index('миллионом')
    elif 'миллионе' in clean_numbers:
        million_index = clean_numbers.index('миллионе')
    elif 'миллионов' in clean_numbers:
        million_index = clean_numbers.index('миллионов')
    else:
        million_index = -1

    if 'тысяча' in clean_numbers:
        thousand_index = clean_numbers.index('тысяча')
    elif 'тысячи' in clean_numbers:
        thousand_index = clean_numbers.index('тысячи')
    elif 'тысяче' in clean_numbers:
        thousand_index = clean_numbers.index('тысяче')
    elif 'тысячу' in clean_numbers:
        thousand_index = clean_numbers.index('тысячу')
    elif 'тысячей' in clean_numbers:
        thousand_index = clean_numbers.index('тысячей')
    elif 'тысяч' in clean_numbers:
        thousand_index = clean_numbers.index('тысяч')
    else:
        thousand_index = -1

    if (thousand_index > -1 and (thousand_index < million_index or thousand_index < billion_index)) \
            or (1 <= million_index < billion_index):
        raise ValueError("Неверный формат числа! Пожалуйста, введите допустимое числовое слово"
                         "(например, два миллиона двадцать три тысячи сорок девять)")

    total_sum = 0  # storing the number to be returned

    if len(clean_numbers) > 0:

        if len(clean_numbers) == 1:
            total_sum += russian_number_system[clean_numbers[0]]

        else:
            if billion_index > -1:
                billion_multiplier = number_formation(clean_numbers[0:billion_index])
                total_sum += billion_multiplier * 1000000000

            if million_index > -1:
                if billion_index > -1:
                    million_multiplier = number_formation(clean_numbers[billion_index + 1:million_index])
                else:
                    million_multiplier = number_formation(clean_numbers[0:million_index])
                total_sum += million_multiplier * 1000000

            if thousand_index > -1:
                if million_index > -1:
                    thousand_multiplier = number_formation(clean_numbers[million_index + 1:thousand_index])

                elif billion_index > -1 and million_index == -1:
                    thousand_multiplier = number_formation(clean_numbers[billion_index + 1:thousand_index])

                elif thousand_index == 0:
                    thousand_multiplier = 1

                else:
                    thousand_multiplier = number_formation(clean_numbers[0:thousand_index])
                total_sum += thousand_multiplier * 1000

            if thousand_index > -1 and thousand_index == len(clean_numbers) - 1:
                hundreds = 0
            elif thousand_index > -1 and thousand_index != len(clean_numbers) - 1:
                hundreds = number_formation(clean_numbers[thousand_index + 1:])
            elif million_index > -1 and million_index != len(clean_numbers) - 1:
                hundreds = number_formation(clean_numbers[million_index + 1:])
            elif billion_index > -1 and billion_index != len(clean_numbers) - 1:
                hundreds = number_formation(clean_numbers[billion_index + 1:])
            elif thousand_index == -1 and million_index == -1 and billion_index == -1:
                hundreds = number_formation(clean_numbers)
            else:
                hundreds = 0
            total_sum += hundreds

    # adding decimal part to total_sum (if exists)
    if len(clean_decimal_numbers) > 0:
        decimal_sum = get_decimal_sum(clean_decimal_numbers)
        total_sum += decimal_sum

    return total_sum


def word2num_ru(text, otherwords=False):
    if otherwords:
        clean_numbers = []
        clean_words = []
        nums = []
        new_split_words = []
        split_words = text.strip().split()

        for word in split_words:
            if word in russian_number_system or word in ['десятых', 'сотых', 'тысячных']:
                clean_numbers.append(word)
                clean_words.append('')
            else:
                clean_numbers.append('')
                clean_words.append(word)

        if not ''.join(clean_numbers):
            return text

        line = re.sub("#+", " ", ' '.join(clean_numbers)).strip().replace('  ', '#').split('#')
        line_words = re.sub("#+", " ", ' '.join(clean_words)).strip().replace('  ', '#').split('#')

        for word in line:
            num = word_to_num(word)
            nums.append(num)

        len_nums = len(nums)

        if split_words[0] in russian_number_system:
            new_split_words.append(str(nums[0]))
            del nums[0]
            len_nums -= 1

        c = 0
        for word in line_words:
            if word:
                if len_nums == 0:
                    new_split_words.append(word)
                    break
                else:
                    new_split_words.append(word + ' ' + str(nums[c]))
                    len_nums -= 1
                    c += 1

        result = re.sub(" +", " ", ' '.join(new_split_words)).strip()
    else:
        result = word_to_num(text)

    if result:
        return result
