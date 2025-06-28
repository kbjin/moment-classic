from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import now
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from moment_classic import models, schemas
from moment_classic.auth import auth_or_api_key
from moment_classic.database import SessionLocal

app = FastAPI()
templates = Jinja2Templates(directory="moment_classic/templates")

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
def get_emotion_page(emotion: str, db: Session = Depends(get_db)):
    data = (
        db.query(models.MusicEntry).filter(models.MusicEntry.emotion == emotion).first()
    )
    if not data:
        return HTMLResponse("<h2>해당 감정의 음악이 없습니다.</h2>", status_code=404)

    return f"""
    <!DOCTYPE html>
    <html lang=\"ko\">
        <head>
            <meta charset=\"UTF-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
            <title>{emotion}을 위한 음악</title>
            <link href=\"https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css\" rel=\"stylesheet\">
        </head>
        <body class=\"bg-gray-50 text-gray-800 flex flex-col items-center justify-center min-h-screen p-6\">
            <div class=\"max-w-xl w-full bg-white rounded-2xl shadow-lg p-6\">
                <h1 class=\"text-2xl font-bold text-center mb-4\">{emotion}을 위한 클래식</h1>
                <h2 class=\"text-xl font-semibold mb-2\">🎼 {data.title}</h2>
                <div class=\"aspect-w-16 aspect-h-9 mb-4\">
                    <iframe class=\"w-full h-64 rounded\" src="https://www.youtube.com/embed/{data.youtube_url}?autoplay=1" 
                        title="moment classic player" 
                        frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                        referrerpolicy="strict-origin-when-cross-origin" 
                        allowfullscreen>
                    </iframe>
                </div>
                <p class=\"text-gray-700 mb-2\">{data.description}</p>
                <p class=\"italic text-sm text-gray-600\">오늘의 한마디: {data.commentary}</p>
            </div>
        </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def root():
    return f"""
    <!DOCTYPE html>
    <html lang=\"ko\">
        <head>
            <meta charset=\"UTF-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
            <title>모멘트 클래식 - 감정 기반 클래식 힐링 서비스</title>
            <link href=\"https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css\" rel=\"stylesheet\">
        </head>
        <body class=\"bg-gray-50 text-gray-800 flex flex-col items-center justify-center min-h-screen p-6\">
            <div class=\"max-w-xl w-full bg-white rounded-2xl shadow-lg p-6\">
                <h1 class=\"text-2xl font-bold text-center mb-4\">모멘트 클래식</h1>
                <h2 class=\"text-xl font-semibold mb-2\">주소 뒤에 '/emotion/기쁨' 처럼 붙여서 검색하세요.</h2>
            </div>
        </body>
    </html>
    """


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
def show_form():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>음악 등록</title>
        <script>
            async function submitForm(event) {
                event.preventDefault();
                const data = {
                    emotion: document.getElementById("emotion").value,
                    title: document.getElementById("title").value,
                    youtube_url: document.getElementById("youtube_url").value,
                    description: document.getElementById("description").value,
                    commentary: document.getElementById("commentary").value
                };

                const res = await fetch("/music/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                if (res.ok) {
                    const result = await res.json();
                    alert("저장 완료! ID: " + result.id);
                    document.getElementById("form").reset();
                } else {
                    alert("저장 실패!");
                }
            }
        </script>
    </head>
    <body style="font-family: sans-serif; max-width: 600px; margin: 2rem auto;">
        <h2>🎼 클래식 음악 등록</h2>
        <form id="form" onsubmit="submitForm(event)">
            <label>감정<br><input id="emotion" required style="width: 100%;"/></label><br><br>
            <label>제목<br><input id="title" required style="width: 100%;"/></label><br><br>
            <label>YouTube 링크<br><input id="youtube_url" required style="width: 100%;"/></label><br><br>
            <label>설명<br><textarea id="description" rows="3" style="width: 100%;"></textarea></label><br><br>
            <label>오늘의 한마디<br><input id="commentary" style="width: 100%;"/></label><br><br>
            <button type="submit" style="padding: 10px 20px;">저장</button>
        </form>
    </body>
    </html>
    """


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
