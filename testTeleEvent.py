from pubg_python import PUBG, Shard

api = PUBG('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiMGVhNmM0MC1kNGQzLTAxMzYtYmQ3ZC03MzkyZGYzNjZhZTAiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTQzMzY1NDQxLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InlvdXJpNDAxIn0.Z9i2twdF8yDkSPQ2DVjy1jbr7E5PbtiiB9n3UgfyKCg', Shard.PC_NA)
sample = api.samples().get()
matchId = sample.matches[1].id
match = api.matches().get(matchId)
asset = match.assets[0]
telemetry = api.telemetry(asset.url)
print(match.map_name)
lp = telemetry.events_from_type('LogParachuteLanding')
print(dir(lp[0]))