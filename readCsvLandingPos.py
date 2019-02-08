import pandas as pd
from pubg_python import PUBG, Shard
import cv2
import numpy as np

class getMatchInfo:
    def __init__(self,telemetry):
        self.lgsp = telemetry.events_from_type('LogGameStatePeriodic')
        self.LogPlayerPosition = telemetry.events_from_type('LogPlayerPosition')
    
    def getSafetyAndPoisonGasPosInfo(self):
        zoneElapsedTime = []
        safetyZonePositionX = []
        safetyZonePositionY = []
        poisonGasPositionX = []
        poisonGasPositionY = []
        safetyZoneRadius = []
        poisonGasRadius = []

        for i in range(len(self.lgsp)):
            zoneElapsedTime.append(self.lgsp[i].game_state.elapsed_time)
            safetyZonePositionX.append(self.lgsp[i].game_state.safetyZonePos.x)
            safetyZonePositionY.append(self.lgsp[i].game_state.safetyZonePos.y)
            poisonGasPositionX.append(self.lgsp[i].game_state.poisonGasWarningPos.x)
            poisonGasPositionY.append(self.lgsp[i].game_state.poisonGasWarningPos.y)
            safetyZoneRadius.append(self.lgsp[i].game_state.safety_zone_radius)
            poisonGasRadius.append(self.lgsp[i].game_state.poison_gas_warning_radius)
        
        return zoneElapsedTime,safetyZonePositionX,safetyZonePositionY,poisonGasPositionX,poisonGasPositionY,safetyZoneRadius,poisonGasRadius

    def getAirPlaneInfo(self,map):
        flagCount = 0
        tempIndex = []
        airLineIndexPosFirst =[]
        airLineIndexPosEnd =[]
        airLineFirstPosIndex = []
        airLineEndPosIndex = []
        
        count = 0
        h,w,c = map.shape

        for i in range(len(self.LogPlayerPosition)):
            if not(self.LogPlayerPosition[i].elapsed_time == 0) and self.LogPlayerPosition[i].character.location.z >= 150088:
                if count == 0:
                    airLineIndexPosFirst.append(self.LogPlayerPosition[i].character.location.x/100)
                    airLineIndexPosFirst.append(self.LogPlayerPosition[i].character.location.y/100)
                count = i

        airLineIndexPosEnd.append(self.LogPlayerPosition[count].character.location.x/100)
        airLineIndexPosEnd.append(self.LogPlayerPosition[count].character.location.y/100)
        a = (airLineIndexPosFirst[1]-airLineIndexPosEnd[1])/(airLineIndexPosFirst[0]-airLineIndexPosEnd[0])
        b = airLineIndexPosFirst[1] - a*airLineIndexPosFirst[0]

        airLineAlpha = a
        airLineBeta = b
        #airLineFirstPositionX0Index = [0,b]
        #airLineEndPositionXHIndex = [h,int(a*h+b)]

        if int(b) >= 0 and int(b) <= h and not(flagCount == 2):
            tempIndex.append(0)
            tempIndex.append(int(int(b)))
            flagCount += 1
        
        if int(-1*(b/a)) >= 0 and int(-1*(b/a)) <= w and not(flagCount == 2):
            tempIndex.append(int(-1*(b/a)))
            tempIndex.append(0)
            flagCount += 1
        
        if int(a*h+b) >= 0 and int(a*h+b) <= h and not(flagCount == 2):
            tempIndex.append(w)
            tempIndex.append(int(a*h+b))
            flagCount += 1
        
        if int((h-b)/a) >= 0 and int((h-b)/a) <= w and not(flagCount == 2):
            tempIndex.append(int((h-b)/a))
            tempIndex.append(h)
            flagCount += 1

        if (abs(tempIndex[0]-airLineIndexPosFirst[0])+abs(tempIndex[1]-airLineIndexPosFirst[1])) < (abs(tempIndex[2]-airLineIndexPosFirst[0])+abs(tempIndex[3]-airLineIndexPosFirst[1])):
            airLineFirstPosIndex.append(tempIndex[0])
            airLineFirstPosIndex.append(tempIndex[1])
            airLineEndPosIndex.append(tempIndex[2])
            airLineEndPosIndex.append(tempIndex[3])
        else:
            airLineFirstPosIndex.append(tempIndex[2])
            airLineFirstPosIndex.append(tempIndex[3])
            airLineEndPosIndex.append(tempIndex[0])
            airLineEndPosIndex.append(tempIndex[1])

        return airLineAlpha,airLineBeta,airLineFirstPosIndex,airLineEndPosIndex

