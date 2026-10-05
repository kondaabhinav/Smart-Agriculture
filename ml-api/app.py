from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image

import joblib
import numpy as np
import pandas as pd
import io
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Load disease detection model
# ---------------------------
disease_model = load_model("disease_model.h5")
class_names = sorted(os.listdir("paddy-disease-classification/train_images"))

# ---------------------------
# Load crop yield model
# ---------------------------
yield_model = joblib.load("yield_model.pkl")

yield_features = [
    "Area",
    "Item",
    "Year",
    "average_rain_fall_mm_per_year",
    "pesticides_tonnes",
    "avg_temp",
    "temp_rain",
    "rain_log",
    "temp_sq"
]

# ---------------------------
# Request model for yield API
# ---------------------------
class YieldRequest(BaseModel):
    Area: str
    Item: str
    Year:int
    soil_type: str
    average_rain_fall_mm_per_year: float
    pesticides_tonnes: float
    avg_temp: float

# ---------------------------
# Home route
# ---------------------------
@app.get("/")
def home():
    return {"message": "Disease + Yield Prediction API is running"}

# ---------------------------
# Disease prediction API
# ---------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()

    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img = img.resize((224, 224))

    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    pred = disease_model.predict(img_array)
    predicted_class = class_names[np.argmax(pred)]
    confidence = float(np.max(pred))

    return {
        "disease": predicted_class,
        "confidence": confidence
    }

# ---------------------------
# Yield prediction helper
# ---------------------------
def predict_yield_api(data):
    

    soil_map = {
        "Loamy": 1,
        "Clay": 2,
        "Sandy": 3,
        "Black": 4,
        "Red": 5
    }

    data["soil_type"] = soil_map.get(data.get("soil_type"), 0)
    data["pesticides_tonnes"]=data["pesticides_tonnes"]/1000

    df = pd.DataFrame([data])

    
    if "soil_type" in df.columns:
        df = df.drop(columns=["soil_type"])

    df["temp_rain"] = df["avg_temp"] * df["average_rain_fall_mm_per_year"]
    df["rain_log"] = np.log1p(df["average_rain_fall_mm_per_year"])
    df["temp_sq"] = df["avg_temp"] ** 2

    df = df[yield_features]

    pred_log = yield_model.predict(df)
    pred = np.expm1(pred_log)

    return float(pred[0])
# ---------------------------
# Yield prediction API
# ---------------------------
@app.post("/predict-yield")
def predict_yield(data: YieldRequest):
    result = predict_yield_api(data.dict())

    kg_per_hectare=result

    kg_per_acre=((kg_per_hectare/2.47)/10) * 2
    return {
        "yield_per_acre": round(kg_per_acre,2)
    }