from pubg_python import PUBG, Shard
import cv2

api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.PC_NA)
sample = api.samples().get()
matchId = sample.matches[1].id
match = api.matches().get(matchId)
asset = match.assets[0]
telemetry = api.telemetry(asset.url)
log_match_start = telemetry.events_from_type('LogMatchStart')
ppe = telemetry.events_from_type('LogPlayerPosition')
mapFlag = True
if log_match_start[0].map_name == "Erangel_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Erangel_Main_High_Res.jpg')
        h,w,c = map.shape
elif log_match_start[0].map_name == "Desert_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Miramar_Main_High_Res.jpg')
        h,w,c = map.shape
elif log_match_start[0].map_name == "Savage_Main":
        map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Sanhok_Main_No_Text_Med_Res.jpg')
        h,w,c = map.shape
elif log_match_start[0].map_name == "Range_Main":
        mapFlag = False

for i in range(len(ppe)):
        if not(ppe[i].elapsed_time == 0):
                cv2.circle(map,(int(ppe[i].character.location.x/100),int(ppe[i].character.location.y/100)),15,(0,0,252), -1)
                #print(str(ppe[i].elapsed_time)+":("+str(ppe[i].character.location.x)+","+str(ppe[i].character.location.y)+","+str(ppe[i].character.location.z)+")")
cv2.imwrite("output.png", map)
