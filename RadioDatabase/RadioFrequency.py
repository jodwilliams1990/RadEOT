import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df=pd.DataFrame()
file=open("Radio.rtf", "r")
data=[]

'''
for line in file:
    if 'cb3' in line:
        data_line = line.rstrip().split('\t')
        data.append(data_line)
'''

lines=file.readlines()
i=0
while (i<len(lines)):
    line=lines[i]
    if 'cb3' in line:
        dl = str(line.rstrip().split('\t'))
        data_line = dl.split('\\') #re.search('cb3(.*)\\cb1', dl)
        for s in data_line:
            if 'cb3' in s:
                db=s[4:]
                if 'Hz' in db and 'Concurrent' not in db and 'Award' not in db:
                    db=db.split()
                    if len(db)==4:
                        if db[3]=="kHz":
                            multiple=1000
                        elif db[3]=="MHz":
                            multiple=1
                        elif db[3]=="GHz":
                            multiple=0.001
                        ff=(str(float(db[0])/multiple))
                        ft=(str(float(db[2])/multiple))
                        
                    elif len(db)==5:
                        if db[1]=="kHz":
                            multiple=1000
                        elif db[1]=="MHz":
                            multiple=1
                        elif db[1]=="GHz":
                            multiple=0.001
                        ff=(str(float(db[0])/multiple))
                        if db[4]=="kHz":
                            multiple=1000
                        elif db[4]=="MHz":
                            multiple=1
                        elif db[4]=="GHz":
                            multiple=0.001
                        ft=(str(float(db[3])/multiple))
                        
                    else:
                        print(len(db), db)
                    #print(db)
                    dl1 = str(lines[i+2].rstrip().split('\t'))
                    data_line1 = dl1.split('\c')
                    dl2 = str(lines[i+4].rstrip().split('\t'))
                    data_line2 = dl2.split('\c')
                    dfev = pd.DataFrame(dict(
                        ffrom=ff,
                        fto=ft,
                        units='MHz',
                        descr1=data_line1[2][3:-1],
                        descr2=data_line2[2][3:-1],
                    ), index=[0])
                #data.append(db)
                    df = df.append(dfev, ignore_index=True)
        i=i+3
    else:
        i=i+1

df.to_hdf('database.h5',key='df',mode='w')
reader = pd.read_hdf('database.h5')
ffo = reader['ffrom'].astype(np.float)
fto = reader['fto'].astype(np.float)
de1 = reader['descr1']
de2 = reader['descr2']

ftest= 1.1
utest='GHz'
if utest == 'kHz':
    ftest=ftest/1000
elif utest == 'GHz':
    ftest=ftest*1000

for i in range (0,len(ffo)):
    #print(ftest, type(ftest), ffo[i], fto[i])
    if ftest >= ffo[i] and ftest<=fto[i]:
        print(ftest, 'MHz: ', de1[i], de2[i])