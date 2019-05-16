from pubg_python import PUBG, Shard
import cv2
import csv

class getPlayersPositonInfo:
    def __init__(self,map,telemetry):
        self.map = map
        self.LogPlayerPosition = telemetry.events_from_type('LogPlayerPosition')
        self.telemetry = telemetry

    def getAllPlayersAllInfo(self):
        lo = self.telemetry.events_from_type('LogPlayerCreate')
        charaNameIndex = []
        charaIdIndex = []
        charaPositionXIndex = [[] for i in range(len(lo))]
        charaPositionYIndex = [[] for i in range(len(lo))]
        charaPositionZIndex = [[] for i in range(len(lo))]
        charaRankIndex = [[] for i in range(len(lo))]
        elapsedTimeIndex = [[] for i in range(len(lo))]

        for i in range(len(lo)):
            charaNameIndex.append(lo[i].character.name)
            charaIdIndex.append(lo[i].character.account_id)

        for i in range(len(self.LogPlayerPosition)):
            if not(self.LogPlayerPosition[i].elapsed_time == 0):
                charaPositionXIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)].append(self.LogPlayerPosition[i].character.location.x)
                charaPositionYIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)].append(self.LogPlayerPosition[i].character.location.y)
                charaPositionZIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)].append(self.LogPlayerPosition[i].character.location.z)
                charaRankIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)] = self.LogPlayerPosition[i].character.ranking
                elapsedTimeIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)].append(self.LogPlayerPosition[i].elapsed_time)
        
        return charaNameIndex,charaIdIndex,charaPositionXIndex,charaPositionYIndex,charaPositionZIndex,charaRankIndex,elapsedTimeIndex

    def getPlayerLandingPosition(self,charaIdIndex):
        lp = self.telemetry.events_from_type('LogParachuteLanding')
        playerLandingPositionIndex = [[0 for i in range(3)]for j in range(len(charaIdIndex))]

        for i in range(len(lp)):
            playerLandingPositionIndex[charaIdIndex.index(lp[i].character.account_id)][0] = lp[i].character.location.x
            playerLandingPositionIndex[charaIdIndex.index(lp[i].character.account_id)][1] = lp[i].character.location.y
            playerLandingPositionIndex[charaIdIndex.index(lp[i].character.account_id)][2] = lp[i].character.location.z
        
        return playerLandingPositionIndex

    def getPlayerKillDeadPosition(self,charaIdIndex,charaRankIndex):
        lp = self.telemetry.events_from_type('LogPlayerKill')
        playerDeadPositionIndex = [[0 for i in range(3)]for j in range(len(charaIdIndex))]
        playerKillPositionIndex = [[0 for i in range(3)]for j in range(len(charaIdIndex))]
        playerKillCountIndex = [0 for i in range(len(charaIdIndex))]
        killSum = 0

        for i in range(len(lp)):
            playerDeadPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][0] = lp[i].victim.location.x
            playerDeadPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][1] = lp[i].victim.location.y
            playerDeadPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][2] = lp[i].victim.location.z
            playerKillPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][0] = lp[i].killer.location.x
            playerKillPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][1] = lp[i].killer.location.y
            playerKillPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][2] = lp[i].killer.location.z
            playerKillCountIndex[charaIdIndex.index(lp[i].victim.account_id)] = lp[i].victim_game_result.stats.kill_count
            killSum = killSum + lp[i].victim_game_result.stats.kill_count
        
        if 1 in charaRankIndex:
            playerKillCountIndex[charaRankIndex.index(1)] = len(lp) - killSum
        
        return playerDeadPositionIndex,playerKillPositionIndex,playerKillCountIndex

    def plotAllPlayersAllPosition(self):
        for i in range(len(self.LogPlayerPosition)):
            if not(self.LogPlayerPosition[i].elapsed_time == 0):
                cv2.circle(self.map,(int(self.LogPlayerPosition[i].character.location.x/100),int(self.LogPlayerPosition[i].character.location.y/100)),15,(0,0,252), -1)
        return self.map

    def plotAllPlayersExpectedAirBornPosition(self):
        charaIndex =[]
        count = 0
        for i in range(len(self.LogPlayerPosition)):
            if self.LogPlayerPosition[i].elapsed_time != 0 and self.LogPlayerPosition[i].elapsed_time < 8000 and self.LogPlayerPosition[i].character.location.z < 6000:
                if not(self.LogPlayerPosition[i].character.account_id in charaIndex):
                    count +=1
                    print(str(self.LogPlayerPosition[i].character.location.z))
                    cv2.circle(map,(int(self.LogPlayerPosition[i].character.location.x/100),int(self.LogPlayerPosition[i].character.location.y/100)),20,(0,0,252), -1)
                    charaIndex.append(self.LogPlayerPosition[i].character.account_id)
        return self.map

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

