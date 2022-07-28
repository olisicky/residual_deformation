# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 09:08:49 2019

@author: lisicky
"""

import matplotlib.pyplot as plt
import cv2 as cv2
import numpy as np
from interparc import *
from scipy import interpolate
from intersection import *


pixel_size=0.01 #nastavení velikosti pixelu

###############################################################################
#_________________________IMAGE PROCESSING_____________________________________
###############################################################################
mouseX=[]
mouseY=[]

mouseX_1=[]
mouseY_1=[]
#this function will be called whenever the mouse is clicked
def draw_circle(event,x,y,flags,param):
    global mouseX,mouseY
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(imCrop,(x,y),10,(255,0,0),-1)
        mouseX.append(x)
        mouseY.append(y)
        
def draw_circle_1(event,x,y,flags,param):#
    global mouseX_1,mouseY_1
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(imCrop,(x,y),10,(0,0,255),-1)
        mouseX_1.append(x)
        mouseY_1.append(y)

image=cv2.imread('longitudial.png')
img_shape=image.shape
#NAstavení robrazení obrázku s názvem ROI
cv2.namedWindow("ROI", cv2.WINDOW_NORMAL)
#_________________Nastavení pro umístění textu do základního obrázku___________
font                   = cv2.FONT_HERSHEY_SIMPLEX
place = (int(img_shape[0]/0.9),int(img_shape[1]/2 + 100))
place_1 = (int(img_shape[0]/0.9),int(img_shape[1]/2))
fontScale              = 2
fontColor              = (0,0,255)
lineType               = 5

cv2.putText(image, "Choose the region of interest - drag mouse",place_1, font, fontScale, fontColor, lineType)
cv2.putText(image, "Press ENTER to continue",place, font, fontScale, fontColor, lineType)
#ROI funkce mi zobrazí obrázek "image" a jmenuje se "ROI"
r= cv2.selectROI("ROI",image, fromCenter=False)

#_____________________Vyříznutý obrázek a jeho nastavení_______________________
imCrop = image[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
crop_shape=imCrop.shape

#zobrazení obrázku s názvem Image
cv2.imshow("Image", imCrop)
#Zvolená klávesa, než se bude v kódu pokračovat (jakákoliv)
cv2.waitKey(0)

#set mouse callback function for window
cv2.namedWindow("image", cv2.WINDOW_NORMAL)
cv2.setMouseCallback('image',draw_circle) #přiřazení funkce k oknu
#image_shape=img.shape

#_____důležitý je zde skip key (ESC), který vypne okno!!!
while(1):
    cv2.imshow('image',imCrop)
    k = cv2.waitKey(20) & 0xFF
    if k == 27: #Enter to EXIT
        break
#_____________po zmáčknutí a mohu naklikat druhou křivku_______________________
    elif k == ord('a'):
        cv2.destroyAllWindows()#
        cv2.imshow('image',imCrop)#
        cv2.setMouseCallback('image',draw_circle_1) #přiřazení funkce k oknu#
cv2.destroyAllWindows()        

#převedení na Si jednotky, pozor, Y má nulu nahoře
mouseX=np.asarray(mouseX, dtype=float)
mouseY=np.asarray(mouseY, dtype=float)
mouseX_1=np.asarray(mouseX_1, dtype=float)
mouseY_1=np.asarray(mouseY_1, dtype=float)
#Převedení vůči globálním rozměrům, asi je to zbytečný krok, ale neva :D
locX=(mouseX+r[0])*pixel_size
locY=(mouseY+r[1])*pixel_size
locX_1=(mouseX_1+r[0])*pixel_size
locY_1=(mouseY_1+r[1])*pixel_size
###############################################################################
#___________________________Equidistant points_________________________________
###############################################################################
inter=interparc(50,locX,locY,'linear')
inter_1=interparc(50,locX_1,locY_1,'linear')

vzdalenost=[]
vzdalenost_1=[]
for i in range (1,len(inter),1):
    datax=inter[i][0]-inter[i-1][0]
    datay=inter[i][1]-inter[i-1][1]
    data=np.sqrt(datax**2 + datay**2)
    vzdalenost.append(data)
    datax_1=inter_1[i][0]-inter_1[i-1][0]
    datay_1=inter_1[i][1]-inter_1[i-1][1]
    data_1=np.sqrt(datax_1**2 + datay_1**2)
    vzdalenost_1.append(data_1) 
###############################################################################
#_____________________________Segment length___________________________________
###############################################################################    
vzdalenost=np.asarray(vzdalenost)
delka=sum(vzdalenost)
vzdalenost_1=np.asarray(vzdalenost_1)
delka_1=sum(vzdalenost_1)
print("The length 0 is:", delka, "mm")
print("The length 1 is:", delka_1, "mm")
###############################################################################
#___________________interpolace experimentálních  splinem _____________________
###############################################################################
tck = interpolate.splrep(inter[:,0], inter[:,1], s=0)
tck_1 = interpolate.splrep(inter_1[:,0], inter_1[:,1], s=0)

ynew = interpolate.splev(inter[:,0], tck, der=0)
ynew_1 = interpolate.splev(inter_1[:,0], tck_1, der=0)
###############################################################################
#___________________________Normála____________________________________________
###############################################################################
yder = interpolate.splev(inter[:,0], tck, der=1)
uhel=np.arctan(yder)
k_n=np.tan((uhel + np.pi/2))    #pozor, v radiánech!

y_0=[]
#
#y_1=[]
#y_2=[]
b=[]
#for ii in range (0, len(inter), 1):
#    b_d=inter[ii][1]-k_n[ii]*inter[ii][0]
#    for iii in range (0, len(inter), 1):
#        y_d(iii)=k_n[ii]*inter_1[iii][0] + b_d    
#        y_0[iii][ii].append(y_d)
#    b.append(b_d)
#    
#y_0=np.asarray(y_0)
#b=np.asarray(b)
###############################################################################
#Vytvoření "matice", do kterých budou zaisovány hodnoty jednotlivých normál
###############################################################################
array1=[]
for j in range(len(inter)):
     temp=[]
     for i in range(len(inter)):
             temp.append(0)
     array1.append(temp)
array1
for ii in range (0, len(inter), 1):
    b_d=inter[ii][1]-k_n[ii]*inter[ii][0]
    b.append(b_d)
    for iii in range (0, len(inter), 1):
        y_d=k_n[ii]*inter_1[iii][0] + b_d
        array1[iii].append(y_d)
b=np.asarray(b)
array1=np.asarray(array1)
###############################################################################
#_________________________intersection of inner curve__________________________
###############################################################################
x1 = inter_1[:,0]
y1 = inter_1[:,1]
x2=inter_1[:,0]
x_inters=[]
y_inters=[]
for jj in range (0,len(inter), 1):
    y2=array1[:,len(inter) + jj]
    x,y=intersection(x1,y1,x2,y2)
    x_inters.append(x)
    y_inters.append(y)

###############################################################################
#____________________________MEAN THICKNESS____________________________________
###############################################################################
loc_thick=[]
for loc in range (0, len(inter), 1):
    loc_t=np.sqrt((inter[loc][0] - x_inters[loc])**2 + (inter[loc][1] - y_inters[loc])**2)
    loc_thick.append(loc_t)
loc_thick=np.asarray(loc_thick)
mean_thick = np.mean(loc_thick)
print("Mean thickness is", mean_thick, "mm")
###############################################################################
#_______________________________Result plot____________________________________
###############################################################################
fig, ax=plt.subplots()
ax.plot(inter[:,0],inter[:,1], 'x')
#ax.plot(inter_1[:,0],inter_1[:,1], 'rx')
ax.plot(inter[:,0],ynew, 'b-')
ax.plot(inter_1[:,0],ynew_1, 'r-')

for iiii in range (0,len(inter), 1): 
    ax.plot(inter_1[:,0],array1[:,iiii + len(inter)],"k:")

ax.plot(x_inters, y_inters, "*k")
plt.axis([0,(img_shape[1]*pixel_size),(img_shape[0]*pixel_size),0])
ax.set_xlabel("x axis length [mm]")
ax.set_ylabel("y axis length [mm]")
plt.show()


