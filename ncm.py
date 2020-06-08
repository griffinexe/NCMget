import requests
import json
from playsound import playsound
import time
import os
from mutagen.id3 import ID3,APIC,TIT2,TPE1,TALB



searchURL = 'http://music.163.com/api/search/pc'



headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/35.0.1916.138 Safari/537.36'}



# body = '?s=echo&offset=0&limit=20&type=1'

# ======================================================================================
# content search, return search results OR error info
def search(objName,objType,limit):
    try:
        searchBody = f"?s={objName}&offset=0&limit={limit}&type={objType}"
        searchResult = requests.post(searchURL + searchBody,headers=headers)
        searchResultObj = json.loads(searchResult.text)
        return searchResultObj
    except:
        return 'Search ERROR'

# type details:
# +-------+------------+
# |Songs  |      1     | 
# |Album  |      10    | 
# |Artist |      100   | 
# |Lists  |      1000  | 
# |Users  |      1002  | 
# |mv     |      1004  | 
# +-------+------------+

# get music metadata for display or write to mp3
def getMetadata(dataObj,songID):
    try:
        for i in dataObj['result']['songs']:
            if i['id'] == songID:
                metadata = {'title':i['name'],'artist':i['artists'][0]['name'],'album':i['album']['name'],'id':i['id']}
        return metadata
    except:
        return 'Search ERROR'

# get album art for display or savefile
def getAlbumArt(dataObj,songID):
    try:
        for i in dataObj['result']['songs']:
            if i['id'] == songID:
                albumArt = requests.get(i['album']['picUrl'],headers=headers)
                return albumArt.content
    except:
        return 'GetAlbumArt ERROR'
                    


# save search content to a JSON file
def save_search(result):
    with open('savedResult.json',mode='w',encoding='utf-8') as savefile:
        json.dump(result,savefile)
    savefile.close()
    return 'Save OK'

    
def load_search():
    with open('savedResult.json',mode='r',encoding='utf-8') as savefile:
        res = json.load(savefile)
    savefile.close()
    return res



# get mp3 binary for save or play
def getMp3(musicId):
    try:
        contentUrl = f"http://music.163.com/song/media/outer/url?id={musicId}.mp3"
        mp3 = requests.get(contentUrl,headers=headers)
        return mp3.content
    except:
        return 'GET_Mp3 ERROR'
# NEVER print mp3File.text,terminal broken,,,

# cache as mp3 files
def saveMp3(mp3Bin):
    try:
        mp3File = open('cache.mp3','bw+')
        mp3File.write(mp3Bin)
        mp3File.close()
        return 'Save OK'
    except:
        return 'Save ERROR'

def saveMetadata(file,metadata,albumArt):
    songFile = ID3(file)
    songFile['APIC'] = APIC(encoding=3,mime='image/jpeg',type=3,desc=u'Cover',data=albumArt)
    songFile['TIT2'] = TIT2(encoding=3,text=metadata['title'])
    songFile['TPE1'] = TPE1(encoding=3,text=metadata['artist'])
    songFile['TALB'] = TALB(encoding=3,text=metadata['album'])
    songFile.save()



# save mp3 file with proper filename and full metadata, even lyric
def saveMp3Full(mp3Bin,albumArt,metadata):
    if os.path.exists('./Downloads/') == False:
        os.mkdir('./Downloads/')
    filename = f"{metadata['title']}-{metadata['album']}-{metadata['artist']}.mp3".replace('/','&')
    filename.replace('\\','&')
    mp3File = open('./Downloads/' + filename,'bw+')
    mp3File.write(mp3Bin)
    mp3File.close()
    saveMetadata('./Downloads/' + filename,metadata,albumArt)
    saveLrc(getLyric(metadata['id']),f"./Downloads/{metadata['title']}-{metadata['album']}-{metadata['artist']}.lrc")



# get music lyric
def getLyric(musicId):
    try:
        lrcUrl = f"http://music.163.com/api/song/media?id={musicId}"
        lrcJson = requests.get(lrcUrl,headers=headers)
        lyric = json.loads(lrcJson.text)
        return lyric['lyric']
    except:
        return 'Lyric ERROR or No Lyric'

# save lrc files
def saveLrc(Lrcjson,filename):
    try:
        lrcFile = open(filename,'w',encoding='utf-8')
        lrcFile.write(Lrcjson)
        lrcFile.close()
        return 'LrcSave OK'
    except:
        return 'LrcSave ERROR'

# play music 
def playmusic():
    playsound('cache.mp3',block=False)

# display preparation
def display(metadata,albumPic):
    labelName = f"{metadata['title']}-{metadata['artist']}-{metadata['album']}"
    albumArt = albumPic
    lrc = open(f"{metadata['title']}-{metadata['album']}-{metadata['artist']}.lrc",'r')
    lrcText = lrc.read()
    lrc.close()
    return labelName,albumArt,lrcText

