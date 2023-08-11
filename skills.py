# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import configparser
import cpuinfo
from datetime import date, datetime as dt
import datetime
import GPUtil
from googletrans import Translator
import os
import pathlib
from platform import uname
import psutil
import randfacts
import random
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from subprocess import run, check_output, call
from tabulate import tabulate as tb
import time
from typing import Union, Optional, Any
import webbrowser
import wikipedia

from assistant import Assistant
import dialog as dg
from wordstonum import word2num_ru as w2n
import utils as tls
from widgets.hand_input_widget import get_input

talk = Assistant().speaks
mic_sins = Assistant().mic_sensitivity

homedir = os.getcwdb().decode(encoding='utf-8')


class ProgramManager:

    def __init__(self, program, action):
        self.program = program
        self.action = action

    def get_program_name(self) -> str:
        if self.action == 'off':
            if self.program == 'google-chrome':
                return 'chrome'
            if self.program == 'sudo virtualbox':
                return 'VirtualBox'
        return self.program

    def start_stop_program(self):
        prg = self.get_program_name()
        tls.answer_ok_and_pass()

        if self.action == 'on':
            print(f'  {prg.capitalize()} starts!')
            if prg == 'tor':
                return run(f'~/tor-browser/Browser/start-tor-browser >/dev/null 2>&1 &', shell=True)
            return run(f'{prg} >/dev/null 2>&1 &', shell=True)

        if self.action == 'off' and call(f'pgrep {prg} >/dev/null', shell=True) == 0:
            print(f'  {prg.capitalize()} will be closed!')
            if prg == 'VirtualBox':
                return run(f'sudo pkill {prg} >/dev/null 2>&1', shell=True)
            return run(f'pkill {prg} >/dev/null 2>&1', shell=True)


class Calculator:

    def __init__(self, commandline, action):
        calc_string = w2n(tls.get_meat(action, commandline, dg.actions_dict), otherwords=True).split()
        opr = ' '.join(calc_string[1:-1])
        self.operator = dg.opers[opr] if opr in dg.opers.keys() else None
        self.n1 = self.check_type_num(calc_string[0])
        self.n2 = self.check_type_num(calc_string[-1])

    @classmethod
    def check_type_num(cls, n) -> Union[float, int]:
        try:
            return float(n) if '.' in n else int(n)
        except ValueError:
            pass

    def get_result(self) -> Union[None, float, int]:
        n1, operator, n2 = self.n1, self.operator, self.n2
        if not operator or not n1 or not n2:
            return
        if operator == '+':
            return n1 + n2
        elif operator == '-':
            return n1 - n2
        elif operator == '*':
            return n1 * n2
        elif operator == '/':
            try:
                return n1 / n2
            except ZeroDivisionError:
                talk(f'Обнаружено деление на ноль!!!')

    def tell_the_result(self) -> None:
        result = self.get_result()
        if not result:
            return

        def get_correct_float_res(float_num: float) -> str:
            integer_string, decimal_string = str(float_num).split('.')[0], str(round(float_num, 3)).split('.')[1]
            decimal_title = ''
            if len(decimal_string) == 1:
                decimal_title = 'десятых'
            if len(decimal_string) == 2:
                decimal_title = 'сотых'
            if len(decimal_string) == 3:
                decimal_title = 'тысячных'
            sep = 'целая' if str(integer_string)[-1] == '1' else 'целых'
            return f'{integer_string} {sep} {decimal_string} {decimal_title}'

        tls.answer_ok_and_pass()
        print()
        print(f'  {self.n1} {self.operator} {self.n2} = {round(result, 4)}')
        print()

        if isinstance(result, int):
            return talk(f'Будет: {result}')
        if isinstance(result, float):
            return talk(f'Приблизительно будет: {get_correct_float_res(result)}')


