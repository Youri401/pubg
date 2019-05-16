from pubg_python import PUBG, Shard
import cv2

api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.STEAM)
players = api.players().filter(player_names=['youri401'])
player = players[0]
match = api.matches().get(player.matches[0].id)
asset = match.assets[0]
telemetry = api.telemetry(asset.url)
ppe = telemetry.events_from_type('LogGameStatePeriodic')
map = cv2.imread(r'C:\Users\youri\Documents\api-assets\Assets\Maps\Vikendi_Main_High_Res.jpg')
for i in range(len(ppe)):
    print(str(ppe[i].game_state.elapsed_time)+","+str(ppe[i].game_state.poison_gas_warning_radius)+":"+str(ppe[i].game_state.safety_zone_radius))

#for i in range(len(ppe)):
#    cv2.circle(map,(int(ppe[i].game_state.safetyZonePos.x/0.75/100),int(ppe[i].game_state.safetyZonePos.y/0.75/100)),int(ppe[i].game_state.safety_zone_radius/100/0.75),(0,0,252), 10)
#cv2.imwrite("output.png",map)
#for i in range(len(ppe)):
#    cv2.circle(map,(int(ppe[i].game_state.poisonGasWarningPos.x/100),int(ppe[i].game_state.poisonGasWarningPos.y/100)),int(ppe[i].game_state.poison_gas_warning_radius/100),(0,0,252), 10)
#cv2.imwrite("output.png",map)