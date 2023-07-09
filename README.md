Компиляция синтезатора голоса.  
https://github.com/RHVoice/RHVoice/blob/master/doc/ru/Compiling-on-Linux.md

После установки пакета vosk (pip install vosk):
необходимо скачать архив с русскоязычной моделью "vosk-model-small-ru-0.22".
https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip   
И разархивировать его в корневую папку проекта.

В skills.Translators и skills.Polyhistor используется пакет googletrans версии 3.1.0a0.
Другие версии у меня не заработали, только (pip install googletrans==3.1.0a0).