class SearchEngine:
    wikipedia.set_lang("ru")  # Установка русского языка для Википедии

    def __init__(self, cmd, action, intersection):
        search_words = get_input() if tls.check_hand_input(cmd) else tls.get_meat(action, cmd, dg.actions_dict)
        if intersection < 2 or not search_words or not tls.check_internet():
            return
        self.search_words = search_words
        self.commandline = cmd
        self.action = action
        talk(random.choice(dg.answer_ok))

    def get_result(self) -> None:
        print(f' Ищу: "{self.search_words}"')

        if 'гугл' in self.commandline:
            return self.google_search(self.search_words)
        elif 'вики' in self.commandline:
            return self.wiki_search(self.search_words)
        else:
            return self.wiki_short_answer(self.search_words)

    @classmethod
    def exception_words(cls, wiki_error=False) -> None:
        text = 'Упс! Что-то не так пошло! Скорее всего сеть отсутствует.'
        if wiki_error:
            text = 'Необходим более точный запрос!'
        talk(text)

    @classmethod
    def google_search(cls, text: str) -> None:
        driver = None
        url = 'http://www.google.com'

        if webbrowser.get().basename == 'google-chrome':
            o = Options()
            o.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=o)

        elif webbrowser.get().basename == 'firefox':
            driver = webdriver.Firefox()

        if not driver:
            if webbrowser.get().basename == 'google-chrome':
                o = Options()
                o.add_experimental_option("detach", True)
                driver = webdriver.Chrome(options=o)

            elif webbrowser.get().basename == 'firefox':
                driver = webdriver.Firefox()

            if not driver:
                return talk('Ой! Браузер по умолчанию, не найден!')

        try:
            driver.get(url)
            search = driver.find_element("name", "q")
            search.send_keys(text)
            search.send_keys(Keys.RETURN)  # hit return after you enter search text

        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            cls.exception_words()

    @classmethod
    def wiki_search(cls, text: str) -> None:
        try:
            result = wikipedia.search(text)
            page = wikipedia.page(result[0])
            title = page.title
            content = page.content
            run(f'{tls.choice_xterm("XtermSearch")} echo "{title}{content}" &', shell=True)
            talk('Это всё, что удалось найти!')

        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            cls.exception_words()
        except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
            cls.exception_words(wiki_error=True)

    @classmethod
    def wiki_short_answer(cls, text: str) -> None:
        try:
            result = wikipedia.summary(text, sentences=3)
            result = re.sub(r'[^A-zА-я́0123456789%)(.,`\'":;!?-—]', ' ', str(result)) \
                .replace('.', '. ') \
                .replace('  ', ' ') \
                .replace(' (', ' - ') \
                .replace(')', ',') \
                .replace('; ', ', ') \
                .replace(' %', '%') \
                .replace(',,', ',') \
                .replace(',.', '.')

            talk('Вот, что удалось найти!')
            talk(result, speech_rate=104)

        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError,):
            cls.exception_words()
        except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
            cls.exception_words(wiki_error=True)


