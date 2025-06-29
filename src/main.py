from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import now
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from src import models, schemas
from src.auth import auth_or_api_key
from src.database import SessionLocal

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

# CORS 설정 (프론트에서 요청 가능하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/emotion/{emotion}", response_class=HTMLResponse)
def get_emotion_page(request: Request, emotion: str, db: Session = Depends(get_db)):
    data = (
        db.query(models.MusicEntry).filter(models.MusicEntry.emotion == emotion).first()
    )
    if not data:
        return HTMLResponse("<h2>해당 감정의 음악이 없습니다.</h2>", status_code=404)

    return templates.TemplateResponse(
        "emotion.html", {"request": request, "emotion": emotion, "data": data}
    )


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.post(
    "/music/", response_model=schemas.Music, dependencies=[Depends(auth_or_api_key)]
)
def create_music(music: schemas.MusicCreate, db: Session = Depends(get_db)):
    db_music = models.MusicEntry(**music.model_dump())
    db.add(db_music)
    db.commit()
    db.refresh(db_music)
    return db_music


@app.get(
    "/music/{music_id}",
    response_model=schemas.Music,
    dependencies=[Depends(auth_or_api_key)],
)
def read_music(music_id: int, db: Session = Depends(get_db)):
    music = db.query(models.MusicEntry).filter(models.MusicEntry.id == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail="Music entry not found")
    return music


@app.get("/emotions")
def list_emotions():
    emotions = ["기쁨", "슬픔", "집중", "불안", "혼란"]
    return emotions


@app.get(
    "/submit", response_class=HTMLResponse, dependencies=[Depends(auth_or_api_key)]
)
def submit(request: Request):
    return templates.TemplateResponse("submit.html", {"request": request})


@app.get(
    "/music_list", response_class=HTMLResponse, dependencies=[Depends(auth_or_api_key)]
)
def get_music_list(request: Request, db: Session = Depends(get_db)):
    music_list = db.query(models.MusicEntry).order_by(models.MusicEntry.id.asc()).all()
    return templates.TemplateResponse(
        "music_list.html", {"request": request, "music_list": music_list}
    )


@app.get(
    "/edit/{music_id}",
    response_class=HTMLResponse,
    dependencies=[Depends(auth_or_api_key)],
)
def edit_music_form(music_id: int, request: Request, db: Session = Depends(get_db)):
    music = db.query(models.MusicEntry).filter(models.MusicEntry.id == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail="Not found")
    return templates.TemplateResponse(
        "edit_music.html", {"request": request, "music": music}
    )


@app.post("/edit/{music_id}", dependencies=[Depends(auth_or_api_key)])
def update_music(
    music_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    music = db.query(models.MusicEntry).filter(models.MusicEntry.id == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail="Music entry not found")

    music.title = payload["title"]
    music.emotion = payload["emotion"]
    music.youtube_url = payload["youtube_url"]
    music.description = payload["description"]
    music.commentary = payload["commentary"]
    music.modified_at = now()
    db.commit()
    return {"success": True}


@app.post("/delete/{music_id}", dependencies=[Depends(auth_or_api_key)])
def delete_music(music_id: int, db: Session = Depends(get_db)):
    music = db.query(models.MusicEntry).filter(models.MusicEntry.id == music_id).first()
    if not music:
        raise HTTPException(status_code=404, detail="Music entry not found")
    db.delete(music)
    db.commit()
    return RedirectResponse(url="/music_list", status_code=303)
