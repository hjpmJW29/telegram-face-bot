from Config import Config
from sklearn import neighbors
import pickle
import json
import math

class KNN:

    def __init__(self, db):
        self.db = db
        if (not self.loadKNN()):
            self.fist_train()

    def loadKNN(self):
        try:
            with open(model_path, 'rb') as f:
                self.knn_clf = pickle.load(f)
            return True
        except:
            return False

    def fist_train(self, n_neighbors=1, knn_algo='ball_tree'):
        knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
        knn_clf.fit([json.loads(Config.INIT_FACE)], [Config.INIT_FILEID])
        # Save the trained KNN classifier
        with open(Config.MODEL_PATH, 'wb') as f:
            pickle.dump(knn_clf, f)
        self.knn_clf = knn_clf

    def train(self, n_neighbors=None, verbose=False, knn_algo='ball_tree'):
        X = []
        y = []

        # Iterate through all faces in the database
        faceList = self.db.listFaces()
        while(len(faceList) != 0):
            for face in faceList:
                X.append(face['encoding'])
                y.append(face['fileId'])
            lastFace = faceList[-1:][0]
            faceList = self.db.listFaces(lastFace)

        # Determine how many neighbors to use for weighting in the KNN classifier
        if n_neighbors is None:
            n_neighbors = int(round(math.sqrt(len(X))))
            if verbose:
                print("Chose n_neighbors automatically:", n_neighbors)

        # Create and train the KNN classifier
        knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
        knn_clf.fit(X, y)

        # Save the trained KNN classifier
        with open(Config.MODEL_PATH, 'wb') as f:
            pickle.dump(knn_clf, f)

        self.knn_clf = knn_clf

    def predict(self, encoding):
        # Predict classes and remove classifications that aren't within the threshold
        return [self.knn_clf.predict(encoding), self.knn_clf.predict_proba(encoding)]

    def kneighbors(self, X, n_neighbors=1):
        return self.knn_clf.kneighbors(X, n_neighbors)
