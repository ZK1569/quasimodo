import cv2
import numpy as np
from src.services.vision import VisionService
from src.repositories.face import FaceRepository, get_face_repository

def loading_images(path):
    img = cv2.imread(path)
    if img is None:
        print(f"Failed to load image from {path}.")
        return None
    else:
        print(f"Image loaded successfully from {path}.")
        return img
    
def add_embedding_db(embeddings, face_repo):
    binary_embedding = np.array(embeddings, dtype=np.float32).tobytes()
    firstname = "Elise"
    lastname = "Albrecht"

    insertion = face_repo.insert_face(firstname, lastname, binary_embedding)

    if insertion:
        print("Image added to the database successfully.")
        return True
    else:
        print("Failed to add image to the database.")
        return False

def main(process_or_store, path):
    img = loading_images(path)
    face_repo_gen = get_face_repository()
    face_repo = next(face_repo_gen)
    service = VisionService(face_repo)


    if process_or_store == "process":
        service.process_image(img)
    elif process_or_store == "store":
        embeddings = service.get_image_embedding(img)
        if len(embeddings) == 0:
            print("No embeddings to add to the database.")
            return False
        elif len(embeddings) > 1:
            print("Multiple faces detected, not proper for datatbase insertion.")
            return False
        else:
            add_embedding_db(embeddings[0], face_repo)


if __name__ == "__main__":
    #main("process", "./asset/04984.png")
    main("store", "./asset/webcam.jpg")