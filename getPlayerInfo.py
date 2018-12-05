from pubg_python import PUBG, Shard
import cv2

def main():
    #top10Chara = []
    map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Erangel_Main_Low_Res.jpg')
    h,w,c = map.shape
    api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.STEAM)
    players = api.players().filter(player_names=['youri401'])
    player = players[0]
    match = api.matches().get(player.matches[0].id)
    asset = match.assets[0]
    telemetry = api.telemetry(asset.url)
    ppe = telemetry.events_from_type('LogPlayerPosition')
    for i in range(len(ppe)):
        if ppe[i].character.name == "youri401":
            cv2.circle(map,(int(ppe[i].character.location.x/100*h/8160),int(ppe[i].character.location.y/100*w/8160)),20,(0,0,252), -1)
            #print(str(ppe[i].elapsed_time)+":("+str(ppe[i].character.location.x)+","+str(ppe[i].character.location.y)+","+str(ppe[i].character.location.z)+")")
    cv2.imwrite("output2.png", map)

if __name__ == '__main__':
    main()
