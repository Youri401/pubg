import matplotlib.patches as mpatches
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from pubg_python import PUBG, Shard
import pandas as pd
import cv2
import numpy as np
from numpy import inf
import time
import pickle
import warnings

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
        self.h,self.w,self.c = map.shape
        self.range = int(self.h/200)
        self.map = cv2.cvtColor(map, cv2.COLOR_BGR2RGB)
        self.winPer = np.zeros((self.h,self.w))
        self.winIndex = np.zeros((self.h,self.w))
        self.loseIndex = np.zeros((self.h,self.w))
        self.playerCount = np.zeros((self.h,self.w))
        self.tempList = [-1,0,1]

    def plotPlayerHeatMap(self,playerPosList,color,weight):
        playerXList = []
        playerYList = []
        for i in range(len(playerPosList)):
            position = playerPosList[i].split(',')
            playerXList.append(int(float(position[0])/100))
            playerYList.append(int(float(position[1])/100))
        plt.scatter(playerXList, playerYList, marker="o",alpha=weight,c=color,s=5)
        plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False)

    def plotAirLine(self,alpha,beta):
        x = np.arange(0, self.h, 1)
        y = alpha*x+beta
        xy = np.concatenate([x, y])
        xy = np.reshape(xy,(2,self.h))
        xy = xy[:,np.all((xy<=self.h)& (xy >= 0),axis = 0)]
        plt.plot(xy[0],xy[1],linestyle="dashed",label = 'airLine')
        plt.quiver(xy[0][int(xy[0].size-xy[0].size/10)],xy[1][int(xy[0].size-xy[0].size/10)],xy[0][xy[0].size-1]-xy[0][int(xy[0].size-xy[0].size/10)],xy[1][xy[0].size-1]-xy[1][int(xy[1].size-xy[0].size/10)],angles='xy',scale_units='xy',headwidth = 5,color = 'C0')
    
    def saveFigure(self,gameMode,mapName):
        print('save heat map figure')
        h,w,c = self.map.shape
        plt.xlim(0,self.w)
        plt.ylim(self.h,0)
        plt.scatter([], [], marker="o",c='red',s=5,label = 'top10')
        plt.scatter([], [], marker="o",c='blue',s=5,label = 'other')
        titleName = mapName + ' : '+gameMode
        plt.title(titleName,loc = 'left',fontsize = 6)
        plt.legend(loc='upper left',fontsize = 6).get_frame().set_alpha(0.4)
        plt.savefig('output.jpg', dpi = 500, transparent = True, bbox_inches = 'tight', pad_inches = 0)

    def makeHeatIndex(self,playerPos,rank):
        tempX = 0
        tempY = 0

        for i in range(len(playerPos)):
            position = playerPos[i].split(',')
            tempX = int(float(position[0])/100)
            tempY = int(float(position[1])/100)
            self.playerCount[tempX-self.range:tempX+self.range,tempY-self.range:tempY+self.range] +=1
            if rank == 1:
                self.winIndex[tempX-self.range:tempX+self.range,tempY-self.range:tempY+self.range] += rank
            else:self.loseIndex[tempX-self.range:tempX+self.range,tempY-self.range:tempY+self.range] += rank

    def plotHeatMap(self):
        self.winPer = self.loseIndex + self.winIndex
        warnings.filterwarnings('ignore')
        heatMap = self.winPer/self.playerCount
        heatMap[heatMap == inf] = 0
        #xlist = np.where((self.playerCount != 0))[0]
        #ylist = np.where((self.playerCount != 0))[1]
        #valueList = heatMap[self.playerCount != 0]
        sc = plt.scatter(self.tempList, self.tempList,marker="o",s=0.000001,c = self.tempList, vmin=-1, vmax=1, cmap=cm.seismic)
        plt.colorbar(sc)
        self.map[np.where(self.playerCount != 0)[1],np.where(self.playerCount != 0)[0]] = np.delete((np.array(cm.seismic((heatMap[np.where(self.playerCount != 0)]+1)/2))*255).astype(np.int64),3,1)
        plt.imshow(self.map)

    def getLandingPositionWinningPercentage(self,playerName,lp):
        landX = 0
        landY = 0
        landXIndex = []
        landYIndex = []

        for i in range(len(lp)):
            if lp[i].character.name == playerName:
                landX = int(lp[i].character.location.x/100)
                landY = int(lp[i].character.location.y/100)
                landXIndex.append(int(lp[i].character.location.x/100))
                landYIndex.append(int(lp[i].character.location.y/100))
            
        plt.scatter(landXIndex, landYIndex, marker="o",alpha=1,c='yellow',s=3,label = 'player')
        print('player Landing Position is '+str(landX)+','+str(landY))
        print('Landing Positions Number of top10 player is ',int(self.winIndex[landX,landY]))
        print('Landing Positions Number of other player is ',int(abs(self.loseIndex[landX,landY])))

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

    print("input player name")
    name = input()
    print("input last match (example: 0 is last match, 1 is 2d last match)")
    matchNumber = input()
    print()

    api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.STEAM)
    players = api.players().filter(player_names=[name])
    player = players[0]
    match = api.matches().get(player.matches[int(matchNumber)].id)
    asset = match.assets[0]
    telemetry = api.telemetry(asset.url)
    instance = getMatchInfo(telemetry)

    if not(match.map_name == "Range_Main"):
        map = getMapImg(match.map_name)
        print(match.game_mode)
        h,w,c = map.shape
        limit = h/10
        print(getMapName(match.map_name))
        airLineAlpha,airLineBeta,airLineFirstPositionIndex,airLineEndPositionIndex = instance.getAirPlaneInfo(map)
        df = pd.read_pickle('pickle/match.pickle')
        df_exact = df[df['mapName'] == match.map_name]
        df_exact = df[df['mode'] == match.game_mode]
        df_airLineFirstPos = df_exact['airLineFirstPos']
        df_airLineEndPos = df_exact['airLineEndPos']
        df_airLineAlpha = df_exact['airLineAplha']
        df_airLineBeta = df_exact['airLineBeta']
        df_matchId = df_exact['matchId']

        airLineFirstList = df_airLineFirstPos.values.tolist()
        airLineEndList = df_airLineEndPos.values.tolist()
        airLineAlphaList = df_airLineAlpha.values.toList()
        airLineBetaList = df_airLineBeta.values.toList()
        matchIdList = df_matchId.values.tolist()
        df_player = getPlayerPickle(match.map_name,match.game_mode)

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
    
        print('Number of Similar Match',len(matchedMatchIdList))

        mpom = matPlotOnMap(map)
        playerList.extend(weakPlayerList)
        playerList.extend(top10PlayerList)

        #map = pom.plotAirLine(airLineFirstPositionIndex,airLineEndPositionIndex,(0,0,0))
        #mpom.plotPlayerHeatMap(top10PlayerList,'red',0.1)
        #mpom.plotPlayerHeatMap(weakPlayerList,'blue',0.04)
        #mpom.plotAirLine(airLineAlpha,airLineBeta)
        mpom.makeHeatIndex(weakPlayerList,-1)
        mpom.makeHeatIndex(top10PlayerList,1)
        mpom.plotHeatMap()
        mpom.plotAirLine(airLineAlpha,airLineBeta)
        mpom.getLandingPositionWinningPercentage(name,telemetry.events_from_type('LogParachuteLanding'))
        mpom.saveFigure(match.game_mode,getMapName(match.map_name))

        print('end')

    else:print('this match is range map')

def getMapImg(mapName):
    if mapName == "Erangel_Main":
        map = cv2.imread('Maps\Erangel_Main_High_Res.jpg')
    elif mapName == "Desert_Main":
        map = cv2.imread('Maps\Miramar_Main_High_Res.jpg')
    elif mapName == "Savage_Main":
        map = cv2.imread('Maps\Sanhok_Main_No_Text_Med_Res.jpg')
    elif mapName == 'DihorOtok_Main':
        map = cv2.imread('Maps\Vikendi_Main_High_Res.jpg')
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

def getPlayerPickle(mapName,gameMode):
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
        csvName = "pickle/playerErangel"+gameModeName+".pickle"
        df = pd.read_pickle(csvName)
    elif mapName == "Desert_Main":
        csvName = "pickle/playerDesert"+gameModeName+".pickle"
        df = pd.read_pickle(csvName)
    elif mapName == "Savage_Main":
        csvName = "pickle/playerSavage"+gameModeName+".pickle"
        df = pd.read_pickle(csvName)
    elif mapName == 'DihorOtok_Main':
        csvName = "pickle/playerDihorOtok"+gameModeName+".pickle"
        df = pd.read_pickle(csvName)
    return df

if __name__ == '__main__':
    main()

