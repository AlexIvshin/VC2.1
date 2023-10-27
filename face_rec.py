#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2

# To install the package face_recognition for Debian kernel systems:
# step 1. sudo apt-get install libboost-all-dev libgtk-3-dev build-essential cmake
# step 2. pip install face_recognition
import face_recognition as fr

from typing import Any
from pickle import load
from model_voice import Voice
from start_app import startapp

from dotenv import load_dotenv
load_dotenv()
valid_faces: list = [
    os.getenv("VALID_FACE"),
    os.getenv("FRIENDLY_FACE_1")
]
valid_name = os.getenv("VALID_NAME")


def to_greet(check: bool, name: bool) -> bool:
    talk = Voice().speaks
    text = 'Здравствуйте хозяин!' if name else "Хозяин! У вас гости!" if check else 'Я вас не знаю!'
    talk(text)
    return True if check else False


def adapt_the_image(source: Any, image) -> tuple:
    img_show = image
    adapted_img = None
    weit_key = 0

    if isinstance(source, int) or '.mp4' in source:
        img_show = cv2.flip(image, 1) if isinstance(source, int) else image
        img_show = cv2.resize(img_show, (0, 0), fx=0.5, fy=0.5) if img_show.shape[1] > 800 else img_show
        adapted_img = cv2.cvtColor(img_show, cv2.COLOR_BGR2RGB)
        weit_key = 1

    return img_show, adapted_img, weit_key


def shaping_the_face_frame(image, face_name: str, coordinates: tuple, color: tuple, thickness: int) -> None:
    tp, rt, bm, lt = coordinates
    tp -= 10
    bm += 10

    cv2.rectangle(image, (lt, tp), (rt, bm), color, thickness)
    cv2.rectangle(image, (lt + 17, tp - 13), (lt + 23, tp - 19), color, cv2.FILLED)
    cv2.line(image, (lt + 20, tp), (lt + 20, tp - 19), color, thickness)
    cv2.line(image, (lt - 5, tp + ((bm - tp) // 2)), (lt + 5, tp + ((bm - tp) // 2)), color, thickness)
    cv2.line(image, (rt - 5, tp + ((bm - tp) // 2)), (rt + 5, tp + ((bm - tp) // 2)), color, thickness)
    cv2.line(image, (lt + ((rt - lt) // 2), tp - 5), (lt + ((rt - lt) // 2), tp + 5), color, thickness)
    cv2.line(image, (lt + ((rt - lt) // 2), bm - 5), (lt + ((rt - lt) // 2), bm + 5), color, thickness)
    cv2.putText(image, face_name, (lt + 26, tp - 11), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness)


def face_control(source: Any, puths_to_valid_faces: list) -> bool:
    cap = cv2.VideoCapture(source)
    validation_face: bool = False
    check_main_name: bool = False
    valid_faces_encodings: list = []
    valid_names: list = []
    cnt: int = 0

    for puth_to_valid_face in puths_to_valid_faces:
        valid_faces_encodings.append(load(open(puth_to_valid_face, 'rb'))[0])
        valid_names.append(puth_to_valid_face.split('/')[-2])

    while True:
        ret, img_show = cap.read()
        if not ret:
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
                    check_main_name = True if name == valid_name else False
                    face_name = name.capitalize()
                    rectangle_color = (0, 255, 0)
                    validation_face = True

                face_names.append(face_name)
                rectangle_colors.append(rectangle_color)

        for (top, right, bottom, left), name, color in zip(faces_loc, face_names, rectangle_colors):
            shaping_the_face_frame(img_show, name, (top, right, bottom, left), color, 1)

        cv2.imshow('Result', img_show)
        cnt += 1

        if cv2.waitKey(waitkey) & 0xFF == ord('q') or cnt == 20:
            break

    cap.release()
    cv2.destroyAllWindows()

    return to_greet(validation_face, check_main_name)


def main():
    if face_control(0, valid_faces):
        startapp()
    # face_control(0, valid_faces)


if __name__ == '__main__':
    main()
