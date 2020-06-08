from UI_Lite import Ui_NCMget_main
import ncm
from PyQt5 import QtCore,QtGui,uic,QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import threading
import os
import time

class ncmget(QtWidgets.QMainWindow,Ui_NCMget_main):
    def __init__(self,parent=None):
        super(ncmget,self).__init__(parent)
        self.setupUi(self)
        self.SearchButton.clicked.connect(self.dosearch)
        self.SearchResultList.itemClicked.connect(self.resultSelect)
        self.PlayButton.clicked.connect(self.musicPlay)
        self.DownloadButton.clicked.connect(self.downloadMusic)
        self.SaveSearchButton.clicked.connect(self.saveRes)
        self.LoadSearchButton.clicked.connect(self.loadResult)

    searchResult = None
    currentMusicID = None
    mp3file = None
    albumPic = None
    playTrail = None


    def loadResult(self):
        try:
            global searchResult
            searchResult = ncm.load_search()
            self.SearchResultList.clear()

            for i in searchResult['result']['songs']:
                resultId = i['id']
                resultTitle = i['name']
                resultArtist = i['artists'][0]['name']
                resultAlbum = i['album']['name']
                listUnit = f"{resultId}-{resultTitle}-{resultArtist}-{resultAlbum}"
                self.SearchResultList.addItem(listUnit)
                self.ResultSaveStatus.setText('Load success')

        except:
            self.ResultSaveStatus.setText('Load failed')


    def saveRes(self):
        try:
            ncm.save_search(searchResult)
            self.ResultSaveStatus.setText('Save success')

        except:
            self.ResultSaveStatus.setText('Save failed')



    def downloadMusic(self):
        try:
            ncm.saveMp3Full(ncm.getMp3(currentMusicID),albumPic,ncm.getMetadata(searchResult,currentMusicID))
            self.MusicSaveStatus.setText('Download success!')

        except:
            self.MusicSaveStatus.setText('Media download failed,,,')


    def musicPlay(self):
        try:
            self.MusicSaveStatus.clear()
            # print(currentMusicID)
            global mp3file
            mp3file = ncm.getMp3(currentMusicID)
            ncm.saveMp3(mp3file)
            global playTrail
            playTrail = threading.Thread(target=ncm.playmusic)
            playTrail.start()
            playTrail.join()
            os.remove('cache.mp3')
            self.MusicSaveStatus.setText('Now playing,,,')

            
        except:
            self.MusicSaveStatus.setText('ERROR:Cannot play music\nMay have copyright issues\nor NCM server currentely unavail.')
            self.DownloadButton.setDisabled(True)
 


    def resultSelect(self):
        self.DownloadButton.setEnabled(True)
        resultIndex = self.SearchResultList.currentRow()
        global currentMusicID
        currentMusicID = searchResult['result']['songs'][resultIndex]['id']
        # print(resultIndex)
        # print(searchResult['result']['songs'][resultIndex]['name'])
        self.MediaInfoDisplay.setText(f"title:{searchResult['result']['songs'][resultIndex]['name']}-artist:{searchResult['result']['songs'][resultIndex]['artists'][0]['name']}-album:{searchResult['result']['songs'][resultIndex]['album']['name']}")
        global albumPic
        albumPic = ncm.getAlbumArt(searchResult,searchResult['result']['songs'][resultIndex]['id'])
        QalbumPic = QImage.fromData(albumPic)
        displayImg = QPixmap.fromImage(QalbumPic)
        self.AlbumArtImg.setScaledContents(True)
        self.AlbumArtImg.setPixmap(displayImg)
        # lrcText = ncm.getLyric(searchResult['result']['songs'][resultIndex]['id'])
        lrcText = ncm.getLyric(currentMusicID)
        self.LyricShow.setText(lrcText)

    def dosearch(self):
        try:
            objName = self.SearchName.text()
            objType = 1
            searchLimit = 100
            global searchResult
            searchResult = ncm.search(objName,objType,searchLimit)
            # id-title-artist-album DISPLAY 
            self.SearchResultList.clear()

            for i in searchResult['result']['songs']:
                resultId = i['id']
                resultTitle = i['name']
                resultArtist = i['artists'][0]['name']
                resultAlbum = i['album']['name']
                listUnit = f"{resultId}-{resultTitle}-{resultArtist}-{resultAlbum}"
                self.SearchResultList.addItem(listUnit)
        except:
            print(searchResult)
            self.MusicSaveStatus.setText('Search Failed')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ncmget()
    window.show()
    sys.exit(app.exec_())