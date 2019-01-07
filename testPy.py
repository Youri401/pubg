import pandas as pd

df = pd.read_csv('testcsv.csv',header=0)
tempStr = df['posx'][0]
tempStr = tempStr.split(',')
print(float(tempStr[0]))