import pandas as pd
from pubg_python import PUBG, Shard
import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import time

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

class cv2PlotOnMap:
    def __init__(self,map):
        self.map = map

    def plotAirLine(self,firstPos,endPos,rgb):
        cv2.line(self.map,(firstPos[0],firstPos[1]),(endPos[0],endPos[1]),rgb,30)
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

    def plotPlayerHeatPosition(self,map,playerPosList,color):
        h,w,c = map.shape
        map = cv2.cvtColor(map, cv2.COLOR_BGR2RGB)
        plt.imshow(map)
        playerXList = []
        playerYList = []

        for i in range(len(playerPosList)):
            position = playerPosList[i].split(',')
            playerXList.append(int(float(position[0])/100))
            playerYList.append(int(float(position[1])/100))
        plt.scatter(playerXList, playerYList, marker="o",alpha=0.03,c=color,s=3)
        plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False)

class matPlotOnMap():
    def __init__(self,map):
        self.map = cv2.cvtColor(map, cv2.COLOR_BGR2RGB)
        plt.imshow(self.map)

    def plotPlayerHeatMap(self,playerPosList,color,weight):
        h,w,c = self.map.shape
        playerXList = []
        playerYList = []

        for i in range(len(playerPosList)):
            position = playerPosList[i].split(',')
            playerXList.append(int(float(position[0])/100))
            playerYList.append(int(float(position[1])/100))
        plt.scatter(playerXList, playerYList, marker="o",alpha=weight,c=color,s=5)
        plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False)

    def plotAirLine(self,alpha,beta):
        h,w,c = self.map.shape
        x = np.arange(0, h, 1)
        y = alpha*x+beta
        xy = np.concatenate([x, y])
        xy = np.reshape(xy,(2,h))
        xy = xy[:,np.all((xy<=h)& (xy >= 0),axis = 0)]
        plt.plot(xy[0],xy[1],linestyle="dashed",label = 'airLine')
        plt.quiver(xy[0][int(xy[0].size-xy[0].size/10)],xy[1][int(xy[0].size-xy[0].size/10)],xy[0][xy[0].size-1]-xy[0][int(xy[0].size-xy[0].size/10)],xy[1][xy[0].size-1]-xy[1][int(xy[1].size-xy[0].size/10)],angles='xy',scale_units='xy',headwidth = 5,color = 'C0')
    
    def saveFigure(self,gameMode,mapName):
        h,w,c = self.map.shape
        plt.xlim(0,w)
        plt.ylim(h,0)
        plt.scatter([], [], marker="o",c='red',s=5,label = 'top10')
        plt.scatter([], [], marker="o",c='blue',s=5,label = 'other')
        titleName = mapName + ' : '+gameMode
        plt.title(titleName,loc = 'left',fontsize = 6)
        plt.legend(loc='upper left',fontsize = 6).get_frame().set_alpha(0.4)
        plt.savefig('output.png', dpi = 500, transparent = True, bbox_inches = 'tight', pad_inches = 0)