class plotOnMap:
    def __init__(self,map):
        self.map = map

    def plotAirLine(self,firstPos,endPos,rgb):
        cv2.line(self.map,(firstPos[0],firstPos[1]),(endPos[0],endPos[1]),rgb,10)
        return self.map
    
    def plotPlayerPosition(self,playerPos,bgr):
        h,w,c = self.map.shape
        position = playerPos.split(',')
        x = int(float(position[0])/100)
        y = int(float(position[1])/100)

        cv2.circle(self.map,(x,y),int(h/500),bgr,-1)
        return self.map
    
    def plotPlayerHeatMap(self,playerPos,rank):
        h,w,c = self.map.shape
        position = playerPos.split(',')
        x = int(float(position[0])/100)
        y = int(float(position[1])/100)
        loopRange = int(h/300)
        
        if rank == 0:
            for i in range(loopRange*2):
                for j in range(loopRange*2):
                    temp = self.map[y+j-loopRange,x+i-loopRange][2]+70
                    if temp < 255:
                        self.map[y+j-loopRange,x+i-loopRange][2] += 70
                    else:
                        self.map[y+j-loopRange,x+i-loopRange][2] = 255
        else:
            for i in range(loopRange*2):
                for j in range(loopRange*2):
                    temp = self.map[y+j-loopRange,x+i-loopRange][0]+70
                    if temp < 255:
                        self.map[y+j-loopRange,x+i-loopRange][0] += 70
                    else: 
                        self.map[y+j-loopRange,x+i-loopRange][0] = 255
        
        return self.map

