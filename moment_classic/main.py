from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

# CORS 설정 (프론트에서 요청 가능하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 감정별 음악 콘텐츠
EMOTION_DB: Dict[str, Dict] = {
    "슬픔": {
        "title": "Gounod - Ave Maria",
        "youtube": "https://www.youtube.com/embed/2bosouX_d8Y",
        "description": "고뇌 속에서 위로를 주는 음악",
        "commentary": "오늘의 한마디: '눈물이 날 땐 음악이 가장 먼저 안아줍니다.'",
    },
    "불안": {
        "title": "Bach - Cello Suite No.1 Prelude",
        "youtube": "https://www.youtube.com/embed/mGQLXRTl3Z0",
        "description": "혼란한 마음을 정리하는 구조적인 멜로디",
        "commentary": "오늘의 한마디: '불안할 땐 바흐처럼 질서 있게 나아가요.'",
    },
    "기쁨": {
        "title": "Mozart - Eine kleine Nachtmusik",
        "youtube": "https://www.youtube.com/embed/o1FSN8_pp_o",
        "description": "경쾌하고 생기 넘치는 소나타",
        "commentary": "오늘의 한마디: '기쁨은 나눌수록 커집니다. 함께 들어요.'",
    },
    "집중": {
        "title": "Debussy - Clair de Lune",
        "youtube": "https://www.youtube.com/embed/CvFH_6DNRCY",
        "description": "은은한 긴장감이 흐르는 달빛의 서정",
        "commentary": "오늘의 한마디: '소리는 흐르지만 정신은 멈춰있을 거예요.'",
    },
    "혼란": {
        "title": "Beethoven - Moonlight Sonata",
        "youtube": "https://www.youtube.com/embed/4Tr0otuiQuU",
        "description": "깊고 어두운 감정 속에서 균형을 찾는 과정",
        "commentary": "오늘의 한마디: '혼란도 결국 지나가는 파도에요.'",
    },
}


@app.get("/emotion/{emotion}", response_class=HTMLResponse)
def get_emotion_page(emotion: str):
    data = EMOTION_DB.get(emotion)
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
            <h2 class=\"text-xl font-semibold mb-2\">🎼 {data['title']}</h2>
            <div class=\"aspect-w-16 aspect-h-9 mb-4\">
                <iframe class=\"w-full h-64 rounded\" src="{data['youtube']}" 
                    title="moment classic player" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    referrerpolicy="strict-origin-when-cross-origin" 
                    allowfullscreen>
                </iframe>
            </div>
            <p class=\"text-gray-700 mb-2\">{data['description']}</p>
            <p class=\"italic text-sm text-gray-600\">{data['commentary']}</p>
        </div>
    </body>
    </html>
    """


@app.get("/")
def root():
    return {"message": "감정 기반 클래식 힐링 서비스 - /emotion/기쁨 처럼 요청하세요."}
