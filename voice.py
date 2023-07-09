import configparser
from subprocess import run
import time

config = configparser.ConfigParser()
config.read("settings.ini")


def mic_sensitivity(value: int):
    run(f'amixer -D pulse sset Capture {value}% >/dev/null', shell=True)


def talk(words,
         speech_pitch: int = config['Speech']['speech_pitch'],
         speech_rate: int = config['Speech']['speech_rate'],
         voice_profile: str = config['Speech']['voice_profile'].replace('\'', ''),
         quality: str = config['Speech']['quality'].replace('\'', ''),
         mic_down: int = config['Mic']['mic_down'],
         mic_up: int = config['Mic']['mic_up'],
         otherwords=''):

    print('► ' + words.lstrip(), otherwords)
    mic_sensitivity(mic_down)

    if otherwords:
        run(f'echo {words}{otherwords} | RHVoice-test -q {quality} -r {speech_rate} '
            f'-t {speech_pitch} -p {voice_profile} 2>/dev/null', shell=True)
    else:
        run(f'echo {words} | RHVoice-test -q {quality} -r {speech_rate} '
            f'-t {speech_pitch} -p {voice_profile} 2>/dev/null',
            shell=True)

    time.sleep(0.05)
    mic_sensitivity(mic_up)
