# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 09:45:55 2020

@author: bursa
"""

import matplotlib
matplotlib.use("TkAgg") #Tohle se dá nastavit i ručně ve Spyderu!
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
#from matplotlib import pyplot as plt
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
from tkinter import filedialog
import cv2
from win32api import GetSystemMetrics, GetMonitorInfo, MonitorFromPoint

########################## Rozlišení monitoru #################################
monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
monitor_area = monitor_info.get("Monitor")
work_area = monitor_info.get("Work")
Taskbar_height = (monitor_area[3]-work_area[3])
Des_Width =GetSystemMetrics(0)
Des_Height =GetSystemMetrics(1) - 100

FrameWidth = Des_Width/3
FrameHeight = Des_Height/2

x= np.array([0,1,2,3,4,5,6,7,8,9,10])
y= np.array([0,1,2,3,4,5,6,7,8,9,10])

class Window(Frame):    #Frame je funkce z tkinteru
    
###################### Definice inicializačního okna ##########################
    def __init__(self, master= None):
        Frame.__init__(self, master)
        #super().__init__(master)
        self.grid()
        #for c in range(10):
        #    self.master.rowconfigure(c, weight=1)
        #for r in range(10):
        #    self.master.columnconfigure(r, weight=1)
            
        self.master.resizable(0,0)
        self.init_window()  #zavolání init_window methody
        
########################## Definice hlavního okna #############################
    def init_window(self):
        #Rozložení okna pomocí různých Frame, do kterých budou vkládány data       
        #self.Frame1=Frame(self, width=Des_Width/3, height=Des_Height/2, bg="red")
        #self.Frame1.grid(row = 0, column = 0, sticky="N")
        #self.Frame2 = Frame (self, width=2 * Des_Width/3, height=2*Des_Height/3, bg="blue")
        #self.Frame2.grid(row = 0, column = 1,rowspan=4, columnspan=2, sticky=N)
        #self.Frame3 = Frame (self, width=Des_Width/3, height=Des_Height/2, bg="green")
        #self.Frame3.grid(row = 2, column = 0, sticky=S)
        
        #self.Frame4 = Frame (self, width=Des_Width/3, height=Des_Height/3, bg="purple")
        #self.Frame4.grid(row = 3, column = 2, sticky=SW)
        #self.Frame5 = Frame (self, width=Des_Width/3, height=Des_Height/3, bg="black")
        #self.Frame5.grid(row = 3, column = 2, sticky=(N, S, W, E))
        
        self.Frame1=Frame(self, width = FrameWidth/3, height = FrameHeight,bg="red")
        self.Frame1.grid(row = 0, column = 0, sticky=(N, S, W, E))
        self.Frame2 = Frame (self, width= 2 * FrameWidth/3, height=FrameHeight, bg="blue")
        self.Frame2.grid(row = 0, column = 1, sticky=(N, S, W, E))            
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
        self.ImImport = Button(self.Frame1, text = "Nahrát snímek", command = self.importImage)
        self.ImImport.place(x= (FrameWidth/3) * 0.1, y=(FrameHeight/2) * 0.1)
###########################Přidání obrázku po kliknutí#########################
        self.PixEntry = Entry(self.Frame1, text = "Pixel size", width = 5)
        self.PixEntry.place(x= (FrameWidth/3) * 0.1, y=(FrameHeight/2) * 0.3)
        self.OkButt = Button (self.Frame1, text = "OK", command = self.pixelSize)
        self.OkButt.place(x= (FrameWidth/3) * 0.5, y=(FrameHeight/2) * 0.3)
        
############################### Vykreslení grafu###############################
        self.GraphButt = Button(self.Frame2, text = "Vykresli graf", command = self.drawGraph)
        self.GraphButt.place(x=1, y=1)

########################### Definice nahrání obrázku ##########################
    def openImage (self):
        load = Image.open("bla.png")
        render = ImageTk.PhotoImage(load)
        #labels can be text or images
        img = Label(self.Frame3, image = render)
        img.Image= render
        img.place(x=0, y=0)

########################### Entry pixel value #################################
    def pixelSize (self):
        global pixel 
        pixel = self.PixEntry.get()
        
########################### Definice nahrání grafu ############################
    def drawGraph (self):
        f = Figure(figsize=(1,1), dpi=100)
        a = f.add_subplot(111)  
        a.plot(x,y) #zatím to mám jen v pozadí (chybí plt.show), což u tkinteru nejde!
        canvas = FigureCanvasTkAgg(f, self.Frame2)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand= True)
        
        toolbar = NavigationToolbar2Tk(canvas, self.Frame2)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)
############################## image import ###################################
    def importImage (self):
        path = filedialog.askopenfilename()
        if len(path) >0:
            image= cv2.imread(path)
        #zobrazení obrázku s názvem Image
        #cv2.imshow("Image", image)
        #Zvolená klávesa, než se bude v kódu pokračovat (jakákoliv)
        #cv2.waitKey(0)

####################### Definice funkce ukončení okna #########################
    # definice metody "exit_window", na kterou se odkazujeme při stisknutí tlačístka "quit" pomocí příkazu "command"
    def exit_window (self):
        sys.exit()  #Zde je blbé, že iPython automaticky killne i kernel
        

#root= Tk()
root = Toplevel()   # původně zde bylo Tk(), ale kvůli zobrazení obrázku tam musí být tohle
root.geometry("%dx%d+0+0" % (FrameWidth, FrameHeight))    #Takhle jsem schopen vložit něco do string!
app = Window(root)
root.config(bg="skyblue")
root.mainloop()


