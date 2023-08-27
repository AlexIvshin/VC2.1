# -*- coding: utf-8 -*-

###############################################################
#  russian-speaking voice assistant for Debian kernel systems #
###############################################################

import argparse
import sys
import time
import json as js
import queue

import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

# Модули приложения
import support_skills as ss
from actionslib import yesno_action, callfunc
from dialog import on_off_dict, yes_no_dict, actions_dict
from skills import Translators, ProgramManager
from model_voice import Voice

mode = 'default'


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


class Listener:

    @staticmethod
    def audio_stream_capture():
        SetLogLevel(-1)
        q = queue.Queue()

        def callback(indata, _frames, _time, status) -> None:
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        def get_output(function) -> None:
            if len(text) <= 1:
                return
            print('◄ ' + text.capitalize())
            start = time.time()
            function()
            end = str(round(time.time() - start, 4))
            print(f'-infolabele-runtime{end}s', end='')

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "-l", "--list-devices",
            action="store_true",
            help="show list of audio devices and exit"
        )

        args, remaining = parser.parse_known_args()
        if args.list_devices:
            print(sd.query_devices())
            parser.exit()

        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[parser]
        )
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
            callback=callback
        ):

            model = Model(f'vosk-model-small-ru-0.22')
            rec = KaldiRecognizer(model, args.samplerate)

            talk = Voice().speaks
            talk('Я в деле!')

            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    text = js.loads(rec.Result())['text']
                    get_output(Reactor(text).get_foo_name)


class Reactor:

    def __init__(self, command):
        self.cmd = command

    def check_mode(self) -> str:
        from notebook import notebook_reacts
        global mode
        mode = ss.choice_mode(self.cmd, var_mode=mode)  # Переопределение режима

        if mode == ss.translator_mode:
            Translators(self.cmd).get_result()
        if mode == ss.reverse_mode:
            Translators(self.cmd, reverse=True).get_result()
        if mode == ss.notebook_mode:
            notebook_reacts(self.cmd)

        print(f'Mode: {mode.capitalize()}', end='')
        return mode

    def get_foo_name(self) -> None:

        if self.check_mode() == 'sleep':
            return

        on_off = ss.check_yesno_onoff(self.cmd, dictionary=on_off_dict)  # Определение вкл/выкл
        yes_no = ss.check_yesno_onoff(self.cmd, dictionary=yes_no_dict)  # Определение да/нет
        program = ss.check_prg(self.cmd)  # Определение имени программы, если таковая есть в команде
        action = ss.choice_action(self.cmd, actions_dict)

        if program and on_off:
            ProgramManager(program, on_off).start_stop_program()
        if yes_no:  # обработка моих ответов (да или нет) на вопрос модели
            yesno_action(yes_no)
        if action:  # выбор реакций модели на команды
            callfunc(self.cmd, action, onoff=on_off)
