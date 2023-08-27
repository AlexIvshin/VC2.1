from subprocess import run, CompletedProcess
import pathlib
import configparser

config_path = pathlib.Path(__file__).parent.absolute() / "settings.ini"
config = configparser.ConfigParser()
config.read(config_path)


class Voice:

    @classmethod
    def mic_sensitivity(cls, value: int) -> CompletedProcess[bytes]:
        return run(f'amixer -D pulse sset Capture {value}% >/dev/null', shell=True)

    def speaks(self, words, print_str='',
               speech_pitch: int = config['Speech']['speech_pitch'],
               speech_rate: int = config['Speech']['speech_rate'],
               voice_profile: str = config['Speech']['voice_profile'],
               quality: str = config['Speech']['quality'],
               mic_up: int = config['Mic']['mic_up']) -> None:

        def voice(text) -> None:
            if not text:
                return
            if print_str:
                print(f'{print_str}')

            print(f'► {words.lstrip().replace("́", "")}')
            self.mic_sensitivity(0)
            run(f'echo {text} | RHVoice-test -q {quality} -r {speech_rate} '
                f'-t {speech_pitch} -p {voice_profile}',
                shell=True)
            self.mic_sensitivity(mic_up)

        return voice(words)
