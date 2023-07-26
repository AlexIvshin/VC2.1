# -*- coding: utf-8 -*-

###############################################################
#  russian-speaking voice assistant for Debian kernel systems #
###############################################################

import argparse
import configparser
import pathlib
import sys
from subprocess import run
import time
import json as js
import queue

import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel


class ShortTermMemory:
    __limit: int = 2
    __stack: list = []

    def ad_element(self, action: str) -> None:
        if len(self.__stack) >= self.__limit:
            del self.__stack[0]
        self.__stack.append(action)

    def get_stack(self) -> list:
        return self.__stack

    def clear_stack(self) -> None:
        return self.__stack.clear()


stack = ShortTermMemory()


class Assistant:
    config_path = pathlib.Path(__file__).parent.absolute() / "settings.ini"
    config = configparser.ConfigParser()
    config.read(config_path)
    mode = 'default'

    def listening(self) -> None:
        SetLogLevel(-1)
        q = queue.Queue()

        def callback(indata, _frames, _time, status) -> None:
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-l", "--list-devices", action="store_true", help="show list of audio devices and exit")
        args, remaining = parser.parse_known_args()

        if args.list_devices:
            print(sd.query_devices())
            parser.exit()

        parser = argparse.ArgumentParser(
                add_help=False,
                description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                parents=[parser])

        parser.add_argument("-d", "--device", help="input device (numeric ID or substring)")
        parser.add_argument("-r", "--samplerate", type=int, help="sampling rate")
        args = parser.parse_args(remaining)

        if args.samplerate is None:
            device_info = sd.query_devices(args.device, "input")
            args.samplerate = int(device_info["default_samplerate"])

        with sd.RawInputStream(
                samplerate=args.samplerate,
                blocksize=8000,
                device=args.device,
                dtype="int16",
                channels=1,
                callback=callback):

            model = Model(f'vosk-model-small-ru-0.22')
            rec = KaldiRecognizer(model, args.samplerate)

            self.speaks('Я в деле!')
            print('Mode: Default', end='')

            while True:
                data = q.get()

                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    text = js.loads(result)['text']

                    if len(text) > 0:
                        print('◄ ' + text.capitalize())
                        start = time.time()
                        self.reacts(text)
                        end = str(round(time.time() - start, 4))
                        print(f'-infolabele-runtime{end}s', end='')

    @classmethod
    def mic_sensitivity(cls, value: int) -> None:
        run(f'amixer -D pulse sset Capture {value}% >/dev/null', shell=True)

    def speaks(self, words: str, print_str: str = '',
               speech_pitch: int = config['Speech']['speech_pitch'],
               speech_rate: int = config['Speech']['speech_rate'],
               voice_profile: str = config['Speech']['voice_profile'],
               quality: str = config['Speech']['quality'],
               mic_up: int = config['Mic']['mic_up']) -> None:

        def voice(text: str) -> None:
            if print_str:
                print(f'{print_str}')
            print(f'► {words.lstrip().replace("́", "")}')
            self.mic_sensitivity(0)
            run(f'echo {text} | RHVoice-test -q {quality} -r {speech_rate} '
                f'-t {speech_pitch} -p {voice_profile} 2>/dev/null',
                shell=True)
            time.sleep(0.05)
            Assistant.mic_sensitivity(mic_up)
            
        return voice(words)

    def reacts(self, command: str) -> None:
        import utils as tls
        import actionslib as alib
        from dialog import on_off_dict, yes_no_dict, actions_dict
        from skills import Translators, ProgramManager
        from notebook import notebook_reacts

        cmdline = command
        self.mode = tls.choice_mode(cmdline, var_mode=self.mode)  # Переопределение режима

        try:
            if self.mode == tls.notebook_mode:
                notebook_reacts(cmdline)
            elif self.mode == tls.translator_mode:
                Translators(cmdline).get_result()
            elif self.mode == tls.reverse_mode:
                Translators(cmdline, reverse=True).get_result()
            elif self.mode == tls.sleep_mode:
                return

            on_off = tls.check_yesno_onoff(cmdline, dictionary=on_off_dict)  # Определение вкл/выкл
            yes_no = tls.check_yesno_onoff(cmdline, dictionary=yes_no_dict)  # Определение да/нет
            program = tls.check_prg(cmdline)  # Определение имени программы, если таковая есть в команде

            if program and on_off:
                ProgramManager(program, on_off).start_stop_program()

            if yes_no:  # обработка моих ответов (да или нет) на вопрос модели
                alib.yesno_action(yes_no)
            else:  # выбор реакций модели на команды
                action, max_intersection = tls.choice_action(cmdline, actions_dict)
                if action:
                    alib.callfunc(cmdline, action, max_intersection, onoff=on_off)

        except (AttributeError, ValueError):
            pass
