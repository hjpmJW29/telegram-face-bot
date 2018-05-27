import json

class Config:
    def __init__(self):
        pass

Config.DB_NAME = 'test-database2' # Database name
Config.DB_URL = 'mongodb://localhost:27017/' # Your mongodb url
Config.FIND_LIMIT = 10
Config.MODEL_PATH = 'knn.clf' # KNN model saved name
Config.TG_TOKEN = "Your telegram bot token" # Telegram Bot Token

Config.KNN_RE_FIT_THRESHOLD = 2
Config.KNN_THRESHOLD = 0.6
Config.INIT_FACE = []
for i in range(0, 128):
    Config.INIT_FACE.append(0)
Config.INIT_FACE = json.dumps(Config.INIT_FACE)
Config.INIT_FILEID = 0
