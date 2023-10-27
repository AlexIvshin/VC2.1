import os
import cv2
from PIL import Image
import pickle

# To install the package face_recognition for Debian kernel systems:
# step 1. sudo apt-get install libboost-all-dev libgtk-3-dev build-essential cmake
# step 2. pip install face_recognition
import face_recognition as fr

from typing import Any


def extracting_faces(path_to_files: str) -> None:
    files = os.listdir(path_to_files)

    for file in files:
        if 'extract' not in file and '.jpg' in file:
            img = fr.load_image_file(f'{path_to_files}/{file}')
            faces_loc = fr.face_locations(img)
            cnt = 0

            for face_loc in faces_loc:
                top, right, bottom, left = face_loc
                pil_img = Image.fromarray(img[top:bottom, left:right])

                pref = f'{cnt}_' if len(faces_loc) > 1 else ''
                suf = 'new_extract_' if os.path.isfile(f'{path_to_files}/{pref}extract_{file}') else 'extract_'
                pil_img.save(f'{path_to_files}/{pref}{suf}{file}')
                print(f'Saving "{pref}{suf}{file}" to "{path_to_files}"')
                cnt += 1


def encoding_face(path_to_files: str) -> None:
    files = os.listdir(path_to_files)

    for file in files:
        if 'extract' in file and '.pkl' not in file:
            name = file.replace('jpg', 'pkl').replace('extract', 'encoding')
            valid_face = fr.load_image_file(f'{path_to_files}/{file}')
            face_encoding = fr.face_encodings(valid_face)

            with open(f'{path_to_files}/{name}', 'wb') as f:
                f.write(pickle.dumps(face_encoding))
            print(f'Saving "encoding_{name}" to "{path_to_files}"')


def take_screenshot(source: Any, path: str) -> None:
    path_to_dir = path
    os.mkdir(path_to_dir) if not os.path.exists(path_to_dir) else None

    cap = cv2.VideoCapture(source)
    file_name = path_to_dir.split('/')[-1]
    cnt = 0

    while True:
        ret, img = cap.read()
        if not ret:
            print('Error: Failed to get image!')
            break

        cv2.imshow('Result', img)
        k = cv2.waitKey(1)

        if k == ord(' '):
            cv2.imwrite(f'{path_to_dir}/{file_name}_{cnt}.jpg', img)
            print(f'Saving "{file_name}_{cnt}.jpg" to "{path_to_dir}"')
            cnt += 1
        elif k == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    # take_screenshot(0, 'img/aleksei')
    # extracting_faces('img/aleksei')
    encoding_face('img/aleksei')


if __name__ == '__main__':
    main()
