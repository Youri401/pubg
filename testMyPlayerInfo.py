from pubg_python import PUBG, Shard
import cv2

api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.STEAM)
players = api.players().filter(player_names=['youri401'])
player = players[0]
match = api.matches().get(player.matches[0].id)
print(match.map_name)
asset = match.assets[0]
telemetry = api.telemetry(asset.url)
ppe = telemetry.events_from_type('LogPlayerPosition')
lp = telemetry.events_from_type('LogPlayerKill')
charaIdIndex = []
for i in range(len(ppe)):
    if not(ppe[i].elapsed_time == 0):
        if not(ppe[i].character.account_id in charaIdIndex):
            charaIdIndex.append(ppe[i].character.account_id)

playerDeadPositionIndex = [[0 for i in range(3)]for j in range(len(charaIdIndex))]
playerKillPositionIndex = [[0 for i in range(3)]for j in range(len(charaIdIndex))]
playerKillCountIndex = [0 for i in range(len(charaIdIndex))]

for i in range(len(lp)):
    playerDeadPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][0] = lp[i].victim.location.x
    playerDeadPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][1] = lp[i].victim.location.y
    playerDeadPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][2] = lp[i].victim.location.z
    playerKillPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][0] = lp[i].killer.location.x
    playerKillPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][1] = lp[i].killer.location.y
    playerKillPositionIndex[charaIdIndex.index(lp[i].victim.account_id)][2] = lp[i].killer.location.z
    playerKillCountIndex[charaIdIndex.index(lp[i].victim.account_id)] = lp[i].victim_game_result.stats.kill_count
print(charaIdIndex)
print(playerDeadPositionIndex)
print(playerKillPositionIndex)
print(playerKillCountIndex)
