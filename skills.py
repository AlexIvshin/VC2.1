# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import datetime
from datetime import date, datetime as dt
import GPUtil
from googletrans import Translator
import os
import psutil
import random
import randfacts
import re
import requests
from subprocess import run, check_output, call, CompletedProcess
from tabulate import tabulate as tb
import time
from typing import Union, Optional, Any

# Модули приложения
import dialog as dg
from model_voice import Voice
import support_skills as ss
from widgets.hand_input_widget import get_input
from wordstonum import word2num_ru as w2n

talk = Voice().speaks
mic_sins = Voice().mic_sensitivity

homedir = os.getcwdb().decode(encoding='utf-8')


class ProgramManager:

    def __init__(self, program, action):
        self.program = program
        self.action = action

    def start_stop_program(self) -> CompletedProcess[bytes]:
        prg = self.program

        ss.answer_ok_and_pass()

        if self.action == 'on':
            prg = '~/tor-browser/Browser/start-tor-browser' if prg == 'tor' else prg
            print(f'  {self.program.capitalize()} starts!')
            return run(f'{prg} >/dev/null 2>&1 &', shell=True)

        if self.action == 'off':
            prg = 'chrome' if prg == 'google-chrome' else prg
            if call(f'pgrep {prg} >/dev/null', shell=True) == 0:
                print(f'  {prg.capitalize()} will be closed!')
                return run(f'pkill {prg} >/dev/null 2>&1', shell=True)


class Calculator:

    def __init__(self, commandline):
        self.cmd = commandline
        self.n1, self.operator, self.n2 = self.get_calc_elem()

    @classmethod
    def check_type_num(cls, n) -> Union[float, int]:
        try:
            return float(n) if '.' in n else int(n)
        except ValueError:
            pass

    def get_calc_elem(self) -> tuple[float | int, str | None, float | int] | tuple[None, None, None]:
        opers: dict = {
            'плюс': '+', 'минус': '-', 'отнять': '-', 'умножить на': '*', 'множить на': '*',
            'разделить на': '/', 'раздели на': '/', 'дели на': '/', 'делить на': '/'}
        calc_string = w2n(self.cmd, otherwords=True).split()
        nums_index: list = []
        for i in calc_string:
            try:
                nums_index.append(calc_string.index(i)) if float(i) else None
            except ValueError:
                pass
        if len(nums_index) == 2:
            n1, n2 = self.check_type_num(calc_string[nums_index[0]]), self.check_type_num(calc_string[nums_index[1]])
            opr_str = ' '.join(calc_string[nums_index[0] + 1:nums_index[1]])
            operator: str = opers[opr_str] if opr_str in opers.keys() else None
            if operator:
                return n1, operator, n2
        return None, None, None

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

        ss.answer_ok_and_pass()
        print()
        print(f'  {self.n1} {self.operator} {self.n2} = {round(result, 4)}')
        print()

        if isinstance(result, int):
            return talk(f'Будет: {result}')
        if isinstance(result, float):
            return talk(f'Приблизительно будет: {get_correct_float_res(result)}')