def main():
    airLineAlpha = 0
    airLineBeta = 0
    limit = 0
    airLineFirstPositionIndex = []
    airLineEndPositionIndex = []
    tempListFirst = []
    tempListEnd = []
    #matchedListFirst = []
    #matchedListEnd = []
    playerMatchList = []
    #weakPlayerMatchList = []
    matchedAlphaList = []
    matchedBetaList = []
    matchedMatchIdList = []
    playerList = []
    
    api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.STEAM)
    sample = api.samples().get()
    matchId = sample.matches[1].id
    match = api.matches().get(matchId)
    asset = match.assets[0]
    telemetry = api.telemetry(asset.url)
    instance = getMatchInfo(telemetry)

    if not(match.map_name == "Range_Main"):
        map = getMapImg(match.map_name)
        print(match.game_mode)
        h,w,c = map.shape
        limit = h/10
        print(match.map_name)
        airLineAlpha,airLineBeta,airLineFirstPositionIndex,airLineEndPositionIndex = instance.getAirPlaneInfo(map)
        print(time.perf_counter())
        df = pd.read_csv('csv/match.csv',header=0)
        print(time.perf_counter())
        df_exact = df[df['mapName'] == match.map_name]
        df_exact = df[df['mode'] == match.game_mode]
        df_airLineFirstPos = df_exact['airLineFirstPos']
        df_airLineEndPos = df_exact['airLineEndPos']
        df_matchId = df_exact['matchId']

        airLineFirstList = df_airLineFirstPos.values.tolist()
        airLineEndList = df_airLineEndPos.values.tolist()
        matchIdList = df_matchId.values.tolist()
        print(time.perf_counter())
        df_player = getPlayerCsv(match.map_name,match.game_mode)
        print(time.perf_counter())
        print(len(airLineFirstList))

        for i in range(len(airLineFirstList)):
            tempListFirst = airLineFirstList[i].split(',')
            tempListEnd = airLineEndList[i].split(',')

            if (abs(int(tempListFirst[0])-airLineFirstPositionIndex[0])+abs(int(tempListFirst[1])-airLineFirstPositionIndex[1])+abs(int(tempListEnd[0])-airLineEndPositionIndex[0])+abs(int(tempListEnd[1])-airLineEndPositionIndex[1])) < limit:
                #matchedListFirst.append([int(tempListFirst[0]),int(tempListFirst[1])])         #類似AirLine出力用
                #matchedListEnd.append([int(tempListEnd[0]),int(tempListEnd[1])])
                matchedMatchIdList.append(matchIdList[i])

        df_player_exact = df_player[df_player['matchId'].isin(matchedMatchIdList)]
        df_drop = df_player_exact[df_player_exact['ranking'] != '[]'].copy()
        castData = df_drop['ranking'].astype(np.int64)
        df_drop.loc[df_drop['ranking']!='[]','ranking'] = castData

        df_top10player = df_drop[(df_drop['ranking'] != 0) & (df_drop['ranking'] < 10)]
        df_weakPlayer = df_drop[(df_drop['ranking'] > 10) | (df_drop['ranking']== 0)]
        df_top10PlayerLanding = df_top10player['landingPos']
        df_weakPlayerLanding = df_weakPlayer['landingPos']
        top10PlayerList = df_top10PlayerLanding.values.tolist()
        weakPlayerList = df_weakPlayerLanding.values.tolist()
        #playerMatchList.extend(top10PlayerList)
        #weakPlayerMatchList.extend(weakPlayerList)
    
        print('Number of Match',len(matchedMatchIdList))
        print('Number of Top 10 Player',len(top10PlayerList))

        mpom = matPlotOnMap(map)
        playerList.extend(weakPlayerList)
        playerList.extend(top10PlayerList)

        #map = pom.plotAirLine(airLineFirstPositionIndex,airLineEndPositionIndex,(0,0,0))
        mpom.plotPlayerHeatMap(top10PlayerList,'red',0.1)
        mpom.plotPlayerHeatMap(weakPlayerList,'blue',0.03)
        mpom.plotAirLine(airLineAlpha,airLineBeta)
        mpom.saveFigure(match.game_mode,getMapName(match.map_name))
        print(time.perf_counter())

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

def getPlayerCsv(mapName,gameMode):
    gameModeName = ""

    if gameMode == "solo":
        gameModeName = "Solo"
    elif gameMode == "duo":
        gameModeName = "Duo"
    elif gameMode == "squad":
        gameModeName = "Squad"
    elif gameMode == "solo-fpp":
        gameModeName = "SoloFpp"
    elif gameMode == "duo-fpp":
        gameModeName = "DuoFpp"
    elif gameMode == "squad-fpp":
        gameModeName = "SquadFpp"

    if mapName == "Erangel_Main":
        csvName = "csv/playerErangel"+gameModeName+".csv"
        df_player = pd.read_csv(csvName,header=0)
    elif mapName == "Desert_Main":
        csvName = "csv/playerDesert"+gameModeName+".csv"
        df_player = pd.read_csv(csvName,header=0)
    elif mapName == "Savage_Main":
        csvName = "csv/playerSavage"+gameModeName+".csv"
        df_player = pd.read_csv(csvName,header=0)
    elif mapName == 'DihorOtok_Main':
        csvName = "csv/playerDihorOtok"+gameModeName+".csv"
        df_player = pd.read_csv(csvName,header=0)
    return df_player

def getMapName(mapName):
    name = ''
    if mapName == "Erangel_Main":
        name = 'Erangel'
    elif mapName == "Desert_Main":
        name = 'Miramar'
    elif mapName == "Savage_Main":
        name = 'Sanhok'
    elif mapName == 'DihorOtok_Main':
        name = 'Vikendi'
    return name

if __name__ == '__main__':
    main()