def main():
    airLineAlpha = 0
    airLineBeta = 0
    limit = 0
    airLineFirstPositionIndex = []
    airLineEndPositionIndex = []
    tempListFirst = []
    tempListEnd = []
    matchedListFirst = []
    matchedListEnd = []
    playerMatchList = []
    weakPlayerMatchList = []
    #api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.STEAM)
    #players = api.players().filter(player_names=['youri401'])
    #player = players[0]
    #match = api.matches().get(player.matches[0].id)
    #print(match.map_name)
    #asset = match.assets[0]
    #map = getMapImg(match.map_name)
    api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.STEAM)
    sample = api.samples().get()
    matchId = sample.matches[0].id
    match = api.matches().get(matchId)
    asset = match.assets[0]
    telemetry = api.telemetry(asset.url)
    instance = getMatchInfo(telemetry)
    if not(match.map_name == "Range_Main"):
        map = getMapImg(match.map_name)
        h,w,c = map.shape
        limit = h/10
        print(match.map_name)
        airLineAlpha,airLineBeta,airLineFirstPositionIndex,airLineEndPositionIndex = instance.getAirPlaneInfo(map)

        df = pd.read_csv('match.csv',header=0)
        df_exact = df[df['mapName'] == match.map_name]
        df_exact = df[df['mode'] == match.game_mode]
        df_airLineFirstPos = df_exact['airLineFirstPos']
        df_airLineEndPos = df_exact['airLineEndPos']
        df_matchId = df_exact['matchId']
        airLineFirstList = df_airLineFirstPos.values.tolist()
        airLineEndList = df_airLineEndPos.values.tolist()
        matchIdList = df_matchId.values.tolist()
        print('getAirLine')
        df_player = getPlayerCsv(match.map_name)

        for i in range(len(airLineFirstList)):
            tempListFirst = airLineFirstList[i].split(',')
            tempListEnd = airLineEndList[i].split(',')

            #if (int(tempListFirst[0]) < airLineFirstPositionIndex[0]+width and int(tempListFirst[0]) > airLineFirstPositionIndex[0]-width) and (int(tempListFirst[1]) < airLineFirstPositionIndex[1]+width and int(tempListFirst[1]) > airLineFirstPositionIndex[1]-width) and (int(tempListEnd[0]) < airLineEndPositionIndex[0]+width and int(tempListEnd[0]) > airLineEndPositionIndex[0]-width) and (int(tempListEnd[1]) < airLineEndPositionIndex[1]+width and int(tempListEnd[1]) > airLineEndPositionIndex[1]-width):
                #matchedListFirst.append([int(tempListFirst[0]),int(tempListFirst[1])])
                #matchedListEnd.append([int(tempListEnd[0]),int(tempListEnd[1])])
        
            if (abs(int(tempListFirst[0])-airLineFirstPositionIndex[0])+abs(int(tempListFirst[1])-airLineFirstPositionIndex[1])+abs(int(tempListEnd[0])-airLineEndPositionIndex[0])+abs(int(tempListEnd[1])-airLineEndPositionIndex[1])) < limit:
                matchedListFirst.append([int(tempListFirst[0]),int(tempListFirst[1])])
                matchedListEnd.append([int(tempListEnd[0]),int(tempListEnd[1])])

                df_player_exact = df_player[df_player['matchId'] == matchIdList[i]]
                df_drop = df_player_exact[df_player_exact['ranking'] != '[]'].copy()
                castData = df_drop['ranking'].astype(np.int64)
                df_drop.loc[df_drop['ranking']!='[]','ranking'] = castData

                df_top10player = df_drop[(df_drop['ranking'] != 0) & (df_drop['ranking'] < 10)]
                df_weakPlayer = df_drop[(df_drop['ranking'] > 10) | (df_drop['ranking']== 0)]
                df_top10PlayerLanding = df_top10player['landingPos']
                df_weakPlayerLanding = df_weakPlayer['landingPos']
                top10PlayerList = df_top10PlayerLanding.values.tolist()
                weakPlayerList = df_weakPlayerLanding.values.tolist()
                playerMatchList.extend(top10PlayerList)
                weakPlayerMatchList.extend(weakPlayerList)
    
        print('Number of Match',len(matchedListFirst))
        print(match.game_mode)
        print('Number of Top 10 Player',len(playerMatchList))

        pom = plotOnMap(map)

        for i in range(len(playerMatchList)):
            #map = pom.plotPlayerPosition(playerMatchList[i],(0,0,255))
            map = pom.plotPlayerHeatMap(playerMatchList[i],0)
    
        for i in range(len(weakPlayerMatchList)):
            #map = pom.plotPlayerPosition(weakPlayerMatchList[i],(255,0,0))
            map = pom.plotPlayerHeatMap(weakPlayerMatchList[i],1)

        map = pom.plotAirLine(airLineFirstPositionIndex,airLineEndPositionIndex,(0,0,255))

        cv2.imwrite('output.jpg',map)
    else:print('this is range map')


def getMapImg(mapName):
    if mapName == "Erangel_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Erangel_Main_High_Res.jpg')
    elif mapName == "Desert_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Miramar_Main_High_Res.jpg')
    elif mapName == "Savage_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Sanhok_Main_No_Text_Med_Res.jpg')
    elif mapName == 'DihorOtok_Main':
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Vikendi_Main_High_Res.jpg')
    return map

def getPlayerCsv(mapName):
    if mapName == "Erangel_Main":
        df_player = pd.read_csv('playerErangel.csv',header=0)
    elif mapName == "Desert_Main":
        df_player = pd.read_csv('playerDesert.csv',header=0)
    elif mapName == "Savage_Main":
        df_player = pd.read_csv('playerSavage.csv',header=0)
    elif mapName == 'DihorOtok_Main':
        df_player = pd.read_csv('playerDihorOtok.csv',header=0)
    return df_player

if __name__ == '__main__':
    main()