class SearchEngine:
    import wikipedia
    wikipedia.set_lang("ru")  # Установка русского языка для Википедии

    def __init__(self, cmd, action, confirm):
        self.commandline = cmd
        self.action = action
        self.confirm = confirm
        self.search_words = get_input() if ss.check_hand_input(cmd) else ss.get_meat(action, cmd, dg.actions_dict)

    def get_result(self) -> None:
        if not self.search_words or not ss.check_internet():
            return
        if not self.confirm:
            return talk(f'Искать {self.search_words}?')

        talk(random.choice(dg.answer_ok))
        print(f'  Ищу: "{self.search_words}"')

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
        import webbrowser
        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.chrome.options import Options

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
            result = cls.wikipedia.search(text)
            page = cls.wikipedia.page(result[0])
            title = page.title
            content = page.content
            run(f'{ss.choice_xterm("XtermSearch")} echo "{title}{content}" &', shell=True)
            talk('Это всё, что удалось найти!')

        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError, OSError):
            cls.exception_words()
        except (cls.wikipedia.exceptions.DisambiguationError, cls.wikipedia.exceptions.PageError):
            cls.exception_words(wiki_error=True)

    @classmethod
    def wiki_short_answer(cls, text: str) -> None:
        try:
            result = cls.wikipedia.summary(text, sentences=3)
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
        except (cls.wikipedia.exceptions.DisambiguationError, cls.wikipedia.exceptions.PageError):
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

    def __init__(self, commandline):
        self.commandline = commandline

    @classmethod
    def get_week_day(cls, number: int) -> int:
        return date.isoweekday(datetime.date.today() + datetime.timedelta(days=number))

    def get_url(self) -> str | None:
        for key in self.cities:
            if key in self.commandline:
                return f'{self.site_url}/погода-{self.cities[key]}'
        talk('Не поняла, погода в каком городе?')
        return None

    def get_weather_forecast(self) -> None:
        url_weather_city = self.get_url()
        if not url_weather_city or not ss.check_internet():
            return

        try:
            r = requests.get(url_weather_city)
            if r.status_code != 200:
                print(f'Status code: {r.status_code} !!!')
                return talk('Упс! Целевой сервер не отвечает.')

            talk(random.choice(dg.answer_ok))
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

            current_weekday = int(date.isoweekday(date.today()))
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
    def __init__(self, commandline):
        self.commandline = commandline

    @staticmethod
    def get_joke() -> Optional[Any]:
        if not ss.check_internet():
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
        if not ss.check_internet():
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
            talk(random.choice(dg.qustion_replay))

        except requests.exceptions.ConnectionError:
            talk('Упс! Что-то не так пошло! Скорее всего сеть отсутствует.')


class ExchangeRates:

    def __init__(self, commandline):
        self.commandline = commandline

    @staticmethod
    def get_correct_value_rate(float_num: float) -> str:

        if type(float_num) != float:
            return 'no data'

        rate = round(float_num, 2)
        rate_str = f'{str(rate)}0' if len(str(rate).split('.')[1]) == 1 else str(rate)
        rate_str = rate_str.replace(
            rate_str.split('.')[-1],
            str(int(rate_str.split('.')[-1])))

        g = int(rate_str.split('.')[0][-1])
        k = int(rate_str.split('.')[1][-1])
        grn = 'гривен'

        if g == 1:
            grn = 'гривна'
        if 5 > g > 1:
            grn = 'гривны'
        if int(rate) != float(rate):
            kop = 'копеек'
            if k == 1:
                kop = 'копейка'
            if 5 > k > 1:
                kop = 'копейки'
            return f'{rate_str.replace(".", f" {grn} ")} {kop}.'

        return f'{int(rate)} {grn}'

    def determine_the_currency(self) -> tuple[str, str]:
        key = 'usd'
        currency = 'доллара'
        if 'евро' in self.commandline:
            key, currency = 'eur', 'евро'
        elif 'злот' in self.commandline or 'польск' in self.commandline:
            key, currency = 'pln', 'польского злотого'
        return key, currency

    def get_exchange_rates(self) -> None:
        if not ss.check_internet():
            return

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
            talk(f' Покупка: {self.get_correct_value_rate(buy)}. Продажа: {self.get_correct_value_rate(sale)}.')

        except requests.exceptions.ConnectionError:
            print('Упс! Что-то не так пошло! Скорее всего сеть отсутствует.')