def main():
    shardName = 'STEAM'
    charaNameIndex = []
    charaIdIndex = []
    charaPositionXIndex = []
    charaPositionYIndex = []
    charaPositionZIndex = []
    charaRankIndex = []
    elapsedTimeIndex = []
    playerDeadPositionIndex = []
    killPlayerPositionIndex = []
    playerKillCountIndex = []
    playerLandingPositionIndex = []

    zoneElapsedTimeIndex = []
    safetyZonePositionXIndex = []
    safetyZonePositionYIndex = []
    safetyZoneRadiusIndex = []
    poisonGasPositionXIndex = []
    poisonGasPositionYIndex = []
    poisonGasRadiusIndex = []
    airLineAlpha = 0
    airLineBeta = 0
    airLineFirstPositionIndex = []
    airLineEndPositionIndex = []
    airLineFirstPos = []
    matchDay = ""

    api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.STEAM)
    sample = api.samples().get()

    for i in range(len(sample.matches)):
        try:
            matchId = sample.matches[i].id
            match = api.matches().get(matchId)
            asset = match.assets[0]
            telemetry = api.telemetry(asset.url)
            log_match_start = telemetry.events_from_type('LogMatchStart')
            log_player_position = telemetry.events_from_type('LogPlayerPosition')

            if not(log_match_start[0].map_name == "Range_Main"):
                if not(log_match_start[0].is_event_mode):
                    map = getMapImg(log_match_start[0].map_name)
                    player = getPlayersPositonInfo(map,telemetry)
                    matchDay = match.attributes["createdAt"]
                    customMatchFlag = log_match_start[0].is_custom_game
                    charaNameIndex,charaIdIndex,charaPositionXIndex,charaPositionYIndex,charaPositionZIndex,charaRankIndex,elapsedTimeIndex = player.getAllPlayersAllInfo()
                    playerDeadPositionIndex,killPlayerPositionIndex,playerKillCountIndex = player.getPlayerKillDeadPosition(charaIdIndex,charaRankIndex)
                    playerLandingPositionIndex = player.getPlayerLandingPosition(charaIdIndex)
                    instanceMatch = getMatchInfo(telemetry)
                    zoneElapsedTimeIndex,safetyZonePositionXIndex,safetyZonePositionYIndex,safetyZoneRadiusIndex,poisonGasPositionXIndex,poisonGasPositionYIndex,poisonGasRadiusIndex = instanceMatch.getSafetyAndPoisonGasPosInfo()
                    airLineAlpha,airLineBeta,airLineFirstPositionIndex,airLineEndPositionIndex = instanceMatch.getAirPlaneInfo(map)

                    wpIndex = makePlayerWriteIndex(charaNameIndex,charaIdIndex,charaRankIndex,playerLandingPositionIndex,elapsedTimeIndex,charaPositionXIndex,charaPositionYIndex,charaPositionZIndex,playerDeadPositionIndex,killPlayerPositionIndex,playerKillCountIndex,match.id)
                    wmIndex = makeMatchWriteIndex(match.map_name,match.game_mode,match.id,matchDay,customMatchFlag,airLineAlpha,airLineBeta,airLineFirstPositionIndex,airLineEndPositionIndex,zoneElapsedTimeIndex,safetyZonePositionXIndex,safetyZonePositionYIndex,safetyZoneRadiusIndex,poisonGasPositionXIndex,poisonGasPositionYIndex,poisonGasRadiusIndex,shardName)

                    print(str(i)+"/"+str(len(sample.matches))+"  :  "+match.map_name)

                    writePlayerCsv(wpIndex,match.map_name,match.game_mode)
                    writeMatchCsv(wmIndex)

                else: print(str(i)+" : this match is EventMode")
            else: print(str(i)+"/"+str(len(sample.matches))+" : this match is Range_Main")
        except Exception as e:
            print(e)

