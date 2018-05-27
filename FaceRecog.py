from PIL import Image
from Config import Config
import face_recognition
import os
import numpy
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class FaceRecog:
    def __init__(self, db, knn):
        self.db = db
        self.knn = knn
        self.newPhotoCount = 0

    def getPhoto(self, bot, fileId):
        cacheFile = bot.get_file(fileId) # Download file
        cacheFile.download(fileId)
        photo = face_recognition.load_image_file(fileId) # Load photo
        os.remove(fileId)
        return photo

    def matchFace(self, targetEncoding):
        '''
        Find whether there is a match in the database
        '''
        faceList = self.db.listFaces()
        while(len(faceList) != 0):
            encodingList = []
            for face in faceList:
                encodingList.append(face['encoding'])
            results = face_recognition.compare_faces(encodingList, targetEncoding)
            if (True in results):
                index = results.index(True)
                return faceList[index]

            lastFace = faceList[-1:][0]
            faceList = self.db.listFaces(lastFace)

        return None

    def sendMsg(self, bot, msg, responses):
        for tResponse in responses:
            bot.send_message(chat_id=msg.chat_id, text=tResponse)

    def msg(self, bot, msg):
        if (len(msg.photo) <= 0):
            self.sendMsg(bot, msg, ['No photo received.'])

        fileId = msg.photo[-1].file_id # Get largest photo
        '''
        First search for exact match
        '''
        face = self.db.findFace({
            'fileId': fileId
        })
        if (face != None):
            # Found exact match with file id
            logger.info('Exact match found: ' + face['fileId'])
            id = 'Id: ' + face['fileId']
            tag = 'Tag: ' + face['text']
            self.sendMsg(bot, msg, ['Found face:', id, tag])
            return

        '''
        Check number of faces & encode
        '''
        photo = self.getPhoto(bot, fileId)
        photoEncoding = face_recognition.face_encodings(photo)
        if (len(photoEncoding) > 1):
            self.sendMsg(bot, msg, ['More than one face found.'])
            return
        elif (len(photoEncoding) < 1):
            self.sendMsg(bot, msg, ['No face found.'])
            return
        photoEncoding = photoEncoding[0] # One face only

        knnResult = self.knnClassify(photoEncoding)
        if (knnResult != None):
            self.sendMsg(bot, msg, knnResult)
            return

        '''
        Find matching face from database
        '''
        self.sendMsg(bot, msg, self.linearSearch(photoEncoding, fileId))

        if (self.newPhotoCount >= Config.KNN_RE_FIT_THRESHOLD):
            self.newPhotoCount = 0
            self.knn.train()

    def knnClassify(self, photoEncoding):
        X = numpy.array(photoEncoding)
        X = X.reshape(1, -1)
        # Check distance to see if worth to try KNN
        closest_distances = self.knn.kneighbors(X, n_neighbors=1)[0][0][0]
        logger.info('KNN distance: ' + str(closest_distances))
        if (closest_distances < Config.KNN_THRESHOLD):
            # Try KNN
            id = self.knn.predict(X)[0][0]
            logger.info('KNN result:' + id)
            face = self.db.findFace({
                'fileId': id
            })
            # Verify KNN result
            result = face_recognition.compare_faces([face['encoding']], photoEncoding)
            if (True in result):
                logger.info('Match found by KNN: ' + face['fileId'])
                id = 'Id: ' + face['fileId']
                tag = 'Tag: ' + face['text']
                return ['Face found:', id, tag]

    def linearSearch(self, photoEncoding, fileId):
        result = self.matchFace(photoEncoding)
        if (result == None):
            # Add new face
            logger.info('Added new face: ' + fileId)
            self.db.addFace({'fileId': fileId,
                             'encoding': photoEncoding,
                             'text': 'default text'})
            self.newPhotoCount = self.newPhotoCount + 1
            return ['Face not found, now added to database.', 'Id: ' + fileId]
        else:
            logger.info('Match found: ' + result['fileId'])
            # Found match in database
            id = 'Id: ' + result['fileId']
            tag = 'Tag: ' + result['text']
            return ['Face found:', id, tag]