class Translators:
    def __init__(self, commandline, reverse=False):
        self.commandline = commandline
        self.reverse = reverse

    def check_language(self) -> tuple[str, str]:
        from_lang, to_lang = 'ru', 'en'
        languages: dict = {
            'украинск': 'ukr', 'русск': 'ru', 'английск': 'en', 'немецк': 'de',
            'итальянск': 'it', 'французск': 'fr', 'испанск': 'es'
        }
        for lang in languages.keys():
            if f'с {lang}' in self.commandline:
                from_lang = languages[lang]
            if f'на {lang}' in self.commandline:
                to_lang = languages[lang]
        return from_lang, to_lang

    @staticmethod
    def get_google_translate(string: str, lang: str) -> str | None:
        try:
            tr = Translator()
            result = tr.translate(string, dest=lang)
            return result.text.lower()
        except requests.exceptions.ConnectionError:
            return talk('Упс! Что-то не так пошло с Гуглом!')

    @staticmethod
    def get_tranlate(string, f_lang, t_lang) -> str | None:
        from translate import Translator

        try:
            tr = Translator(from_lang=f_lang, to_lang=t_lang)
            result = tr.translate(string)
            return result.lower()
        except requests.exceptions.ConnectionError:
            return talk('Упс! Сервер не отвечает.')

    def get_result(self) -> None:
        if not ss.check_internet():
            return

        from_lang, to_lang = self.check_language()

        if self.reverse:
            from_lang, to_lang = to_lang, from_lang
        from_to = f'  {from_lang.upper()} -> {to_lang.upper()}'
        print(from_to)

        text = get_input() if ss.check_hand_input(self.commandline) else None

        if 'текст' in self.commandline and not text:
            split_commandline = self.commandline.split()
            index = split_commandline.index('текст')
            text = ' '.join(split_commandline[index + 1:])

        if not text:
            return

        ss.answer_ok_and_pass()
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
        import cpuinfo
        import psutil
        from platform import uname

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
    def pars_info(dict_info: dict) -> list[str]:
        sys_info = []
        gpus = GPUtil.getGPUs()
        gpu_name = gpu_total_mem = gpu_free_mem = 'Нет данных'

        for gpu in gpus:
            if gpu.display_active == gpu.display_mode == 'Enabled':
                gpu_name = gpu.name
                gpu_total_mem = f'{int(gpu.memoryTotal)}Mb'
                gpu_free_mem = f'{int(gpu.memoryFree)}Mb'

        for item in dict_info['info']:
            if item == "system_info":
                for elem in dict_info['info'][item]:
                    if elem == 'system':
                        sys_info.append(
                            f"\n[+] Информация о системе:\n"
                            f"    - Имя компьютера: {dict_info['info'][item][elem]['comp_name']}\n"
                            f"    - Опереционная система: {dict_info['info'][item][elem]['os_name']}\n"
                            f"    - Сборка: {dict_info['info'][item][elem]['version']}\n"
                            f"    - Архитектура: {dict_info['info'][item][elem]['machine']}\n\n"
                        )

                    if elem == 'processor':
                        sys_info.append(
                            f"[+] Информация о процессоре:\n"
                            f"    - Семейство: {dict_info['info'][item][elem]['name']}\n"
                            f"    - Физические ядра: {dict_info['info'][item][elem]['phisycal_core']}\n"
                            f"    - Всего ядер: {dict_info['info'][item][elem]['all_core']}\n"
                            f"    - Максимальная частота: {dict_info['info'][item][elem]['freq_max']}\n\n"
                        )

                    if elem == 'ram':
                        sys_info.append(
                            f"[+] Оперативная память:\n"
                            f"    - Объем: {dict_info['info'][item][elem]['volume']}\n"
                            f"    - Доступно: {dict_info['info'][item][elem]['aviable']}\n"
                            f"    - Используется: {dict_info['info'][item][elem]['used']}\n\n"
                        )

            if item == "disk_info":
                for elem in dict_info['info'][item]:
                    sys_info.append(
                        f"[+] Информация о дисках:\n"
                        f"    - Имя диска: {elem}\n"
                        f"    - Файловая система: {dict_info['info'][item][elem]['file_system']}\n"
                        f"    - Объем диска: {dict_info['info'][item][elem]['size_total']}\n"
                        f"    - Занято: {dict_info['info'][item][elem]['size_used']}\n"
                        f"    - Свободно: {dict_info['info'][item][elem]['size_free']}\n"
                        f"    - Заполненность: {dict_info['info'][item][elem]['percent']}%\n\n"
                    )

            if item == "net_info":
                for elem in dict_info['info'][item]:
                    sys_info.append(
                        f"[+] Информация о сети\n"
                        f"    - Имя интерфейса: {elem}\n"
                        f"    - MAC-адрес: {dict_info['info'][item][elem]['mac']}\n"
                        f"    - Local IP: {dict_info['info'][item][elem]['local_ip']}\n\n"
                    )

        sys_info.append(
            f"[+] Информация о видеокарте\n"
            f"    - Модель: {gpu_name}\n"
            f"    - Обьём памяти: {gpu_total_mem}\n"
            f"    - Свободно памяти: {gpu_free_mem}\n"
        )

        return sys_info

    @staticmethod
    def sys_monitoring() -> None:
        core_temp_warning = 95
        core_temp_critical = 100
        ram_per_warning = 90
        ram_per_critical = 98

        try:
            gpu_temp_warning = 98
            gpu_temp_critical = 102
            gpus = GPUtil.getGPUs()
            gpus_temps = []
            [gpus_temps.append(gpu.temperature) for gpu in gpus]
            gpu_temp: float = int(round(max(gpus_temps), 0))

            # Следим за температурой графического ядра
            if gpu_temp_warning <= gpu_temp < gpu_temp_critical:
                talk(f'ВНИМАНИЕ! Температура графического ядра́ {gpu_temp}°!')
            if gpu_temp >= gpu_temp_critical:
                talk(f'ВНИМАНИЕ! Критично! Температура графического ядра́ {gpu_temp}°!')

        except ValueError:
            gpu_temp: str = '??'

        cores_temps = []
        [cores_temps.append(temp.current) for temp in psutil.sensors_temperatures()['coretemp']]

        ram_per_used: float = int(round(psutil.virtual_memory().percent, 0))
        swap_per_used: float = int(round(psutil.swap_memory().percent, 0))
        core_temp: float = int(round(max(cores_temps), 0))

        # Следим за оперативной памятью
        if ram_per_warning <= ram_per_used < ram_per_critical:
            talk(f'ВНИМАНИЕ! Оперативная память заполнена на {ram_per_used}%!')
        if ram_per_used >= ram_per_critical:
            talk(f'ВНИМАНИЕ! Критично! Оперативная память заполнена на {ram_per_used}%!')

        # Следим за swap-диском
        if swap_per_used:
            if ram_per_warning <= swap_per_used < ram_per_critical:
                talk(f'ВНИМАНИЕ! Swap заполнен на {swap_per_used}%!')
            if swap_per_used >= ram_per_critical:
                talk(f'ВНИМАНИЕ! Критично! Swap заполнен на {swap_per_used}%!')

        # Следим за температурой ядра
        if core_temp_warning <= core_temp < core_temp_critical:
            talk(f'ВНИМАНИЕ! Температура ядра́ {core_temp}°!')
        if core_temp >= core_temp_critical:
            talk(f'ВНИМАНИЕ! Критично! Температура ядра́ {core_temp}°!')

        swap_str = 'not used' if swap_per_used == 0 else f'{swap_per_used}%'
        print(f'-infolabele-■ Core temp: {core_temp}°  ■ GPU temp: {gpu_temp}°  ■ '
              f'Mem used: {ram_per_used}%  ■ SWAP Used: {swap_str}  ■ Runtime: no process', end='')

    def get_sysinfo(self) -> list[str]:
        sysinfo = self.create_sysinfo()
        return self.pars_info(sysinfo)


