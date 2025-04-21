from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Habilitar CORS
origins = [
    "https://uac-filial-sicuani.netlify.app/",  # Asegúrate de reemplazarlo por el dominio de tu frontend
    "http://127.0.0.1:5500",  # Dirección local de Live Server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir los orígenes especificados
    allow_credentials=True,
    allow_methods=["*"],  # Permitir cualquier método (GET, POST, etc.)
    allow_headers=["*"],  # Permitir cualquier encabezado
)

class Vote(BaseModel):
    item_id: str  # ID único de la carta
    vote: str     # "like" o "dislike"

def init_db():
    conn = sqlite3.connect("votes.db")
    c = conn.cursor()
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL,
            vote TEXT CHECK(vote IN ('like', 'dislike'))
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.post("/vote")
def cast_vote(vote: Vote):
    if vote.vote not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    conn = sqlite3.connect("votes.db")
    c = conn.cursor()
    c.execute("INSERT INTO votes (item_id, vote) VALUES (?, ?)", (vote.item_id, vote.vote))
    conn.commit()
    conn.close()
    return {"message": "Vote recorded"}

@app.get("/rating/{item_id}")
def get_rating(item_id: str):
    conn = sqlite3.connect("votes.db")
    c = conn.cursor()
    c.execute("SELECT vote, COUNT(*) FROM votes WHERE item_id = ? GROUP BY vote", (item_id,))
    results = dict(c.fetchall())
    conn.close()
    return {
        "item_id": item_id,
        "likes": results.get("like", 0),
        "dislikes": results.get("dislike", 0),
        "total": results.get("like", 0) + results.get("dislike", 0)
    }
