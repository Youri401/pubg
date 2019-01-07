from pubg_python import PUBG, Shard
import cv2
import csv

class getPlayersPositonInfo:
    def __init__(self,map,LogPlayerPosition):
        self.map = map
        self.LogPlayerPosition = LogPlayerPosition

    def getAllPlayersAllInfo(self):
        charaNameIndex = []
        charaIdIndex = []
        charaPositionXIndex = []
        charaPositionYIndex = []
        charaPositionZIndex = []
        charaRankIndex = []
        elapsedTimeIndex = []

        for i in range(len(self.LogPlayerPosition)):
            if not(self.LogPlayerPosition[i].elapsed_time == 0):
                if self.LogPlayerPosition[i].character.name in charaNameIndex:
                    charaPositionXIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)].append(self.LogPlayerPosition[i].character.location.x)
                    charaPositionYIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)].append(self.LogPlayerPosition[i].character.location.y)
                    charaPositionZIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)].append(self.LogPlayerPosition[i].character.location.z)
                    charaRankIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)] = self.LogPlayerPosition[i].character.ranking
                    elapsedTimeIndex[charaNameIndex.index(self.LogPlayerPosition[i].character.name)].append(self.LogPlayerPosition[i].elapsed_time)
                else:
                    charaNameIndex.append(self.LogPlayerPosition[i].character.name)
                    charaPositionXIndex.append([self.LogPlayerPosition[i].character.location.x])
                    charaPositionYIndex.append([self.LogPlayerPosition[i].character.location.y])
                    charaPositionZIndex.append([self.LogPlayerPosition[i].character.location.z])
                    charaRankIndex.append(self.LogPlayerPosition[i].character.ranking)
                    elapsedTimeIndex.append([self.LogPlayerPosition[i].elapsed_time])
                    charaIdIndex.append(self.LogPlayerPosition[i].character.account_id)
        
        return charaNameIndex,charaIdIndex,charaPositionXIndex,charaPositionYIndex,charaPositionZIndex,charaRankIndex,elapsedTimeIndex

    def getPlayerLandingPosition(self,charaIdIndex,logParachuteLanding):
        lp = logParachuteLanding
        playerLandingPositionIndex = [[0 for i in range(3)]for j in range(len(charaIdIndex))]

        for i in range(len(lp)):
            playerLandingPositionIndex[charaIdIndex.index(lp[i].character.account_id)][0] = lp[i].character.location.x
            playerLandingPositionIndex[charaIdIndex.index(lp[i].character.account_id)][1] = lp[i].character.location.y
            playerLandingPositionIndex[charaIdIndex.index(lp[i].character.account_id)][2] = lp[i].character.location.z
        
        return playerLandingPositionIndex

    def getPlayerKillDeadPosition(self,charaIdIndex,charaRankIndex,logPlayerKill):
        lp = logPlayerKill
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

    def plotAirPlaneRoot(self):
        airLineIndexPosFirst =[]
        airLineIndexPosEnd =[]
        count = 0
        h,w,c = self.map.shape
        for i in range(len(self.LogPlayerPosition)):
            if not(self.LogPlayerPosition[i].elapsed_time == 0) and self.LogPlayerPosition[i].character.location.z >= 150088 and self.LogPlayerPosition[i].character.location.y > 0:
                if count == 0:
                    airLineIndexPosFirst.append(self.LogPlayerPosition[i].character.location.x/100)
                    airLineIndexPosFirst.append(self.LogPlayerPosition[i].character.location.y/100)
                    count = i

        airLineIndexPosEnd.append(self.LogPlayerPosition[count].character.location.x/100)
        airLineIndexPosEnd.append(self.LogPlayerPosition[count].character.location.y/100)
        a = (airLineIndexPosFirst[1]-airLineIndexPosEnd[1])/(airLineIndexPosFirst[0]-airLineIndexPosEnd[0])
        b = airLineIndexPosFirst[1] - a*airLineIndexPosFirst[0]
        cv2.line(map,(0,int(b)),(h,int((a*h+b))),(255,0,0),5)
        return self.map

def main():
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

    api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.STEAM)
    players = api.players().filter(player_names=['youri401'])
    player = players[0]
    match = api.matches().get(player.matches[0].id)
    print(match.map_name)
    asset = match.assets[0]
    telemetry = api.telemetry(asset.url)
    log_match_start = telemetry.events_from_type('LogMatchStart')
    log_player_position = telemetry.events_from_type('LogPlayerPosition')
    log_player_kill = telemetry.events_from_type('LogPlayerKill')
    log_parachute_landing = telemetry.events_from_type('LogParachuteLanding')

    if not(log_match_start[0].map_name == "Range_Main"):
        map = getMapImg(log_match_start[0].map_name)
        player = getPlayersPositonInfo(map,log_player_position)
        '''
        charaNameIndex,charaIdIndex,charaPositionXIndex,charaPositionYIndex,charaPositionZIndex,charaRankIndex,elapsedTimeIndex = player.getAllPlayersAllInfo()
        playerDeadPositionIndex,killPlayerPositionIndex,playerKillCountIndex = player.getPlayerKillDeadPosition(charaIdIndex,charaRankIndex,log_player_kill)
        playerLandingPositionIndex = player.getPlayerLandingPosition(charaIdIndex,log_parachute_landing)

        wIndex = makeWriteIndex(charaNameIndex,charaIdIndex,charaRankIndex,playerLandingPositionIndex,elapsedTimeIndex,charaPositionXIndex,charaPositionYIndex,charaPositionZIndex,playerDeadPositionIndex,killPlayerPositionIndex,playerKillCountIndex,match.id)
        with open('test.csv','a') as f:
            writer = csv.writer(f,lineterminator='\n')
            writer.writerows(wIndex)
        '''
    else: print("this match is Range_Main")

def getMapImg(mapName):
    if mapName == "Erangel_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Erangel_Main_High_Res.jpg')
    elif mapName == "Desert_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Miramar_Main_High_Res.jpg')
    elif mapName == "Savage_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Sanhok_Main_No_Text_Med_Res.jpg')
    elif mapName == 'DihorOtok_Main':
        map = cv2.imread(r'C:\Users\youri\Documents\api-assets\Assets\Maps\Vikendi_Main_High_Res.jpg')
    return map

def makeWriteIndex(charaNameIndex,charaIdIndex,charaRankIndex,playerLandingPositionIndex,elapsedTimeIndex,charaPositionXIndex,charaPositionYIndex,charaPositionZIndex,playerDeadPositionIndex,killPlayerPositionIndex,playerKillCountIndex,matchId):
    writeIndex = []
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

def changeListToStr(index):
    index = str(index)
    index = index.strip('[]')
    index = index.replace(' ','')
    return index

if __name__ == '__main__':
    main()