class AssistantSettings:

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

        ss.restart_app()

    def change_conf_set(self) -> None:
        import configparser
        import pathlib

        config_path = pathlib.Path(__file__).parent.absolute() / "settings.ini"
        config = configparser.ConfigParser()
        config.read(config_path)
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
    DIR = f'{homedir}/scripts/'

    def __init__(self, script_key):
        self.script_key = script_key

    def get_script(self) -> tuple[str, str]:
        scr_name = ''.join(self.script_key.split('_')[-1])
        sudo = 'sudo' if 'sudo' in self.script_key else ''
        category = ''.join(self.script_key.split('_')[-2])
        scr_str = f'{ss.choice_xterm(category)} {sudo} {self.DIR}./{scr_name}.sh &'
        return scr_str, scr_name

    def run_script(self) -> None:
        scr, scr_name = self.get_script()
        if not scr:
            return
        run(scr, shell=True)
        print(f'  Script: Run {scr_name}.sh')
        passwd = True if 'sudo' in scr else False
        ss.answer_ok_and_pass(answer=False, enter_pass=passwd)


class Anonimizer:

    @staticmethod
    def component_check() -> bool:
        path_tor = '/usr/sbin/tor'
        path_toriptables2 = '/usr/local/bin/toriptables2.py'
        path_python2 = '/usr/bin/python2'
        path_iptables = '/usr/sbin/iptables'

        if not os.path.isfile(path_tor):
            talk('Тор в системе не обнаружен!')
            print('  Для установки Tor, выполнить: <sudo apt install tor>')
            return False

        if not os.path.isfile(path_iptables):
            talk('Айпи тэйбл в системе не обнаружен!')
            print('  Для установки iptables, выполнить: <sudo apt install iptables>')
            return False

        if not os.path.isfile(path_toriptables2):
            talk('Тор айпи тэйбл в системе не обнаружен! Для установки, следуйте инструкции!')
            print('  Для установки toriptables2, выполнить в терминале:')
            print('  1) <git clone https://github.com/ruped24/toriptables2>')
            print('  2) <cd toriptables2/>')
            print('  3) <sudo mv toriptables2.py /usr/local/bin/>')
            print('  4) <cd>')
            return False

        if not os.path.isfile(path_python2):
            talk('Для работы скрипта необходим пайтон2!')
            print('  Выполнить в терминале: <sudo apt install python2>')
            return False

        return True

    def __init__(self, on_off):
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
        if not ss.check_internet() or not self.component_check():
            return

        if self.on_off == 'on':
            ipaddress = self.get_ip()
            print(f'  Мой IP: {ipaddress}')
            ss.answer_ok_and_pass(enter_pass=True)
            mic_sins(0)
            run(f'{ss.choice_xterm("XtermSmall")} sudo toriptables2.py -l', shell=True)
            new_ipaddress = self.get_ip()
            print(f'  Мой новый IP: {new_ipaddress}')
            return talk('Упс! Не вышло') if ipaddress == new_ipaddress else talk(random.choice(dg.done))

        if self.on_off == 'off':
            ss.answer_ok_and_pass(enter_pass=True)
            mic_sins(0)
            run(f'{ss.choice_xterm("XtermSmall")} sudo toriptables2.py -f', shell=True)
            print(f'  Мой IP: {self.get_ip()}')
            return talk(random.choice(dg.done))


class File:
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
        ss.answer_ok_and_pass()
        os.rename(old_file, new_file)

    def create_memo_file(self, cmd: str) -> bool:
        memo_data = get_input() if ss.check_hand_input(cmd) \
            else ss.get_meat('create_memo_file', cmd, dg.notebook_action_dict)
        if not memo_data:
            return False

        import datetime
        short_name = ' '.join(memo_data.split()[0:3])
        current_time = datetime.datetime.now().strftime('%d%m%y')
        file_name = f'''{short_name}_{current_time}.txt'''.replace(' ', '_')
        memo_data = w2n(memo_data, otherwords=True)

        if self.create_file(file_name, memo_data):
            talk('Мемо-файл создан!')

    def edit_file(self, file: str) -> None:
        ss.answer_ok_and_pass()
        run(f'kate {self.note_dir}/{file} &', shell=True)

    def delete_file(self, file: str, permission=False) -> str:
        if permission:
            os.remove(f'{self.note_dir}/{file}')
            talk(random.choice(dg.done))
        else:
            talk(f'Действительно удалить файл?')
            print(f'"{file}"')
            return 'not permission'
