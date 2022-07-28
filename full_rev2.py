# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 09:45:55 2020

@author: bursa
"""

# matplotlib.pyplot as plt
#matplotlib.use("TkAgg") #Tohle se dá nastavit i ručně ve Spyderu!
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
from tkinter import filedialog
import cv2 as cv2
from win32api import GetSystemMetrics, GetMonitorInfo, MonitorFromPoint
#import keyboard as kb
from intersection import *
from interparc import *
from scipy import interpolate
import math
#from scipy.interpolate import CubicSpline
#import AppKit

########################## Rozlišení monitoru #################################
monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
monitor_area = monitor_info.get("Monitor")
work_area = monitor_info.get("Work")
Taskbar_height = (monitor_area[3]-work_area[3])
Des_Width =GetSystemMetrics(0)
Des_Height =GetSystemMetrics(1)
#____________________________ MAc X OS_________________________________________
#a=[(screen.frame().size.width, screen.frame().size.height)
#    for screen in AppKit.NSScreen.screens()]

app_scale_x = 0.7
app_scale_y = 0.7
FrameWidth = Des_Width*app_scale_x
FrameHeight = Des_Height *app_scale_y
#FrameWidth = 1000
#FrameHeight = 600
Frame1_w = FrameWidth/3
Frame1_h = 2*FrameHeight/6
Frame2_w = FrameWidth/3
Frame2_h = 4*FrameHeight/6
Frame3_w = (2 * FrameWidth / 3)
Frame3_h = FrameHeight
Frame4_w = FrameWidth/3
Frame4_h = FrameHeight/6
bg_color="gray90"


############################### point click ###################################
#tohle musí být nadefinováno před class, kde ji používám!!
mouseX=[]
mouseY=[]
mouseX_1=[]
mouseY_1=[]
mouseX_2=[]
mouseY_2=[]
vzdalenost=[]
vzdalenost_1=[]
b=[]
array1=[]
y_0=[]
x_inters=[]
y_inters=[]
x_interss=[]
y_interss=[]
loc_thickness=[]
x_locT = []
y_locT = []

def draw_circle (event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(imCrop,(x,y),1,(0,0,255),-1)
        mouseX.append(x)
        mouseY.append(y)
        return mouseX, mouseY
def draw_circle_1 (event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(imCrop,(x,y),1,(255,0,0),-1)
        mouseX_1.append(x)
        mouseY_1.append(y)
        return mouseX_1, mouseY_1
def draw_circle_2 (event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(image_calibration,(x,y),1,(255,0,0),-1)
        mouseX_2.append(x)
        mouseY_2.append(y)
        return mouseX_2, mouseY_2
    
def SI_convert(mX, mY, mX_1, mY_1, r):
    """
    Nadefinování metody, která převádí získané body po kliknutích v pixelech 
    na normální jednotky, nejen SI, ale prostě na ty, ve kterých se zadá pixel
    size. Výstupem této metody jsou souřadnice vnitřního a vnějšího okraje """
#Převedení vůči globálním rozměrům, asi je to zbytečný krok, ale neva :D
    global locX, locY, locX_1, locY_1
    mX = mouseX     # když využívám jinou var, tak ji takhle zkopíruji a řeší toproblém s "refered before assignment"
    mY= mouseY
    mX_1 = mouseX_1
    mY_1 = mouseY_1
    roi = r
    mX=np.asarray(mX, dtype=float)
    mY=np.asarray(mY, dtype=float)
    mX_1=np.asarray(mX_1, dtype=float)
    mY_1=np.asarray(mY_1, dtype=float)
    locX=(mX+roi[0])*pixel_size
    locY=(mY+roi[1])*pixel_size
    locX_1=(mX_1+roi[0])*pixel_size
    locY_1=(mY_1+roi[1])*pixel_size
    return locX, locY, locX_1, locY_1
###############################################################################
#_____________________________Segment length___________________________________
###############################################################################
def SegLen (vzdalenost, vzdalenost_1):
    global len_out, len_inner
    
    len_0 = vzdalenost
    len_1 = vzdalenost_1
    len_0=np.asarray(len_0)
    len_out =sum (vzdalenost)
    len_1=np.asarray(len_1)
    len_inner = sum(vzdalenost_1)
    print("The length 0 is:", len_out, "mm")
    print("The length 1 is:", len_inner, "mm")

###############################################################################
#Vytvoření "matice", do kterých budou zaisovány hodnoty jednotlivých normál
###############################################################################
def NormalLines (newpoints, k_n):   
    global b_coef, arr1
    arr1 = array1
    b_coef = b
    for j in range(len(newpoints)):
        temp=[]
        for i in range(len(newpoints)):
            temp.append(0)
        arr1.append(temp)
    #array1
    for ii in range (0, len(newpoints), 1):
        b_d=(newpoints[ii][1])-(k_n[ii])*(newpoints[ii][0])
        b_coef.append(b_d)
        for iii in range (0, len(newpoints), 1):
            y_d=k_n[ii]*newpoints_1[iii][0] + b_coef[ii]   
            arr1[iii].append(y_d)
    b_coef=np.asarray(b_coef)
    arr1=np.asarray(arr1)
    return 
###############################################################################
#_________________________intersection of inner curve__________________________
###############################################################################
def Extract(lst): 
    """Tahle funkce extrahuje jenom první elementy ze seznamů arrays (problém u intersection
když jich je více """
    return [item[0] for item in lst] 

def find_nearest(array, value):
    """ Tahle funkce pomáhá najít nejbližší element z vloženého array. Je to z důvodu
    více průsečíku u x_inters, y_inters. Pomocí Exact je možné získat hodnotu na určité 
    pozici, ale řazení průsečíků je s rostoucím x """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def innerIntersection (newpoints_1, arr1, newpoints):
    """ Tahle funkce využívá funkci intersection, která ovšem potřebuje, aby dvě
    například funkce měli stejnou délku. První funkce je vnitřní obvod křivky a
    druhou funkcí jsou normály, kde y souřadnice byla prvně vložena do arr1.
    Celé je to o délce vnitřního průměru"""
    global x_interss, y_interss, x_inters, Y_inters, x_locT, y_locT
    x1 = newpoints_1[:,0]
    y1 = newpoints_1[:,1]
    x2=newpoints_1[:,0]
    for jj in range (0,len(newpoints), 1):
        y2=arr1[:,len(newpoints) + jj]
        x,y=intersection(x1,y1,x2,y2)
        x_inters.append(x)
        y_inters.append(y)
    #x_inters = Extract_inters)
    #y_inters = Extract(y_inters)
    for jjj in range (0,len(x_inters),1):
        if len(x_inters[jjj])>0:
            x_new_inters = find_nearest(x_inters[jjj], newpoints[jjj][0]) 
            x_interss.append(x_new_inters)
            x_locT.append(newpoints[jjj][0])
        if len(y_inters[jjj])>0:
            y_new_inters = find_nearest(y_inters[jjj], newpoints[jjj][1])
            y_interss.append(y_new_inters)
            y_locT.append(newpoints[jjj][1])
###############################################################################
#____________________________MEAN THICKNESS____________________________________
###############################################################################
def MeanThickness (x_locT, y_locT, x_interss, y_interss):
    """ Tato funkce určuje průměrnou tloušťku segmentovného vzorku. Bere v potaz
    pouze elementy, které mají sůj průsečík"""
    global mean_thick, loc_thickness
    #loc_thickness = loc_thick
    for loc in range (0, len(x_locT), 1):
        loc_t=np.sqrt((x_locT[loc] - x_interss[loc])**2 + (y_locT[loc] - y_interss[loc])**2)
        """ Přidaná podmínka, když tam není více průsečíků, ale první je na špatném
        místě (není zde soused pro tloušťku, tak to projde až dále) """
        if loc_t < 6:
            loc_thickness.append(loc_t)
        #loc_thickness=np.asarray(loc_thickness)
    mean_thick = np.nanmean(loc_thickness)
    print("Mean thickness is", mean_thick, "mm")
###############################################################################
#___________________________ OPENING ANGL E____________________________________
###############################################################################
def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))
def length(v):
    return math.sqrt(dotproduct(v, v))
def angle(v1, v2):
    return math.degrees(math.acos(dotproduct(v1, v2) / (length(v1) * length(v2))))
 
class Window(Frame):    #Frame je funkce z tkinteru
    """ Tahle třída odpovídá celému úvodnímu oknu aplikace. V rámci aplikace jsou
    definovány jednotlivé frame, do kterých jsou vkládány jednotlivé metody."""
###################### Definice inicializačního okna ##########################
    def __init__(self, master= None):
        """ Úvodní metoda, která vždy inicializuje vytvožení základního Frame s
        mřížkou. Jsou zde nastaveny také váhy jednotlivých řádků  a sloupců,
        ale to je možná zbytečné. Vždy při inicializaci je zavoláno init_window
        metoda, která vytvoří prvotní rozřazení aplikace"""
        Frame.__init__(self, master)
        #super().__init__(master)
        self.grid()
        for c in range(10):
            self.master.rowconfigure(c, weight=1)
        for r in range(10):
            self.master.columnconfigure(r, weight=1)
            
        self.master.resizable(0,0)
        self.init_window()  #zavolání init_window methody
        
########################## Definice hlavního okna #############################
    def init_window(self):
        """ Nastavení layoutu aplikace a vložení jednotlivých widgets s určitou
        metodou uvnitř"""
        global chkValue_2
        #Rozložení okna pomocí různých Frame, do kterých budou vkládány data               
        self.Frame1=LabelFrame(self, width = Frame1_w, height = Frame1_h , text="Control", font = 12, bg=bg_color)
        self.Frame1.grid(row = 0, column = 0, sticky=N)
        self.Frame2= Frame (self, width= Frame2_w, height= Frame2_h, bd = 0, bg=bg_color)
        self.Frame2.grid(row = 0, column = 0, sticky= S)
        self.Frame3 = Frame (self, width= Frame3_w, height= Frame3_h, bd = 0)
        self.Frame3.grid(row = 0, column = 1,sticky=(N, W))
        self.Frame4 = LabelFrame (self, width= Frame4_w, height= Frame4_h, text = "Results", font = 12, bg=bg_color)
        self.Frame4.grid(row = 0, column = 0, sticky=S)                
        #změna názvu našeho "master" okna
        self.master.title("Opening angle")        
############################# Vytvoření tlačíka ###############################    
        #vytvoření "quit" tlačítka
        #quitB = Button(self, text = "Quit", command = self.exit_window)
        #quitB.place(x= 0, y=0)
        
################################# Menu lišta ##################################        
        #vytvoření menu lišty
        menu = Menu(self.master)
        self.master.config(menu = menu)
        #Přidání "File" do našeho menu, Tohle musím udělat pro každou záložku v menu liště
        file=Menu(menu)
        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        file.add_command(label="Exit", command=self.exit_window)
        #added "file" to our menu
        menu.add_cascade(label="File", menu= file)
        edit=Menu(menu) #vytvoření zásložky v části menu
        edit.add_command(label="Undo") #přidání funkce "Undo" do mé nové záložky
        menu.add_cascade(label="Edit", menu = edit) #přidání vytvořené záložky "Edit" do mého menu

###############################   Import image    #############################
        self.ImImport = Button(self.Frame1, text = "Upload image", command = self.importImage, bd=0, highlightbackground=bg_color)
        self.ImImport.place(x= (FrameWidth/3) * 0.05, y=0)
########################## Nastavení velikosti pixelu #########################
        self.chkValue_1 = BooleanVar() 
        self.chkValue_1.set(False)
        self.Basler = Checkbutton (self.Frame1, text = "Image from Basler camera", var=self.chkValue_1, command = self.pixelSize, bd=0, bg=bg_color)
        self.Basler.place(x= ((FrameWidth/3) * 0.05), y=(FrameHeight/2) * 0.11)
###############################   calibration     #############################
        self.Calibration = Button(self.Frame1, text = "Calibration", command = self.calibration, bd=0, highlightbackground=bg_color)
        self.Calibration.place(x= (FrameWidth/3) - 100, y=0)        
        #self.PixEntry = Entry(self.Frame1, text = "Pixel size", width = 5)
        #self.PixEntry.place(x= ((FrameWidth/3) * 0.05) + 70, y=(FrameHeight/2) * 0.11)
        #self.Pix = Label (self.Frame1, text = "Pixel size:", bg = "red")
        #self.Pix.place (x = (FrameWidth/3) * 0.05, y=(FrameHeight/2) * 0.1)
        #self.OkButt = Button (self.Frame1, text = "OK", command = self.pixelSize)
        #self.OkButt.place(x= (FrameWidth/3) * 0.5, y=(FrameHeight/2) * 0.1)
############################### Vykreslení grafu###############################
        self.ROIButt = Button(self.Frame1, text = "Select boundary", command = self.ROI_select, bd=0, highlightbackground=bg_color)
        self.ROIButt.place(x=(FrameWidth/3) * 0.05, y=(FrameHeight/2) * 0.2)
############################### Vykreslení grafu ###############################
        self.DrawResults = Button(self.Frame1, text = "Draw results", command = self.DrawResults, bd=0, highlightbackground=bg_color)
        self.DrawResults.place(x=(FrameWidth/3) * 0.05, y=(FrameHeight/2) * 0.5)
####################### Number of equidistant points ##########################
        self.PointEntry = Entry(self.Frame1, width = 5, bd=0, highlightbackground=bg_color)
        self.PointEntry.place(x= ((FrameWidth/3) * 0.05) + 120, y=(FrameHeight/2) * 0.3)
        self.Point = Label (self.Frame1, text = "Number of Points:", bd=0, bg=bg_color)
        self.Point.place (x = (FrameWidth/3) * 0.05, y=(FrameHeight/2) * 0.3)
        self.OkButt_1 = Button (self.Frame1, text = "OK", command = self.NumberPoint, bd=0, highlightbackground=bg_color)
        self.OkButt_1.place(x= ((FrameWidth/3) * 0.05) + 180, y=(FrameHeight/2) * 0.3)  
############################## Full circle + cutted ###########################
        self.chkValue_2 = BooleanVar() 
        self.chkValue_2.set(False)
        self.Cutted = Checkbutton (self.Frame1, text = "Cutted ring", var=self.chkValue_2, command = self.CuttedRing, bd=0, bg=bg_color)
        self.Cutted.place(x= ((FrameWidth/3) * 0.05), y=(FrameHeight/2) * 0.4)
        self.chkValue_3 = BooleanVar() 
        self.chkValue_3.set(False)        
        self.Cutted = Checkbutton (self.Frame1, text = "Full ring", var=self.chkValue_3, command = self.FullRing, bd=0, bg=bg_color)
        self.Cutted.place(x= ((FrameWidth/3) * 0.5), y=(FrameHeight/2) * 0.4)
################################## Výsledeky ################################## 
        self.OutLenRes = Text(self.Frame4, bd=0, width = int(Frame4_h/4.5), height = 1, highlightbackground=bg_color, bg=bg_color)
        self.OutLenRes.place(x=Frame4_w * 0, y=Frame4_h * 0) 
        self.InnerLenRes = Text(self.Frame4, bd=0, width = int(Frame4_h/4.5), height = 1, highlightbackground=bg_color, bg=bg_color)
        self.InnerLenRes.place(x=Frame4_w * 0, y=Frame4_h * 0.2)
        self.OutRadRes= Text(self.Frame4, bd=0, width = int(Frame4_h/4.5), height = 1, highlightbackground=bg_color, bg=bg_color)
        self.OutRadRes.place(x=Frame4_w * 0, y=Frame4_h * 0.4)        
        self.InnerRadRes= Text(self.Frame4, bd=0, width = int(Frame4_h/4.5), height = 1, highlightbackground=bg_color, bg=bg_color)
        self.InnerRadRes.place(x=Frame4_w * 0, y=Frame4_h * 0.6)
        self.ThickRes= Text(self.Frame4, bd=0, width = int(Frame4_h/4.5), height = 1, highlightbackground=bg_color, bg=bg_color)
        self.ThickRes.place(x=Frame4_w * 0.5, y=Frame4_h * 0)
        self.AngleRes= Text(self.Frame4, bd=0, width = int(Frame4_h/4.5), height = 1, highlightbackground=bg_color, bg=bg_color)
        self.AngleRes.place(x=Frame4_w * 0.5, y=Frame4_h * 0.2)
        
###############################################################################
#_________________________ Hlavní definice bodů tepny  ________________________
###############################################################################
############################## calibration ####################################
    def calibration(self, *args):
        """ KAlibrační metoda, když bych například měl snímky z jiného zařízení.
        Jinak stačí zvolit, že se jedná o naši BASLER kameru, kde to bude nastaveno
        defaultně, jen někdy to pro jistotu můžeme předefinovat"""
        global image_calibration, pixel_size
        path_calib = filedialog.askopenfilename(title='Please select a directory')
        if len(path_calib) > 0:
            image_calibration = cv2.imread(path_calib)
        img_shape = image_calibration.shape
        cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
#        cv2.setMouseCallback('Calibration', draw_circle_2)
        cv2.imshow("Calibration", image_calibration)
        #cv2.waitKey(0)
        cv2.destroyWindow("Calibration")
        cv2.namedWindow("calibration", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('calibration', draw_circle_2)
        while(1):
            cv2.imshow('calibration',image_calibration)
            k = cv2.waitKey(20) & 0xFF
            if k == 27: #ESC to EXIT window
                cv2.destroyWindow("calibration")
                break
                
        dist_cal = np.sqrt((mouseX_2[0] - mouseX_2[1] )**2 +(mouseY_2[0] -mouseY_2[1] )**2)
        object_len = 1 #mm
        new_pix = object_len / dist_cal #object je to u čeho znám délku, musím zadat!
        pixel_size = new_pix
        print (dist_cal)
        print (new_pix)
        return pixel_size
############################## image import ###################################
    def importImage (self, *arg):
        """ Vložení základního obrázku, který bude využit pro ROI a nastavení 
        vnějšího a vnitřního okraje """
        global path
#        path = filedialog.askopenfilename(parent=root,initialdir="/",title='Please select a directory')
        path = filedialog.askopenfilename(title='Please select a directory')
        load = Image.open(path)
        load = load.resize((int(Frame2_w), int(Frame2_h- 80)), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        #labels can be text or images
        img = Label(self.Frame2, image = render, borderwidth = 0)
        img.Image= render
        img.place(x=0, y=0)
# V případě, kdy budou metadata i DPI info, z BASLERU to nemáme
        #dpi = load.info["dpi"]
        #Pixel_mm = 25.4/(dpi[0])
        #print(Pixel_mm)
        return path
########################### Entry pixel value #################################
    def pixelSize (self):
        """ Pixel size je nutné nastavit, když mám snímky z BASLER. JEdnou za čas
        překalibrovat snímek z BASLER. Při kalibraci je důležité, aby marker ležel
        v místě, kde snímkuji. Když jsem měl hist. sklíčko pod tím trochu, tak tam
        je lehce odklon. Rozměr je ručně trochu posunut. 0.033 je ok pro konec plastové
        tyčinky, takže to příště nalepit co nejvíce srovnané s horním okrajem!!!"""
        global pixel_size
        pixel_size = 0.0325
        #defaultně nastavená hodnota
        #pixel_size = 0.032
        #pixel = self.PixEntry.get()
        #pixel_size = float(pixel) * calibration    #calibration je přepočet s ohledem na vzdálenost!
        print ("nečum")
        return pixel_size
########################### Entry pixel value #################################
    def CuttedRing (self):
        """ PNAstaví parametr pro spline, aby nespojoval konce"""
        global ringShape
        ringShape = 0
        return pixel_size
########################### Entry pixel value #################################
    def FullRing (self):
        """ Nastaví parametr pro spline, aby to bylo uzavřeno"""
        global ringShape
        ringShape=1
        return pixel_size
########################### Entry pixel value #################################
    def NumberPoint (self):
        """ Metoda, která mi nastaví globální proměnou odpovídající počtu budů 
        pro intepolaci"""
        global NumPoints 
        Points = self.PointEntry.get()
        NumPoints = int(Points)
        return NumPoints
###############################################################################
#________________________ Nahrání originálního obrázku ________________________
##############################################################################
    def ROI_select (*args):
        """ Metoda využívající opencv pro výběr vnějšího a vnitřního obvodu pomocí
        naklikávání okraje. Body nemusí být rozloženy rovnoměrně, ale v případě
        větší křivosti je potřeba toto místo zaznamenat"""
        global img_shape, image, imCrop, crop_shape, r        
        if len(path) > 0:
            image = cv2.imread(path)
        img_shape = image.shape
        cv2.namedWindow("Original image", cv2.WINDOW_NORMAL)
        cv2.imshow("Original image", image)
        #cv2.waitKey(0)    #Když to není, tak se to hned vypne. Nemusím tak zbytečně rozbrazovat origo pro potvrzení
###############################################################################
#_____________________ výběr ROI z originálního obrázku _______________________
###############################################################################
        cv2.namedWindow("Select ROI", cv2.WINDOW_NORMAL)
        cv2.destroyWindow("Original image")
        r= cv2.selectROI("Select ROI",image, fromCenter=False)
        imCrop = image[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        cv2.namedWindow("Your choosen ROI", cv2.WINDOW_NORMAL)
        crop_shape=imCrop.shape
        cv2.destroyWindow("Select ROI")
        cv2.imshow("Your choosen ROI", imCrop)
        #cv2.waitKey(0)
        cv2.destroyWindow("Your choosen ROI")
        cv2.namedWindow("Outer boundary", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Outer boundary', draw_circle)
        while(1):
            cv2.imshow('Outer boundary',imCrop)
            k = cv2.waitKey(20) & 0xFF
            if k == 27: #ESC to EXIT window
                break
#_____________po zmáčknutí a mohu naklikat druhou křivku_______________________
            elif k == 32:   #32 odpovídá mezerníku, ENTER nemá unikátní číslo.. lze využít ord("a"), například
                cv2.destroyAllWindows()#
                cv2.namedWindow("Outer boundary", cv2.WINDOW_NORMAL)
                cv2.imshow('Outer boundary',imCrop)#
                cv2.setMouseCallback('Outer boundary',draw_circle_1) #přiřazení funkce k oknu#
        cv2.destroyAllWindows()
        return        
                
########################### Provedení inrerpolace bodů ########################

########################### Definice nahrání grafu ############################
    def DrawResults (self):
        """ Metoda DrawResult nedělá poue vykreslení grafu, ale také bere do sebe
        ostaní metody, které postupně upravují data, zíkaná z naklikaných bodů """
        
        global curv_outer, curv_inner
        global inter, inter_1, DPI, newpoints, newpoints_1, yder, k_n, xp, yp, loc_out_radius, opening_angle, v1, v2
        # použití funkce SI_converter, která má za výstup souřadnice na ty dané body v daných jednotkách (dáno pixel pize)
        SI_convert(mouseX, mouseY, mouseX_1, mouseY_1, r)   #převedení na SI
        inter=interparc(NumPoints,locX,locY,'linear')  #interpolace na equidistant points
        inter_1=interparc(NumPoints,locX_1,locY_1,'linear')    
        for i in range (1,len(inter),1):
            datax=inter[i][0]-inter[i-1][0]
            datay=inter[i][1]-inter[i-1][1]
            data=np.sqrt(datax**2 + datay**2)
            vzdalenost.append(data)
            datax_1=inter_1[i][0]-inter_1[i-1][0]
            datay_1=inter_1[i][1]-inter_1[i-1][1]
            data_1=np.sqrt(datax_1**2 + datay_1**2)
            vzdalenost_1.append(data_1) 
        SegLen (vzdalenost, vzdalenost_1)   # určení délky segmentů
###############################################################################
#___________________interpolace experimentálních  splinem _____________________
##############################################################################
        #PARAMETR S SE MUSÍ ROVNAT jedničce! JINAK JE MOC VELKÉ VYHLAZENÍ A NEODPOVÍDÁ TO TVARU!!
        tck,u= interpolate.splprep([inter[:,0], inter[:,1]], s=1, u=None, per = ringShape)
        tck_1,u_1= interpolate.splprep([inter_1[:,0], inter_1[:,1]], s=1, u=None, per = ringShape)
        """Parametr s u splprep určuje, zda je spline uzavřený, nebo ne. Takže 
        v případě, kdy budu interpolovat kruh, tak mohu dát s=1 a mělo by se to uzavřít."""
        #ynew = interpolate.splev(inter[:,0], tck, der=0)
        #ynew_1 = interpolate.splev(inter_1[:,0], tck_1, der=0)
        newpoints =np.transpose(np.asarray(interpolate.splev(u, tck)))
        newpoints_1 =np.transpose(np.asarray(interpolate.splev(u_1, tck_1)))
#____ derivace interpolovaného splinu pro určení tečny a následně normály _____     
        """Tady pozor na vyjádření derivace. Tím, že používám splprep, tak mám B-spline 
        N-dimensional, takže mi to hodí diferenciál pro každou osu. JEstliže chci tečnu,
        tak musím ještě provést výpočet dy,dx. Stejný problém bude i u křivosti."""
        dx,dy = interpolate.splev(u, tck, der=1) 
        dx_1,dy_1 = interpolate.splev(u_1, tck_1, der=1) 
        derivative = dy/dx
        uhel=np.arctan(derivative)
        k_n=np.tan((uhel + np.pi/2))    #pozor, v radiánech!
#________ úprava záskaných dat pomocí metod nadefinovaných mimo class _________
        NormalLines (newpoints, k_n)
        innerIntersection (newpoints_1, arr1, newpoints)
        MeanThickness (x_locT, y_locT, x_interss, y_interss)
###############################################################################       
#################### Druhá derivace + křivost + poloměr #######################
###############################################################################           
        dxx, dyy = interpolate.splev(u, tck, der=2)
        dxx_1, dyy_1 = interpolate.splev(u_1, tck_1, der=2)
        curv_outer = np.abs(dx* dyy - dy* dxx) / np.power(dx** 2 + dy** 2, 3 / 2)
        curv_inner = np.abs(dx_1* dyy_1 - dy_1* dxx_1) / np.power(dx_1** 2 + dy_1** 2, 3 / 2)
        curv_outer_mean = np.mean(curv_outer)
        curv_inner_mean = np.mean(curv_inner)
        print("mean_curv_out", curv_outer_mean, "mean_curv_inner", curv_inner_mean)
#_________________ určení lokálního rádiusu, což odpovídá 1/k _________________
        loc_out_radius =1/curv_outer
        loc_in_radius = 1/curv_inner
        mean_out_radius = np.mean(loc_out_radius)
        mean_in_radius = np.mean(loc_in_radius)
        print("menaOutRadius",mean_out_radius, "menaInRadius", mean_in_radius) 
###############################################################################       
############################## opening angle ##################################
############################################################################### 
        if ringShape == 0:
            v1 = newpoints_1[0] - newpoints_1[round((NumPoints-1)/2)] 
            v2 = newpoints_1[round(NumPoints-1)] - newpoints_1[round((NumPoints-1)/2)] 
            opening_angle = angle(v1,v2)
    
###############################################################################       
###################### Nastavení vykreslení výsledků ##########################
###############################################################################
#Rozměry to určuje nesprávně, takže je to stejně potřeba nastavit ručně...
#Tyto výpočty jsou jen bokovka, nemají význam!!!  
        screen_DPI = 156
        Pixel_mm = 25.4/screen_DPI
        Pixel_in = Pixel_mm / 25.4
#Rozměry obrázku je potřeba naladit na určitý zařízení!!
        fig = Figure(figsize=((Frame3_w)* Pixel_in,(Frame3_h - 35 )*Pixel_in), dpi=156)
        ax = fig.add_subplot(111) 
        fig.subplots_adjust(wspace=0.6, hspace=0.6, left=0.15, bottom=0.22, right=0.96, top=0.96)
        ax.plot(newpoints[:,0],newpoints[:,1], 'x')
        ax.plot(newpoints_1[:,0],newpoints_1[:,1], 'rx')
        # interpolace splinem
        ax.plot(newpoints[:,0],newpoints[:,1], 'b-')
        ax.plot(newpoints_1[:,0],newpoints_1[:,1], 'r-')
        
        # for iiii in range (0,len(newpoints[:,0]), 1): 
        #     ax.plot(newpoints_1[:,0],arr1[:,iiii + len(newpoints)],"k:")
        ax.plot((newpoints_1[0][0], newpoints_1[round((NumPoints-1)/2)][0]), (newpoints_1[0][1],newpoints_1[round((NumPoints-1)/2)][1]), "g:")
        ax.plot((newpoints_1[round(NumPoints-1)][0], newpoints_1[round((NumPoints-1)/2)][0]), (newpoints_1[round(NumPoints-1)][1], newpoints_1[round((NumPoints-1)/2)][1]), "g:")
        ax.plot(x_interss, y_interss, "*k")
        ax.axis([0,(img_shape[1]*pixel_size),(img_shape[0]*pixel_size),0])
        ax.set_xlabel("x axis length [mm]")
        ax.set_ylabel("y axis length [mm]")
        canvas = FigureCanvasTkAgg(fig, self.Frame3)
        canvas.get_tk_widget().pack(side = TOP, fill = NONE, expand = 1)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, self.Frame3)
        toolbar.update()
        canvas._tkcanvas.pack(side=BOTTOM, fill=NONE, expand=1)
        
###############################################################################       
######################## Nastavení vypsání výsledků ###########################
###############################################################################          
        self.OutLenRes.insert(END,("Outer length=","%.2f" % len_out))
        self.InnerLenRes.insert(END, ("Inner length=","%.2f" % len_inner))
        self.OutRadRes.insert(END, ("Outer radius=","%.2f" % mean_out_radius))
        self.InnerRadRes.insert(END, ("Inner radius=","%.2f" % mean_in_radius))
        self.ThickRes.insert(END, ("Mean thickness=","%.2f" % mean_thick))
        if ringShape == 0:
            self.AngleRes.insert(END, ("Opening angle:","%.2f" % opening_angle))
        
        return 
####################### Definice funkce ukončení okna #########################
    # definice metody "exit_window", na kterou se odkazujeme při stisknutí tlačístka "quit" pomocí příkazu "command"
    def exit_window (self):
        #sys.exit()  #Zde je blbé, že iPython automaticky killne i kernel
        root.quit()     # stops mainloop
        root.destroy()

#root= Tk()
root = Toplevel()   # původně zde bylo Tk(), ale kvůli zobrazení obrázku tam musí být tohle
root.geometry("%dx%d+0+0" % (FrameWidth, FrameHeight))    #Takhle jsem schopen vložit něco do string!
app = Window(root)
root.config(bg="skyblue")
root.mainloop()


