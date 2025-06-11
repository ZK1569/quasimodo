import cv2
import numpy as np
import os

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from src.services.vision import get_vision_service
from src.services.service import VisionServiceAbs
from src.models.face import Face

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/face/new")
async def new_face(
    file: UploadFile = File(...),
    vision_service: VisionServiceAbs = Depends(get_vision_service),
):
    content = await file.read()
    img_array = np.frombuffer(content, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Image non valide")

    filename = os.path.splitext(file.filename)[0]
    try:
        firstname, lastname = filename.split("_", maxsplit=1)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être nommé : Prenom_Nom.<ext>",
        )

    embeddings = vision_service.get_image_embedding(img)

    if len(embeddings) == 0:
        return {"status": "error", "detail": "Aucun visage détecté"}
    if len(embeddings) > 1:
        return {"status": "error", "detail": "Plusieurs visages détectés"}

    if add_embedding_db(embeddings[0], vision_service.face_repository, firstname, lastname):
        return {"status": "ok"}

    return {"status": "error", "detail": "Échec d’insertion dans la base"}


@router.post("/face")
async def detect_face(
    file: UploadFile = File(...),
    vision_service: VisionServiceAbs = Depends(get_vision_service),
):
    content: bytes = await file.read()
    img_array = np.frombuffer(content, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Image non valide")

    try:
        face = vision_service.process_image(img)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Erreur de traitement") from exc

    if face is None :
        return {"status": "error", "detail": "Aucun visage reconnu"}
    elif face == -1:
        return {"status": "error", "detail": "Aucun visage correspondant trouvé dans la base de données"}

    return {
        "status": "ok",
        "data": {
            "firstname": face.firstname,
            "name": face.name,
            "face_id": face.face_id,
            "similarity": float(face.similarity),
        },
    }


def loading_images(path):
    img = cv2.imread("./asset/webcam2.jpg")
    if img is None:
        print(f"Failed to load image from {path}.")
        return None
    else:
        print(f"Image loaded successfully from {path}.")
        return img


def add_embedding_db(embedding, face_repo, firstname: str, lastname: str) -> bool:
    binary_embedding = np.array(embedding, dtype=np.float32).tobytes()
    return face_repo.insert_face(firstname, lastname, binary_embedding)
