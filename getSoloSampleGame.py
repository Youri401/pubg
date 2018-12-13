from pubg_python import PUBG, Shard
import cv2

class plotPlayersPos:
    def __init__(self,map,LogPlayerPosition):
        self.map = map
        self.LogPlayerPosition = LogPlayerPosition

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
    api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.PC_NA)
    sample = api.samples().get()
    matchId = sample.matches[0].id
    match = api.matches().get(matchId)
    asset = match.assets[0]
    telemetry = api.telemetry(asset.url)
    log_match_start = telemetry.events_from_type('LogMatchStart')
    log_player_position = telemetry.events_from_type('LogPlayerPosition')
    if not(log_match_start[0].map_name == "Range_Main"):
        map = getMapImg(log_match_start[0].map_name)
        cv2.imwrite("output.png", map)
    else: print("this match is Range_Main")

def getMapImg(mapName):
    if mapName == "Erangel_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Erangel_Main_High_Res.jpg')
    elif mapName == "Desert_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Miramar_Main_High_Res.jpg')
    elif mapName == "Savage_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Sanhok_Main_No_Text_Med_Res.jpg')
    return map

if __name__ == '__main__':
    main()