class Sinoptik:
    cities: dict = {
        'винниц': 'винница',
        'кропивницк': 'кропивницкий',
        'полтав': 'полтава',
        'харьков': 'харьков',
        'днепр': 'днепр',
        'луганск': 'луганск',
        'ровно': 'ровно',
        'херсон': 'херсон',
        'донецк': 'донецк',
        'луцк': 'луцк',
        'симферопол': 'симферополь',
        'хмельницк': 'хмельницкий',
        'житомир': 'житомир',
        'львов': 'львов',
        'сум': 'сумы',
        'черкас': 'черкассы',
        'запорожье': 'запорожье',
        'николаев': 'николаев',
        'тернопол': 'тернополь',
        'чернигов': 'чернигов',
        'ивано-франковск': 'ивано-франковск',
        'одесс': 'одесса',
        'ужгород': 'ужгород',
        'черновц': 'черновцы',
        'киев': 'киев',
        'амстердам': 'амстердам',
        'андорра-ла-вел': 'андорра-ла-велья',
        'афин': 'афины',
        'белград': 'белград',
        'берлин': 'берлин',
        'берн': 'берн',
        'братислав': 'братислава',
        'брюссел': 'брюссель',
        'будапешт': 'будапешт',
        'бухарест': 'бухарест',
        'вадуц': 'вадуц',
        'валлетт': 'валлетта',
        'варшав': 'варшава',
        'ватикан': 'ватикан',
        'вен': 'вена',
        'вильнюс': 'вильнюс',
        'дублин': 'дублин',
        'загреб': 'загреб',
        'кишинёв': 'кишинёв',
        'копенгаген': 'копенгаген',
        'лиссабон': 'лиссабон',
        'лондон': 'лондон',
        'люблян': 'любляна',
        'люксембург': 'люксембург',
        'мадрид': 'мадрид',
        'минск': 'минск',
        'монако': 'монако',
        'москв': 'москва',
        'осло': 'осло',
        'париж': 'париж',
        'подгориц': 'подгорица',
        'праг': 'прага',
        'рейкьявик': 'рейкьявик',
        'риг': 'рига',
        'рим': 'рим',
        'сан-марино': 'сан-марино',
        'сараев': 'сараево',
        'скопье': 'скопье',
        'софи': 'софия',
        'стокгольм': 'стокгольм',
        'таллин': 'таллин',
        'тиран': 'тирана',
        'хельсинки': 'хельсинки',
        'приштин': 'приштина',
        'тираспол': 'тирасполь'
    }
    weekdays = ['0', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    site_url = 'https://sinoptik.ua'

    def __init__(self, commandline, intersection):
        self.commandline = commandline
        self.intersection = intersection
        self.split_commandline = commandline.split()

    @classmethod
    def get_week_day(cls, number: int) -> int:
        return date.isoweekday(datetime.date.today() + datetime.timedelta(days=number))

    def get_url(self) -> str:
        for word in self.split_commandline:
            for key in self.cities:
                if key in word:
                    talk(random.choice(dg.answer_ok))

                    return f'{self.site_url}/погода-{self.cities[key]}'

        talk('Не поняла, погода в каком городе?')

    def get_weather_forecast(self) -> None:

        if self.intersection < 2 or not tls.check_internet():
            return

        url_weather_city = self.get_url()
        if not url_weather_city:
            return

        current_date = date.today()
        current_weekday = int(date.isoweekday(current_date))

        try:
            r = requests.get(url_weather_city)
            if r.status_code != 200:
                print(f'Status code: {r.status_code} !!!')
                talk('Упс! Целевой сервер не отвечает.')
                return

            soup = BeautifulSoup(r.text, 'html.parser')
            temp = soup.find('p', class_="today-temp").text
            description = soup.find('div', class_="description").text
            description = description.strip() \
                .replace('вечера', 'вéчера') \
                .replace('самого', 'са́мого') \
                .replace('облачка', 'о́блачка') \
                .replace('утра', 'утра́')
            min_res = soup.find_all('div', class_="min")
            max_res = soup.find_all('div', class_="max")
            light = soup.find_all('div', class_="infoDaylight")
            temps = soup.find_all('tr', class_='temperature')
            day_light = re.sub(r'[^0123456789:-]', ' ', str(light)).replace(' ', '')
            min_temps = re.sub(r'[^0123456789+°-]', ' ', str(min_res)).replace(' ', '').split('°')
            max_temps = re.sub(r'[^0123456789+°-]', ' ', str(max_res)).replace(' ', '').split('°')
            temps = re.sub(r'[^0123456789+°-]', ' ', str(temps)).replace(' ', '').split('°')
            current_temp = temp.replace('°C', ' по цельсию')

            week_data = [
                ['Min°C', min_temps[0], min_temps[1], min_temps[2],
                 min_temps[3], min_temps[4], min_temps[5], min_temps[6]],
                ['Max°C', max_temps[0], max_temps[1], max_temps[2],
                 max_temps[3], max_temps[4], max_temps[5], max_temps[6]]
            ]
            col_names = [
                "Day", self.weekdays[current_weekday], self.weekdays[self.get_week_day(1)],
                self.weekdays[self.get_week_day(2)], self.weekdays[self.get_week_day(3)],
                self.weekdays[self.get_week_day(4)], self.weekdays[self.get_week_day(5)],
                self.weekdays[self.get_week_day(6)]
            ]

            daily_temp = []
            [daily_temp.append(t[1:]) for t in temps]

            daily_temp_data = [['°C', daily_temp[1], daily_temp[2], daily_temp[3],
                                daily_temp[4], daily_temp[5], daily_temp[6], daily_temp[7]]]
            col_names_daily_temp = ['t', '3:00', '6:00', '9:00', '12:00', '15:00', '18:00', '21:00']

            print(f'{dt.today().strftime("%d-%m-%Y")} / Восход: {day_light[0:5]} / Закат: {day_light[5:]}')
            print(tb(daily_temp_data, headers=col_names_daily_temp, tablefmt="mixed_outline", numalign="center"))
            print(tb(week_data, headers=col_names, tablefmt="mixed_outline", numalign="center"))
            talk(f'Сейчас, {current_temp}. {description}', speech_rate=100)

        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            talk('Упс! Что-то не так пошло! Скорее всего сеть отсутствует.')


class Polyhistor:
    def __init__(self, commandline, intersection):
        if intersection < 2:
            return
        self.commandline = commandline

    @staticmethod
    def get_joke() -> Optional[Any]:
        if not tls.check_internet():
            return
        url_joke = 'https://www.anekdot.ru/random/anekdot/'
        r = requests.get(url_joke)
        if r.status_code != 200:
            print('Status code: ', r.status_code)
            return talk('Упс! Целевой сервер не отвечает.')

        soup = BeautifulSoup(r.text, 'html.parser')
        anecdot = soup.find_all('div', class_="text")
        joke = []
        for article in anecdot:
            article_title = article.text.strip()
            res = re.sub(r'[^A-zА-яё0123456789́\'".,:;!?-—%]', ' ', str(article_title)).replace('.', '. ')
            joke.append(res)
        return random.choice(joke)

    @staticmethod
    def get_fact() -> Optional[Any]:
        if not tls.check_internet():
            return
        f = randfacts.get_fact(False)
        tr = Translator()
        fact = tr.translate(f, dest='ru')
        return fact.text

    @staticmethod
    def get_saying() -> str:
        sayings = []
        with open(f'{homedir}/various_files/sayings.txt', 'r') as f:
            for line in f:
                sayings.append(line.replace('\n', ''))
        return random.choice(sayings)

    def get_result(self) -> None:
        try:
            result = None
            if 'анекдот' in self.commandline:
                result = self.get_joke()
            if 'факт' in self.commandline:
                result = self.get_fact()
            if 'поговорк' in self.commandline or 'пословиц' in self.commandline:
                result = self.get_saying()

            talk(result, speech_rate=100)
            time.sleep(0.2)
            if 'поговорк' not in self.commandline:
                talk(random.choice(dg.qustion_replay))
        except requests.exceptions.ConnectionError:
            talk('Упс! Что-то не так пошло! Скорее всего сеть отсутствует.')


class ExchangeRates:

    def __init__(self, commandline, intersection):
        if intersection < 2 or not tls.check_internet():
            return
        self.commandline = commandline

    @staticmethod
    def correct_value_rate(float_num: float) -> str:
        try:
            rate = round(float_num, 2)
            res = f'{str(rate)}0' if len(str(rate).split('.')[1]) == 1 else str(rate)
            return f'{int(rate)} гривен' if int(rate) == float(rate) else f'{res.replace(".", " гривен ")} копеек'
        except ValueError:
            pass

    def determine_the_currency(self) -> tuple[str, str]:
        key = 'usd'
        currency = 'доллара'

        if 'евро' in self.commandline:
            key, currency = 'eur', 'евро'
        elif 'злот' in self.commandline or 'польск' in self.commandline:
            key, currency = 'pln', 'польского злотого'

        return key, currency

    def get_exchange_rates(self) -> None:
        current_date = dt.today().strftime('%d-%m-%Y %H:%M:%S')
        currency_key, currency = self.determine_the_currency()
        url = f'https://minfin.com.ua/currency/banks/{currency_key}/'

        try:
            r = requests.get(url)
            if r.status_code != 200:
                print(f'  Status code: {r.status_code} !!!')
                return talk('Упс! Целевой сервер не отвечает.')

            soup = BeautifulSoup(r.text, 'html.parser')
            soup_banks_names = soup('td', class_='js-ex-rates mfcur-table-bankname')
            soup_buy = soup.find_all('td', class_='responsive-hide mfm-text-right mfm-pr0')
            soup_sale = soup.find_all('td', class_='responsive-hide mfm-text-left mfm-pl0')

            exchange_rates: dict = {}
            len_banks_names: list = []
            count = 0

            while len(exchange_rates) <= 5:
                buy = soup_buy[count].text
                sale = soup_sale[0].text if count == 0 else soup_sale[count * 2].text

                if buy and sale:
                    bank_name = soup_banks_names[count].text.replace('\n', '').strip()
                    len_banks_names.append(len(bank_name))
                    exchange_rates[bank_name] = {'buy': buy, 'sale': sale}

                count += 1

            max_len_bank_name: int = max(len_banks_names)
            print()
            print(f'{current_date}{" " * (max_len_bank_name - len(str(current_date)))}  {currency_key.upper()}')

            for key in exchange_rates.keys():
                pstring = f'{key}: {exchange_rates[key]["buy"]} / {exchange_rates[key]["sale"]}'
                index = max_len_bank_name - len(key)
                print(f'{" " * index}{pstring}')

            bank_name = soup_banks_names[0].text.replace('\n', '')
            buy = round(float(soup_buy[0].text), 2)
            sale = round(float(soup_sale[0].text), 2)

            print()
            talk(f'В {bank_name}е курс {currency} к гривне сегодня:')
            talk(f' Покупка: {self.correct_value_rate(buy)}. Продажа: {self.correct_value_rate(sale)}.')

        except requests.exceptions.ConnectionError:
            print('Ups(')


class Translators:
    def __init__(self, commandline, reverse=False):
        if not tls.check_internet():
            return
        self.commandline = commandline
        self.reverse = reverse

    def check_language(self) -> tuple[str, str]:
        from_lang, to_lang = 'ru', 'en'
        languages: dict = {'украинск': 'ukr',
                           'русск': 'ru',
                           'английск': 'en',
                           'немецк': 'de',
                           'итальянск': 'it',
                           'французск': 'fr',
                           'испанск': 'es'}

        for lang in languages.keys():
            if f'с {lang}' in self.commandline:
                from_lang = languages[lang]
            if f'на {lang}' in self.commandline:
                to_lang = languages[lang]

        return from_lang, to_lang

    @staticmethod
    def get_google_translate(string: str, lang: str) -> str:
        from googletrans import Translator

        try:
            tr = Translator()
            result = tr.translate(string, dest=lang)
            return result.text.lower()

        except requests.exceptions.ConnectionError:
            talk('Упс! Что-то не так пошло с Гуглом!')
            return ':('

    @staticmethod
    def get_tranlate(string, f_lang, t_lang) -> str:
        from translate import Translator

        try:
            tr = Translator(from_lang=f_lang, to_lang=t_lang)
            result = tr.translate(string)
            return result.lower()

        except requests.exceptions.ConnectionError:
            talk('Упс! Сервер не отвечает.')
            return ':('

    def get_result(self) -> None:
        from_lang, to_lang = self.check_language()

        if self.reverse:
            from_lang, to_lang = to_lang, from_lang
        from_to = f'  {from_lang.upper()} -> {to_lang.upper()}'
        print(from_to)

        text = get_input() if tls.check_hand_input(self.commandline) else None

        if 'текст' in self.commandline and not text:
            split_commandline = self.commandline.split()
            index = split_commandline.index('текст')
            text = ' '.join(split_commandline[index + 1:])

        if not text:
            return

        tls.answer_ok_and_pass()
        translator_res = self.get_tranlate(text, from_lang, to_lang)
        googletrans_res = self.get_google_translate(text, to_lang)
        os.system('clear')
        print(f'  {from_to}', '\n')
        print(f'  Текст: "{text}"')
        print(f'  {translator_res} - версия translate')
        print(f'  {googletrans_res} - версия googletrans', '\n')
        talk(random.choice(dg.done))


class SysInformer:
    @classmethod
    def correct_size(cls, bts, ending='iB') -> str:
        _size = 1024
        for item in ["", "K", "M", "G", "T", "P"]:
            if bts < _size:
                return f"{bts:.2f}{item}{ending}"
            bts /= _size

    def create_sysinfo(self) -> dict[str, dict]:
        collect_info_dict: dict = {}

        if 'info' not in collect_info_dict:
            collect_info_dict['info']: dict = {}
            collect_info_dict['info']['system_info']: dict = {}
            collect_info_dict['info']['system_info'] = {
                'system': {'comp_name': uname().node,
                           'os_name': f"{uname().system} {uname().release}",
                           'version': uname().version,
                           'machine': uname().machine},
                'processor': {'name': cpuinfo.get_cpu_info()['brand_raw'],
                              'phisycal_core': psutil.cpu_count(logical=False),
                              'all_core': psutil.cpu_count(logical=True),
                              'freq_max': f"{psutil.cpu_freq().max:.2f}MHz"},
                'ram': {'volume': self.correct_size(psutil.virtual_memory().total),
                        'aviable': self.correct_size(psutil.virtual_memory().available),
                        'used': self.correct_size(psutil.virtual_memory().used)}
            }

        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
            except PermissionError:
                continue

            if 'disk_info' not in collect_info_dict['info']:
                collect_info_dict['info']['disk_info']: dict = {}

            if f"'device': {partition.device}" not in collect_info_dict['info']['disk_info']:
                collect_info_dict['info']['disk_info'][partition.device]: dict = {}
                collect_info_dict['info']['disk_info'][partition.device] = {
                    'file_system': partition.fstype,
                    'size_total': self.correct_size(partition_usage.total),
                    'size_used': self.correct_size(partition_usage.used),
                    'size_free': self.correct_size(partition_usage.free),
                    'percent': f'{partition_usage.percent}'
                }

        iface_name, local_ip, mac = '', '', ''

        for i in psutil.net_if_addrs().keys():
            for n in psutil.net_if_addrs()[i]:
                if n.broadcast and n.netmask:
                    iface_name = i
                    local_ip = n.address
                if n.broadcast and i == iface_name:
                    mac = n.address

        collect_info_dict['info']['net_info']: dict = {}
        collect_info_dict['info']['net_info'][iface_name] = {'mac': mac, 'local_ip': local_ip}
        return collect_info_dict

    @staticmethod
    def print_info(dict_info: dict) -> None:

        for item in dict_info['info']:
            if item == "system_info":
                for elem in dict_info['info'][item]:

                    if elem == 'system':
                        print(f"[+] Информация о системе\n"
                              f"  - Имя компьютера: {dict_info['info'][item][elem]['comp_name']}\n"
                              f"  - Опереционная система: {dict_info['info'][item][elem]['os_name']}\n"
                              f"  - Сборка: {dict_info['info'][item][elem]['version']}\n"
                              f"  - Архитектура: {dict_info['info'][item][elem]['machine']}\n")

                    if elem == 'processor':
                        print(f"[+] Информация о процессоре\n"
                              f"  - Семейство: {dict_info['info'][item][elem]['name']}\n"
                              f"  - Физические ядра: {dict_info['info'][item][elem]['phisycal_core']}\n"
                              f"  - Всего ядер: {dict_info['info'][item][elem]['all_core']}\n"
                              f"  - Максимальная частота: {dict_info['info'][item][elem]['freq_max']}\n")

                    if elem == 'ram':
                        print(f"[+] Оперативная память\n"
                              f"  - Объем: {dict_info['info'][item][elem]['volume']}\n"
                              f"  - Доступно: {dict_info['info'][item][elem]['aviable']}\n"
                              f"  - Используется: {dict_info['info'][item][elem]['used']}\n")

            if item == "disk_info":
                for elem in dict_info['info'][item]:
                    print(f"[+] Информация о дисках\n"
                          f"  - Имя диска: {elem}\n"
                          f"  - Файловая система: {dict_info['info'][item][elem]['file_system']}\n"
                          f"  - Объем диска: {dict_info['info'][item][elem]['size_total']}\n"
                          f"  - Занято: {dict_info['info'][item][elem]['size_used']}\n"
                          f"  - Свободно: {dict_info['info'][item][elem]['size_free']}\n"
                          f"  - Заполненность: {dict_info['info'][item][elem]['percent']}%\n")

            if item == "net_info":
                for elem in dict_info['info'][item]:
                    print(f"[+] Информация о сети\n"
                          f"  - Имя интерфейса: {elem}\n"
                          f"  - MAC-адрес: {dict_info['info'][item][elem]['mac']}\n"
                          f"  - Local IP: {dict_info['info'][item][elem]['local_ip']}\n")

    @staticmethod
    def sys_monitoring() -> None:
        core_temp_warning = 90.0
        core_temp_critical = 95.0
        gpu_temp_warning = 93.0
        gpu_temp_critical = 98.0
        ram_per_warning = 90.0
        ram_per_critical = 98.0
        gpus = GPUtil.getGPUs()
        cores_temps = []
        gpus_temps = []

        [cores_temps.append(temp.current) for temp in psutil.sensors_temperatures()['coretemp']]
        [gpus_temps.append(gpu.temperature) for gpu in gpus]

        ram_per_used: float = psutil.virtual_memory().percent
        swap_per_used: float = psutil.swap_memory().percent
        core_temp: float = max(cores_temps)
        gpu_temp: float = max(gpus_temps)

        # Следим за оперативной памятью
        if ram_per_warning <= ram_per_used < ram_per_critical:
            talk(f'ВНИМАНИЕ! Оперативная память заполнена на {int(round(ram_per_used, 0))}%!')
        if ram_per_used >= ram_per_critical:
            talk(f'ВНИМАНИЕ! Критично! Оперативная память заполнена на {int(round(ram_per_used, 0))}%!')
        # Следим за swap-диском
        if ram_per_warning <= swap_per_used < ram_per_critical:
            talk(f'ВНИМАНИЕ! Swap заполнен на {int(round(swap_per_used, 0))}%!')
        if swap_per_used >= ram_per_critical:
            talk(f'ВНИМАНИЕ! Критично! Swap заполнен на {int(round(swap_per_used, 0))}%!')
        # Следим за температурой ядра
        if core_temp_warning <= core_temp < core_temp_critical:
            talk(f'ВНИМАНИЕ! Температура ядра́ {int(round(core_temp, 0))}°!')
        if core_temp >= core_temp_critical:
            talk(f'ВНИМАНИЕ! Критично! Температура ядра́ {int(round(core_temp, 0))}°!')
        # Следим за температурой графического ядра
        if gpu_temp_warning <= gpu_temp < gpu_temp_critical:
            talk(f'ВНИМАНИЕ! Температура графического ядра́ {int(round(gpu_temp, 0))}°!')
        if gpu_temp >= gpu_temp_critical:
            talk(f'ВНИМАНИЕ! Критично! Температура графического ядра́ {int(round(gpu_temp, 0))}°!')

        print(f'-infolabele-■ Core temp: {core_temp}°  ■ GPU temp: {gpu_temp}°  ■ '
              f'Mem used: {ram_per_used}%  ■ SWAP Used: {swap_per_used}%  ■ Runtime: no process', end='')

    def get_sysinfo(self) -> None:
        sysinfo = self.create_sysinfo()
        self.print_info(sysinfo)


class AssistantSettings:
    config_path = pathlib.Path(__file__).parent.absolute() / "settings.ini"
    config = configparser.ConfigParser()
    config.read(config_path)

    def __init__(self, commandline):
        self.commandline = commandline
        self.param = w2n(commandline)

    @staticmethod
    def update_settings(old_param, new_param, category: str = '') -> None:
        with open('settings.ini', 'r') as f:
            old_data = f.read()
            new_data = old_data.replace(old_param, new_param)

        with open('settings.ini', 'w') as f:
            f.write(new_data)
        print(f'  {new_param}')

        if category == 'Speech':
            talk('Мои настройки го́лоса будут изменены!')
        elif category == 'Mic':
            talk('Настройки микрофона будут изменены!')
        else:
            talk('Мои настройки будут изменены!')

        tls.restart_app()

    def change_conf_set(self) -> None:
        config = configparser.ConfigParser()
        config.read("settings.ini")
        param = w2n(self.commandline)

        if not isinstance(param, int):
            return

        if 'высота' in self.commandline:
            old_pitch = config['Speech']['speech_pitch']
            self.update_settings(f'speech_pitch={old_pitch}', f'speech_pitch={param}', category='Speech')
        elif 'скорость' in self.commandline:
            old_rate = config['Speech']['speech_rate']
            self.update_settings(f'speech_rate={old_rate}', f'speech_rate={param}', category='Speech')
        elif 'чувствительность' in self.commandline:
            old_sensitivity = config['Mic']['mic_up']
            self.update_settings(f'mic_up={old_sensitivity}', f'mic_up={param}', category='Mic')

    def change_volume(self) -> None:
        value = w2n(self.commandline)
        check_done = False

        if 'громкость' in self.commandline and isinstance(value, int):
            run(f'amixer -D pulse sset Master {value}% >/dev/null', shell=True)
            check_done = True

        elif 'громче' in self.commandline:
            run('amixer -D pulse sset Master 10%+ >/dev/null', shell=True)
            check_done = True

        elif 'тише' in self.commandline:
            run('amixer -D pulse sset Master 10%- >/dev/null', shell=True)
            check_done = True

        if check_done:
            volume_str = check_output(f'''amixer scontents | grep "Left: Playback" | awk -F " " '{{print $5}}' ''',
                                      encoding='utf-8',
                                      shell=True)
            volume_val = re.sub(r'[][]', '', volume_str)
            print(f'  Громкость: {volume_val.strip()}')
            return talk(random.choice(dg.done))


class ScriptStarter:
    scriptdir = f'{homedir}/scripts/'

    def __init__(self, script_key, intersection):
        self.script_key = script_key
        self.intersection = intersection

    def get_script(self) -> tuple[str, str]:
        script, script_name = None, ''.join(self.script_key.split('_')[-1])

        if script_name == 'nmstart' and self.intersection == 3 \
                or script_name == 'cleancashe' and self.intersection == 2:
            script = f'{tls.choice_xterm("XtermSmall")} sudo {self.scriptdir}./{script_name}.sh &'
        elif script_name == 'sysfullupgrade' and self.intersection == 2:
            script = f'{tls.choice_xterm("Xterm")} sudo {self.scriptdir}./{script_name}.sh &'
        return script, script_name

    def run_script(self) -> None:
        scr, scr_name = self.get_script()
        if not scr:
            return
        tls.answer_ok_and_pass()
        if 'sudo' in scr:
            tls.answer_ok_and_pass(answer=False, enter_pass=True)
        print(f'  Script: run {scr_name}.sh')
        run(scr, shell=True)


class Anonimizer:

    @staticmethod
    def component_check() -> bool:
        path_tor = '/usr/sbin/tor'
        path_toriptables2 = '/usr/local/bin/toriptables2.py'
        path_python2 = '/usr/bin/python2'
        path_iptables = '/usr/sbin/iptables'

        if not os.path.isfile(path_tor):
            talk('Тор в системе не обнаружен!')
            print('Для установки Tor, выполнить: <sudo apt install tor>')
            return False

        if not os.path.isfile(path_iptables):
            talk('Айпи тэйбл в системе не обнаружен!')
            print('Для установки iptables, выполнить: <sudo apt install iptables>')
            return False

        if not os.path.isfile(path_toriptables2):
            talk('Тор айпи тэйбл в системе не обнаружен! Для установки, следуйте инструкции!')
            print('Для установки toriptables2, выполнить в терминале:')
            print('1) <git clone https://github.com/ruped24/toriptables2>')
            print('2) <cd toriptables2/>')
            print('3) <sudo mv toriptables2.py /usr/local/bin/>')
            print('4) <cd>')
            return False

        if not os.path.isfile(path_python2):
            talk('Для работы скрипта необходим пайтон2!')
            print('Выполнить в терминале: <sudo apt install python2>')
            return False

        return True

    def __init__(self, intersection, on_off):
        if intersection < 2 or not tls.check_internet() or not self.component_check():
            return
        self.on_off = on_off

    @staticmethod
    def get_ip() -> str:
        url = 'https://check.torproject.org/api/ip'
        try:
            my_public_ip = requests.get(url).json()['IP']
            return my_public_ip
        except requests.exceptions.ConnectionError:
            talk('Похоже проблемы с интернетом!')

    def start_stop_anonimizer(self) -> None:
        if self.on_off == 'on':
            ipaddress = self.get_ip()
            print(f'  Мой IP: {ipaddress}')
            tls.answer_ok_and_pass(enter_pass=True)
            mic_sins(0)
            run(f'{tls.choice_xterm("XtermSmall")} sudo toriptables2.py -l', shell=True)
            new_ipaddress = self.get_ip()
            print(f'  Мой новый IP: {new_ipaddress}')
            return talk('Упс! Не вышло') if ipaddress == new_ipaddress else talk(random.choice(dg.done))

        if self.on_off == 'off':
            tls.answer_ok_and_pass(enter_pass=True)
            mic_sins(0)
            run(f'{tls.choice_xterm("XtermSmall")} sudo toriptables2.py -f', shell=True)
            print(f'  Мой IP: {self.get_ip()}')
            return talk(random.choice(dg.done))


class FileLife:
    homedir = os.getcwdb().decode(encoding='utf-8')
    note_dir = os.path.abspath('notebook')

    @staticmethod
    def file_name_assignment(path: str, name='') -> str:
        print(f'"{path}"')
        file_name = name

        while True:
            if not file_name:
                print('  Рекомендуемый формат имени файла: [name.extension]')
                talk('Введите имя файла!')
                file_name = get_input()
                file_name = file_name.replace(' ', '_')

            if os.path.isfile(f'{path}/{file_name}'):
                talk('Файл с таким именем уже существует. Необходимо выбрать другое имя!')
                file_name = ''
                continue

            if file_name == '':
                talk('Имя файла не может быть пустым!')
            else:
                return file_name

    def read_file(self, file: str) -> None:
        f = open(f'{self.note_dir}/{file}', 'r')
        [print(line, end='') for line in f]
        print()
        f.close()

    def create_file(self, name='', data='') -> bool:
        file_name = self.file_name_assignment(self.note_dir, name)

        file = open(f'{self.note_dir}/{file_name}', 'w+')
        if data:
            file.write(str(data))
        file.close()
        return True

    def rename_file(self, old_name: str) -> None:
        new_file_name = self.file_name_assignment(self.note_dir, get_input(old_name))
        old_file = os.path.join(self.note_dir, old_name)
        new_file = os.path.join(self.note_dir, new_file_name)
        tls.answer_ok_and_pass()
        os.rename(old_file, new_file)

    def create_memo_file(self, cmd: str) -> bool:
        memo_data = get_input() if tls.check_hand_input(cmd) \
            else tls.get_meat('create_memo_file', cmd, dg.notebook_action_dict)
        if not memo_data:
            return False

        short_name = ' '.join(memo_data.split()[0:3])
        current_time = datetime.datetime.now().strftime('%d%m%y')
        file_name = f'''{short_name}_{current_time}.txt'''.replace(' ', '_')
        memo_data = w2n(memo_data, otherwords=True)

        if self.create_file(file_name, memo_data):
            talk('Мемо-файл создан!')

    def edit_file(self, file: str) -> None:
        tls.answer_ok_and_pass()
        run(f'kate {self.note_dir}/{file} &', shell=True)

    def delete_file(self, file: str, permission=False) -> str:
        if permission:
            os.remove(f'{self.note_dir}/{file}')
            talk(random.choice(dg.done))
        else:
            talk(f'Действительно удалить файл?')
            print(f'"{file}"')
            return 'not permission'


if __name__ == '__main__':
    sinfo = SysInformer()
    sinfo.get_sysinfo()
