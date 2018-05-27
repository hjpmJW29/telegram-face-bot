#!/usr/bin/env python3.6
from Database import Database
from FaceRecog import FaceRecog
from Telegram import Telegram
from KNN import KNN

def main():
    db = Database()
    knn = KNN(db)
    fr = FaceRecog(db, knn)
    tg = Telegram(fr, db)
    tg.start()

if __name__ == '__main__':
    main()
