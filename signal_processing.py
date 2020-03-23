import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import csv
from scipy.signal import savgol_filter
from numpy import mean

txtfiles=[]

def getFiles():
    for file in glob.glob("*.txt"):
        txtfiles.append(file)

def openFile():

    for i in range (txtfiles.__len__()):
        print("Press "+"{}".format(i+1)+" to open "+txtfiles[i])
     
    choice=int(input())
    f=open(txtfiles[choice-1])
    return f
    
def peakdetect(y_axis, x_axis = None, window = 50, delta = 0):
    """
    Wtitten based on a MATLAB script at http://billauer.co.il/peakdet.html
    
    Algorithm to detect local maximas and minmias in a signal.
    It detects peaks by searching for values which are surrounded by lower
    or larger values for maximas and minimas respectively
    
    keyword arguments:
    y_axis: List containg the signal over which to find peaks
    x_axis (optional): A x-axis whose values correspond to the y-axis and is used
        to obtain the x value at the maximas or minimas. (Default: 0 , return the
        index of the y-axis)

    window (optional): distance to look ahead from a peak candidate to
        determine if it is the actual peak (default: 50) 
        
    delta (optional): specifies a minimum difference between a peak and
        the following points, before a peak may be considered a peak. 
        Useful to allow for finer control over processing
    
    returns two lists [maxtab, mintab] containing the maximas and minimas
        respectively. Each cell of the lists contains a tupple of:
        (position, peak_value) 
    """
    maxtab = []
    mintab = []
    dump = []   #Used to pop the first hit which always if false
       
    length = len(y_axis)

    # if x-axis isnt provided
    if x_axis is None:
        x_axis = range(length)
    
    #maxima and minima candidates are temporarily stored in mx and mn
    mn, mx = np.Inf, -np.Inf
    
    #Only detect peak if there is 'window' amount of points after it
    for index, (x, y) in enumerate(zip(x_axis[:-window], y_axis[:-window])):
        if y > mx:
            mx = y
            mxpos = x
        if y < mn:
            mn = y
            mnpos = x
        
        ####look for max####
        if y < mx-delta and mx != np.Inf:
            #Maxima peak candidate found
            #look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+window].max() < mx:
                maxtab.append((mxpos, mx))
                dump.append(True)
                #set algorithm to only find minima now
                mx = np.Inf
                mn = np.Inf
        
        ####look for min####
        if y > mn+delta and mn != -np.Inf:
            #Minima peak candidate found 
            #look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+window].min() > mn:
                mintab.append((mnpos, mn))
                dump.append(False)
                #set algorithm to only find maxima now
                mn = -np.Inf
                mx = -np.Inf
    
    
    #Remove the false hit on the first value of the y_axis
    try:
        if dump[0]:
            maxtab.pop(0)
            #print "pop max"
        else:
            mintab.pop(0)
            #print "pop min"
        del dump
    except IndexError:
        #no peaks were found, should the function return empty lists?
        pass
    
    return maxtab, mintab

#fuction to filter signal
def filter(data_in,N,poly):

    filtered_sig= savgol_filter(data_in,N,poly)

    return filtered_sig

def outlierDeletion(data,N):
    mylist = data
    size = mylist.__len__()

    for i in range (size):
        if(mylist[i]>2*mean(mylist[i:i+N])):
            mylist[i]=mean(mylist[i:i+N])
        elif(mylist[i]<2*mean(mylist[i:i+20])):
            mylist[i]=mean(mylist[i:i+N])
        elif(mylist[i]<mean(mylist)):
            mylist[i]=mean(mylist[i:i+int(N/2)])
        elif(mylist[i]>mean(mylist)):
            mylist[i]=mean(mylist[i:i+int(N/2)])

if __name__=="__main__":

    voltage_current_pairs=[]
    voltage=[]
    current=[]

    #open file
    getFiles()

    for j in range(txtfiles.__len__()):
        file=open(txtfiles[j])

        #read file
        for line in file:
            csv_reader = csv.reader(file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                voltage_current_pairs.append(row)
    
        #split current and voltage into seperate array
        i=0
        while i<voltage_current_pairs.__len__():
            voltage.append(voltage_current_pairs[i][0]) #store voltage only
            current.append(voltage_current_pairs[i][1]) #store current only
            i+=1

        #convert into numpy array
        y = np.asarray(current, dtype=np.float)
        x= np.asarray(voltage, dtype=np.float)
      
        #using algorithm to delete outliers
        window=3
        outlierDeletion(y,window)

        poly=2
        window=11
        y=filter(y,window,poly)

        _max, _min = peakdetect(y,x,10)
        xm = [p[0] for p in _max]
        ym = [p[1] for p in _max]
        xn = [p[0] for p in _min]
        yn = [p[1] for p in _min]

        # color=['r','g','b','k','m','r','r']
        # print(color[j])
        name=["blank calibration","150uM","50uM","250uM","blank","200uM","100uM","150uM"]

        plt.plot(x,y,label=name[j])
        plt.plot(xm,ym,'b+')
        plt.ticklabel_format(style='sci',scilimits=(0,0),axis='y')
        plt.xlabel('Voltage/V')
        plt.ylabel('Current/A')
        plt.title("P-aminophenol Calibration graph by square wave voltammetry")
        print(_max)
 
        voltage_current_pairs.clear()
        voltage.clear()
        current.clear()

    
    plt.legend(loc='best')
    plt.show()
    
