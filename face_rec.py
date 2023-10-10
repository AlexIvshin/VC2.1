import os
import cv2
import face_recognition as fr
from typing import Any
from subprocess import run
from pickle import load
from start_app import startapp

from dotenv import load_dotenv
load_dotenv()


def hello_boss(check: bool, name: str) -> bool:
    if check:
        text = 'Здравствуйте хозяин!' if name == 'alex' else "Хозяин! У вас гости!"
    else:
        text = 'Я вас не знаю!'
    run(f'echo {text} | RHVoice-test -q max -r 110 -t 105 -p Anna', shell=True)
    return True if check else False


def adapt_the_image(source: Any, image) -> tuple:

    if isinstance(source, int) or '.mp4' in source:
        img_show = cv2.flip(image, 1) if isinstance(source, int) else image

        if img_show.shape[1] > 800:
            img_show = cv2.resize(img_show, (0, 0), fx=0.5, fy=0.5)

        adapted_img = cv2.cvtColor(img_show, cv2.COLOR_BGR2RGB)
        return img_show, adapted_img, 1

    return image, None, 5000


def face_control(source: Any, puths_to_valid_faces: list) -> bool:
    cap = cv2.VideoCapture(source)
    main_name: str = ''
    cnt: int = 0
    validation_face: bool = False

    valid_faces_encodings: list = []
    valid_names: list = []
    for puth_to_valid_face in puths_to_valid_faces:
        valid_faces_encodings.append(load(open(puth_to_valid_face, 'rb'))[0])
        valid_names.append(puth_to_valid_face.split('/')[-2])

    while True:

        success, img_show = cap.read()
        if not success:
            break

        img_show, img, waitkey = adapt_the_image(source, img_show)

        faces_loc = fr.face_locations(img, model="hog")
        face_encodings = fr.face_encodings(img, faces_loc)

        face_names: list = []
        rectangle_colors: list = []

        for face_encoding in face_encodings:
            for (valid_face_encoding, name) in zip(valid_faces_encodings, valid_names):
                face_name = '???'
                rectangle_color = (255, 255, 255)

                if fr.compare_faces([valid_face_encoding], face_encoding)[0]:
                    if name == 'alex':
                        main_name = name
                    face_name = name.capitalize()
                    rectangle_color = (0, 255, 0)
                    validation_face = True

                face_names.append(face_name)
                rectangle_colors.append(rectangle_color)

        for (top, right, bottom, left), name, color in zip(faces_loc, face_names, rectangle_colors):
            top -= 10
            bottom += 10

            cv2.rectangle(img_show, (left, top), (right, bottom), color, 1)
            cv2.rectangle(img_show, (left + 17, top - 13), (left + 23, top - 19), color, cv2.FILLED)
            cv2.line(img_show, (left + 20, top), (left + 20, top - 19), color, 1)

            cv2.line(img_show, (left - 5, top + ((bottom - top) // 2)),
                     (left + 5, top + ((bottom - top) // 2)), color, 1)
            cv2.line(img_show, (right - 5, top + ((bottom - top) // 2)),
                     (right + 5, top + ((bottom - top) // 2)), color, 1)
            cv2.line(img_show, (left + ((right - left) // 2), top - 5),
                     (left + ((right - left) // 2), top + 5), color, 1)
            cv2.line(img_show, (left + ((right - left) // 2), bottom - 5),
                     (left + ((right - left) // 2), bottom + 5), color, 1)

            cv2.putText(img_show, name, (left + 26, top - 11), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

        cv2.imshow('Result', img_show)
        cnt += 1

        if cv2.waitKey(waitkey) & 0xFF == ord('q') or cnt == 30:
            break

    cap.release()
    cv2.destroyAllWindows()

    return hello_boss(validation_face, main_name)


def main():
    valid_faces: list = [
        f'{os.getenv("VALID_FACE")}',
        f'{os.getenv("FRIENDLY_FACE_1")}'
    ]
    # startapp() if face_control(0, valid_faces) else None
    face_control(0, valid_faces)


if __name__ == '__main__':
    main()
