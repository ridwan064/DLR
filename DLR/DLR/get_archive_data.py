import csv

#index=[]
#i=2
#while i<39:
#    index.append(i)
#    i=i+4

#print (index.pop())
with open('s2-main.csv') as fd:
    reader=csv.reader(fd)
    interestingrows=[row for idx, row in enumerate(reader) if idx in (2, 6, 10, 14, 18, 22, 26, 30, 34, 38)]
    p = str(str(interestingrows[0]).split(",")[7].strip())
    pp = float(p)
    print (pp)



