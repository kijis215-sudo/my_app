import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    # NOTE: キーは .env から読み込む（リポジトリに直書きしない）
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    GOOGLE_GENAI_API_KEY = os.environ.get("GOOGLE_GENAI_API_KEY", "")

    DIRECTIONS_API_KEY = os.environ.get("DIRECTIONS_API_KEY", "")
    MAP_JAVA_API_KEY = os.environ.get("MAP_JAVA_API_KEY", "")

    # 外部APIが遅い/落ちている時に無限待ちしないためのタイムアウト
    GOOGLEMAPS_HTTP_TIMEOUT_SEC = float(os.environ.get("GOOGLEMAPS_HTTP_TIMEOUT_SEC", "5"))
    GEMINI_TIMEOUT_SEC = float(os.environ.get("GEMINI_TIMEOUT_SEC", "6"))
    USE_GEMINI = os.environ.get("USE_GEMINI", "0") == "1"
    