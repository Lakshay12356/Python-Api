from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Tea(BaseModel):
    id: int
    name: str
    price: float

teas: List[Tea] = []

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/teas")
def get_teas():
    return teas

@app.post("/teas")
def add_tea(tea: Tea):
    teas.append(tea)
    return teas

@app.put("/teas/{tea_id}")
def update_tea(tea_id: int, tea: Tea):
    for index, t in enumerate(teas):
        if t.id == tea_id:
            teas[index] = tea
            return teas
    return {"error": "Tea not found"}

@app.delete("/teas/{tea_id}")
def delete_tea(tea_id: int):
    for index, t in enumerate(teas):
        if t.id == tea_id:
            teas.pop(index)
            return teas
    return {"error": "Tea not found"}