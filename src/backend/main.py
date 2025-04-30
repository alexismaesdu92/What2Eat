from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware 
import shutil 
import os 

from backend.food_getter import IngredientExtractor


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:5173'],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
UPLOADED_DIR = 'temp/uploads'
os.makedirs(UPLOADED_DIR, exist_ok=True)


@app.post("/upload")
async def upload_file(image: UploadFile = File(...)):
    if image.content_type != "image/png":
        return {"error": "Seuls les fichiers PNG sont autorisés"}
    file_location = os.path.join(UPLOADED_DIR, image.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    print("Image reçue avec succès")
    extractor = IngredientExtractor()
    ingredients_text = extractor.get_ingredients(file_location)
    print(ingredients_text)
    return {"message": "Image reçue avec succès", 
            "filename": image.filename,
            "ingredients": ingredients_text}