from Config import Config
import json
import pymongo

class Database:
    def __init__(self, db = Config.DB_NAME, url = Config.DB_URL):
        self.client = pymongo.MongoClient(url)
        self.db = self.client[db]
        self.faces = self.db['faces']

    def __del__(self):
        self.client.close()

    def listFaces(self, lastFace = None):
        findParam = {}
        if (lastFace != None):
            findParam['_id'] = {
                'gte': lastFace['_id']
            }

        faceData = self.faces.find(findParam,
            sort=[('_id', pymongo.ASCENDING)],
            limit=Config.FIND_LIMIT)

        if (faceData == None):
            return None

        faceList = []
        for face in faceData:
            face['encoding'] = self.stringToEncoding(face['encoding'])
            faceList.append(face)
        return faceList

    def findFace(self, param):
        face = self.faces.find_one(param)
        if (face == None):
            return None
        face['encoding'] = self.stringToEncoding(face['encoding'])
        return face

    def encodingToString(self, encoding):
        return json.dumps(encoding)

    def stringToEncoding(self, s):
        return json.loads(s)

    def addFace(self, face):
        face['encoding'] = self.encodingToString(list(face['encoding']))
        result = self.faces.insert_one(face)
        return result

    def updateFace(self, fileId, text):
        result = self.faces.find_one_and_update({
            'fileId': fileId
        }, {
            '$set': {
                'text': text
            }
        })
        return result