def writePlayerCsv(index,mapName,gameMode):
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
        with open(csvName,'a') as f:
            writer = csv.writer(f,lineterminator='\n')
            print("writePlayerInfo...")
            writer.writerows(index)
    elif mapName == "Desert_Main":
        csvName = "csv/playerDesert"+gameModeName+".csv"
        with open(csvName,'a') as f:
            writer = csv.writer(f,lineterminator='\n')
            print("writePlayerInfo...")
            writer.writerows(index)
    elif mapName == "Savage_Main":
        csvName = "csv/playerSavage"+gameModeName+".csv"
        with open(csvName,'a') as f:
            writer = csv.writer(f,lineterminator='\n')
            print("writePlayerInfo...")
            writer.writerows(index)
    elif mapName == 'DihorOtok_Main':
        csvName = "csv/playerDihorOtok"+gameModeName+".csv"
        with open(csvName,'a') as f:
            writer = csv.writer(f,lineterminator='\n')
            print("writePlayerInfo...")
            writer.writerows(index)

def writeMatchCsv(index):
    print("writeMatchInfo...")
    with open('match.csv','a') as g:
        writer = csv.writer(g,lineterminator='\n')
        writer.writerow(index)    

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

def makePlayerWriteIndex(charaNameIndex,charaIdIndex,charaRankIndex,playerLandingPositionIndex,elapsedTimeIndex,charaPositionXIndex,charaPositionYIndex,charaPositionZIndex,playerDeadPositionIndex,killPlayerPositionIndex,playerKillCountIndex,matchId):
    writeIndex = []
    print(len(charaNameIndex))
    for i in range(len(charaNameIndex)):
        charaPositionXStr = changeListToStr(charaPositionXIndex[i])
        charaPositionYStr = changeListToStr(charaPositionYIndex[i])
        charaPositionZStr = changeListToStr(charaPositionZIndex[i])
        playerLandingPositionStr = changeListToStr(playerLandingPositionIndex[i])
        elapsedTimeStr = changeListToStr(elapsedTimeIndex[i])
        playerDeadPositionStr = changeListToStr(playerDeadPositionIndex[i])
        killPlayerPositionStr = changeListToStr(killPlayerPositionIndex[i])

        writeIndex.append([charaNameIndex[i],charaIdIndex[i],charaRankIndex[i],playerLandingPositionStr,elapsedTimeStr,charaPositionXStr,charaPositionYStr,charaPositionZStr,playerDeadPositionStr,killPlayerPositionStr,playerKillCountIndex[i],matchId])
    return writeIndex

def makeMatchWriteIndex(mapName,mode,matchId,matchDay,customMatchFlag,airLineAlpha,airLineBeta,airLineFirstPositionIndex,airLineEndPositionIndex,zoneElapsedTimeIndex,safetyZonePositionXIndex,safetyZonePositionYIndex,safetyZoneRadiusIndex,poisonGasPositionXIndex,poisonGasPositionYIndex,poisonGasRadiusIndex,shardName):
    writeIndex = []
    airLineFirstPositionStr = changeListToStr(airLineFirstPositionIndex)
    airLineEndPositionStr = changeListToStr(airLineEndPositionIndex)
    zoneElapsedTimeStr = changeListToStr(zoneElapsedTimeIndex)
    safetyZonePositionXStr = changeListToStr(safetyZonePositionXIndex)
    safetyZonePositionYStr = changeListToStr(safetyZonePositionYIndex)
    safetyZoneRadiusStr = changeListToStr(safetyZoneRadiusIndex)
    poisonGasPositionXStr = changeListToStr(poisonGasPositionXIndex)
    poisonGasPositionYStr = changeListToStr(poisonGasPositionYIndex)
    poisonGasRadiusStr = changeListToStr(poisonGasRadiusIndex)

    writeIndex = [mapName,mode,matchId,matchDay,customMatchFlag,airLineAlpha,airLineBeta,airLineFirstPositionStr,airLineEndPositionStr,zoneElapsedTimeStr,safetyZonePositionXStr,safetyZonePositionYStr,safetyZoneRadiusStr,poisonGasPositionXStr,poisonGasPositionYStr,poisonGasRadiusStr,shardName]
    return writeIndex

def changeListToStr(index):
    index = str(index)
    index = index.strip('[]')
    index = index.replace(' ','')
    return index

if __name__ == '__main__':
    main()