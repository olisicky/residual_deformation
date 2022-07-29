# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 09:45:55 2020

@author: Ondřej Lisický
"""

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
from tkinter import filedialog
import cv2 as cv2
# from win32api import GetSystemMetrics, GetMonitorInfo, MonitorFromPoint
from scipy import interpolate
import math
from pathlib import Path
import json

from intersection import *
from interparc import *

# get monitor size Win
# monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
# monitor_area = monitor_info.get("Monitor")
# work_area = monitor_info.get("Work")
# taskbar_height = (monitor_area[3] - work_area[3])
# desctop_width = GetSystemMetrics(0)
# desctop_height = GetSystemMetrics(1)

# get monitor site MACOS
#a=[(screen.frame().size.width, screen.frame().size.height)
#    for screen in AppKit.NSScreen.screens()]

# default scaling for the app

# frame_width = desctop_width * app_scale_x
# frame_height = desctop_height * app_scale_y

frame_width = 1000
frame_height = 600

mouseX, mouseY, mouseX_1, mouseY_1, mouseX_2, mouseY_2 = [[] for _ in range(6)]


def draw_circle(event, x, y, flag, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(imCrop, (x, y), 3, (0, 0, 255), -1)
        mouseX.append(x)
        mouseY.append(y)


def draw_circle_1(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(imCrop, (x, y), 3, (255, 0, 0), -1)
        mouseX_1.append(x)
        mouseY_1.append(y)
        return 10


def draw_circle_2(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(image_calibration, (x, y), 3, (255, 0, 0), -1)
        mouseX_2.append(x)
        mouseY_2.append(y)


def segment_len(vzdalenost, vzdalenost_1):
    ''' Get full length of boundaries. '''
    len_out = sum(vzdalenost)
    len_inner = sum(vzdalenost_1)
    return len_out, len_inner


def normal_lines(newpoints, newpoints_1, k_n):   
    ''' This creates only arrays for the points. It is probably too complicated but I do not want to reqork it now. '''
    arr1 = []
    b_coef = []
    for point in range(len(newpoints)):
        temp = []
        for i in range(len(newpoints)):
            temp.append(0)
        arr1.append(temp)
    for ii in range(len(newpoints)):
        b_d = (newpoints[ii][1]) - (k_n[ii]) * (newpoints[ii][0])
        b_coef.append(b_d)
        for iii in range(0, len(newpoints), 1):
            y_d = k_n[ii] * newpoints_1[iii][0] + b_coef[ii]
            arr1[iii].append(y_d)
    return np.asarray(b_coef), np.asarray(arr1)


def Extract(lst):
    """Tahle funkce extrahuje jenom první elementy ze seznamů arrays (problém u intersection
    když jich je více """
    return [item[0] for item in lst]


def find_nearest(array, value):
    """ Tahle funkce pomáhá najít nejbližší element z vloženého array. Je to z důvodu
    více průsečíku u x_inters, y_inters. Pomocí Exact je možné získat hodnotu na určité 
    pozici, ale řazení průsečíků je s rostoucím x """
    input_array = np.asarray(array)
    idx = (np.abs(np.asarray(array) - value)).argmin()
    return input_array[idx]


def innerIntersection(newpoints_1, arr1, newpoints):
    """ Tahle funkce využívá funkci intersection, která ovšem potřebuje, aby dvě
    například funkce měli stejnou délku. První funkce je vnitřní obvod křivky a
    druhou funkcí jsou normály, kde y souřadnice byla prvně vložena do arr1.
    Celé je to o délce vnitřního průměru. """
    x_inters, x_interss, y_inters, y_interss, x_locT, y_locT = [[] for _ in range(6)]
    x1 = newpoints_1[:, 0]
    y1 = newpoints_1[:, 1]
    x2 = newpoints_1[:, 0]
    for jj in range(len(newpoints)):
        y2 = arr1[:, len(newpoints) + jj]
        x, y = intersection(x1, y1, x2, y2)
        x_inters.append(x)
        y_inters.append(y)
    # x_inters = Extract_inters)
    # y_inters = Extract(y_inters)
    for jjj in range(len(x_inters)):
        if len(x_inters[jjj]) > 0:
            x_new_inters = find_nearest(x_inters[jjj], newpoints[jjj][0])
            x_interss.append(x_new_inters)
            x_locT.append(newpoints[jjj][0])
        if len(y_inters[jjj]) > 0:
            y_new_inters = find_nearest(y_inters[jjj], newpoints[jjj][1])
            y_interss.append(y_new_inters)
            y_locT.append(newpoints[jjj][1])
    return x_inters, x_interss, y_inters, y_interss, x_locT, y_locT


def mean_thickness(x_thicknesses, y_thicknesses, x_points, y_points):
    """ Tato funkce určuje průměrnou tloušťku segmentovného vzorku. Bere v potaz
    pouze elementy, které mají sůj průsečík"""
    loc_thickness = []
    for loc in range(len(x_thicknesses)):
        loc_t = np.sqrt((x_thicknesses[loc] - x_points[loc])**2 + (y_thicknesses[loc] - y_points[loc])**2)
        if loc_t < 6:    # limit thickness if there are more intersections
            loc_thickness.append(loc_t)
    mean_thick = np.nanmean(loc_thickness)
    return mean_thick


def dotproduct(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))


def length(v):
    return math.sqrt(dotproduct(v, v))


def angle(v1, v2):
    return math.degrees(math.acos(dotproduct(v1, v2) / (length(v1) * length(v2))))


class Window(Frame): 
    """ Tahle třída odpovídá celému úvodnímu oknu aplikace. V rámci aplikace jsou
    definovány jednotlivé frame, ve kterých jsou využívány jednotlivé funkce."""

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        for c in range(10):
            self.master.rowconfigure(c, weight=1)
        for r in range(10):
            self.master.columnconfigure(r, weight=1)
        self.master.resizable(0, 0)
        self.bg_color = "gray90"
        self.pixel_size = 0.0325
        self.app_scale_x = 0.7
        self.app_scale_y = 0.7
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame1_w = self.frame_width / 3
        self.frame1_h = 2 * self.frame_height / 6
        self.frame2_w = self.frame_width / 3
        self.frame2_h = 4 * self.frame_height / 6
        self.frame3_w = (2 * self.frame_width / 3)
        self.frame3_h = self.frame_height
        self.frame4_w = self.frame_width / 3
        self.frame4_h = self.frame_height / 6
        self.len_out = None
        self.len_inner = None
        self.mean_out_radius = None
        self.mean_in_radius = None
        self.mean_thick = None
        self.curv_outer_mean = None
        self.curv_inner_mean = None
        self.init_window()    # zavolání init_window methody

    def init_window(self):
        """ Nastavení layoutu aplikace a vložení jednotlivých widgets s určitou
        metodou uvnitř"""
        global chkValue_2  
        self.Frame1 = LabelFrame(
            self,
            width=self.frame1_w,
            height=self.frame1_h,
            text="Control",
            font=16, bg=self.bg_color)
        self.Frame1.grid(row=0, column=0, sticky=N)
        self.Frame2 = Frame(
            self,
            width=self.frame2_w,
            height=self.frame2_h,
            bd=0,
            bg=self.bg_color)
        self.Frame2.grid(row=0, column=0, sticky=S)
        self.Frame3 = Frame(
            self,
            width=self.frame3_w,
            height=self.frame3_h,
            bd=0)
        self.Frame3.grid(row=0, column=1, sticky=(N, W))
        self.Frame4 = LabelFrame(
            self,
            width=self.frame4_w,
            height=self.frame4_h,
            text="Results",
            font=16,
            bg=self.bg_color)
        self.Frame4.grid(row=0, column=0, sticky=S)
        self.master.title("Opening angle")
        menu = Menu(self.master)
        self.master.config(menu=menu)
        file = Menu(menu)
        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        file.add_command(label="Exit", command=self.exit_window)
        menu.add_cascade(label="File", menu=file)
        edit = Menu(menu)
        edit.add_command(label="Undo")
        menu.add_cascade(label="Edit", menu=edit)
        self.ImImport = Button(
            self.Frame1,
            text="Upload image",
            command=self.import_image,
            bd=0,
            highlightbackground=self.bg_color)
        self.ImImport.place(x=(self.frame_width / 3) * 0.05, y=0)
        self.chkValue_1 = BooleanVar()
        self.chkValue_1.set(False)
        self.Basler = Checkbutton(
            self.Frame1,
            text="Image from Basler camera",
            var=self.chkValue_1,
            command=self.pixelSize,
            bd=0,
            bg=self.bg_color)
        self.Basler.place(x=((self.frame_width / 3) * 0.05), y=(self.frame_height / 2) * 0.11)
        self.Calibration = Button(
            self.Frame1,
            text="Calibration",
            command=self.calibration,
            bd=0,
            highlightbackground=self.bg_color)
        self.Calibration.place(x=(self.frame_width / 3) - 100, y=0)   
        # self.PixEntry = Entry(self.Frame1, text = "Pixel size", width = 5)
        # self.PixEntry.place(x= ((FrameWidth/3) * 0.05) + 70, y=(FrameHeight/2) * 0.11)
        # self.Pix = Label (self.Frame1, text = "Pixel size:", bg = "red")
        # self.Pix.place (x = (FrameWidth/3) * 0.05, y=(FrameHeight/2) * 0.1)
        # self.OkButt = Button (self.Frame1, text = "OK", command = self.pixelSize)
        # self.OkButt.place(x= (FrameWidth/3) * 0.5, y=(FrameHeight/2) * 0.1)
        self.ROIButt = Button(
            self.Frame1,
            text="Select boundary",
            command=self.ROI_select,
            bd=0,
            highlightbackground=self.bg_color)
        self.ROIButt.place(x=(self.frame_width / 3) * 0.05, y=(self.frame_height / 2) * 0.2)
        self.DrawResults = Button(
            self.Frame1,
            text="Draw results",
            command=self.draw_results,
            bd=0,
            highlightbackground=self.bg_color)
        self.DrawResults.place(x=(self.frame_width / 3) * 0.05, y=(self.frame_height / 2) * 0.5)
        self.save_results_button = Button(
            self.Frame1,
            text="Save",
            command=self.save_results,
            bd=0,
            highlightbackground=self.bg_color)
        self.save_results_button.place(x=(self.frame_width / 3) * 0.7, y=(self.frame_height / 2) * 0.5)
        self.PointEntry = Entry(
            self.Frame1,
            width=5,
            bd=0,
            highlightbackground=self.bg_color)
        self.PointEntry.place(x=((self.frame_width / 3) * 0.05) + 120, y=(self.frame_height / 2) * 0.3)
        self.Point = Label(
            self.Frame1,
            text="Number of Points:",
            bd=0,
            bg=self.bg_color)
        self.Point.place(x=(self.frame_width / 3) * 0.05, y=(self.frame_height / 2) * 0.3)
        self.OkButt_1 = Button(
            self.Frame1,
            text="OK",
            command=self.number_point,
            bd=0,
            highlightbackground=self.bg_color)
        self.OkButt_1.place(x=((self.frame_width / 3) * 0.05) + 180, y=(self.frame_height / 2) * 0.3)
        self.chkValue_2 = BooleanVar()
        self.chkValue_2.set(False)
        self.Cutted = Checkbutton(
            self.Frame1,
            text="Cutted ring",
            var=self.chkValue_2,
            command=self.cutted_ring,
            bd=0,
            bg=self.bg_color)
        self.Cutted.place(x=((self.frame_width / 3) * 0.05), y=(self.frame_height / 2) * 0.4)
        self.chkValue_3 = BooleanVar()
        self.chkValue_3.set(False)        
        self.Cutted = Checkbutton(
            self.Frame1,
            text="Full ring",
            var=self.chkValue_3,
            command=self.full_ring,
            bd=0,
            bg=self.bg_color)
        self.Cutted.place(x=((self.frame_width / 3) * 0.5), y=(self.frame_height / 2) * 0.4)
        self.OutLenRes = Text(
            self.Frame4,
            bd=0,
            width=int(self.frame4_h / 4.5),
            height=1,
            highlightbackground=self.bg_color,
            bg=self.bg_color)
        self.OutLenRes.place(x=self.frame4_w * 0, y=self.frame4_h * 0) 
        self.InnerLenRes = Text(
            self.Frame4,
            bd=0,
            width=int(self.frame4_h / 4.5),
            height=1,
            highlightbackground=self.bg_color,
            bg=self.bg_color)
        self.InnerLenRes.place(x=self.frame4_w * 0, y=self.frame4_h * 0.2)
        self.OutRadRes = Text(
            self.Frame4,
            bd=0,
            width=int(self.frame4_h / 4.5),
            height=1,
            highlightbackground=self.bg_color,
            bg=self.bg_color)
        self.OutRadRes.place(x=self.frame4_w * 0, y=self.frame4_h * 0.4)    
        self.InnerRadRes = Text(
            self.Frame4,
            bd=0,
            width=int(self.frame4_h / 4.5),
            height=1,
            highlightbackground=self.bg_color,
            bg=self.bg_color)
        self.InnerRadRes.place(x=self.frame4_w * 0, y=self.frame4_h * 0.6)
        self.ThickRes = Text(
            self.Frame4,
            bd=0,
            width=int(self.frame4_h / 4.5),
            height=1,
            highlightbackground=self.bg_color,
            bg=self.bg_color)
        self.ThickRes.place(x=self.frame4_w * 0.5, y=self.frame4_h * 0)
        self.AngleRes = Text(
            self.Frame4,
            bd=0,
            width=int(self.frame4_h / 4.5),
            height=1,
            highlightbackground=self.bg_color,
            bg=self.bg_color)
        self.AngleRes.place(x=self.frame4_w * 0.5, y=self.frame4_h * 0.2)
        self.outer_mean_curv_res = Text(
            self.Frame4,
            bd=0,
            width=int(self.frame4_h / 4.5),
            highlightbackground=self.bg_color,
            bg=self.bg_color)
        self.outer_mean_curv_res.place(x=self.frame4_w * 0.5, y=self.frame4_h * 0.4)
        self.inner_mean_curv_res = Text(
            self.Frame4,
            bd=0,
            width=int(self.frame4_h / 4.5),
            highlightbackground=self.bg_color,
            bg=self.bg_color)
        self.inner_mean_curv_res.place(x=self.frame4_w * 0.5, y=self.frame4_h * 0.6)

    def calibration(self, *args):
        """ Kalibrační metoda, když bych například měl snímky z jiného zařízení.
        Jinak stačí zvolit, že se jedná o naši BASLER kameru, kde to bude nastaveno
        defaultně, jen někdy to pro jistotu můžeme předefinovat. Je potřeba udělat 
        snímek třeba s měrkou ve výšce toho prsence a tu pak naklikat."""
        global image_calibration
        path_calib = filedialog.askopenfilename(title='Please select a directory')
        if len(path_calib) > 0:
            image_calibration = cv2.imread(path_calib)
        img_shape = image_calibration.shape
        cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
        # cv2.setMouseCallback('Calibration', draw_circle_2)
        cv2.imshow("Calibration", image_calibration)
        # cv2.waitKey(0)
        cv2.destroyWindow("Calibration")
        cv2.namedWindow("calibration", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('calibration', draw_circle_2)
        while(1):
            cv2.imshow('calibration', image_calibration)
            k = cv2.waitKey(20) & 0xFF
            if k == 27:    # ESC to EXIT window
                cv2.destroyWindow("calibration")
                break
        dist_cal = np.sqrt((mouseX_2[0] - mouseX_2[1])**2 + (mouseY_2[0] - mouseY_2[1])**2)
        object_len = 1    # mm
        new_pix = object_len / dist_cal    # object je to u čeho znám délku, musím zadat!
        self.pixel_size = new_pix
        return self.pixel_size

    def import_image(self):
        """ Vložení základního obrázku, který bude využit pro ROI a nastavení
            vnějšího a vnitřního okraje """
        global path
#        path = filedialog.askopenfilename(parent=root,initialdir="/",title='Please select a directory')
        path = filedialog.askopenfilename(title='Please select a directory')
        load = Image.open(path)
        load = load.resize((int(self.frame2_w), int(self.frame2_h - 80)), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        # labels can be text or images
        img = Label(self.Frame2, image=render, borderwidth=0)
        img.Image = render
        img.place(x=0, y=0)
        return path

    def pixelSize(self):
        """ Pixel size je nutné nastavit, když mám snímky z BASLER. JEdnou za čas
        překalibrovat snímek z BASLER. Při kalibraci je důležité, aby marker ležel
        v místě, kde snímkuji. Když jsem měl hist. sklíčko pod tím trochu, tak tam
        je lehce odklon. Rozměr je ručně trochu posunut. 0.033 je ok pro konec plastové
        tyčinky, takže to příště nalepit co nejvíce srovnané s horním okrajem!!!"""
        return self.pixel_size

    def SI_convert(self, mX, mY, mX_1, mY_1, r):
        """ Convert metrics in pixels to the unit which is set during calibration. Millimeters will be used most often. """
        locX = (np.asarray(mX) + r[0]) * self.pixel_size
        locY = (np.asarray(mY) + r[1]) * self.pixel_size
        locX_1 = (np.asarray(mX_1) + r[0]) * self.pixel_size
        locY_1 = (np.asarray(mY_1) + r[1]) * self.pixel_size
        return locX, locY, locX_1, locY_1

    def cutted_ring(self):
        """ NAstaví parametr pro spline, aby nespojoval konce"""
        global ringShape
        ringShape = 0

    def full_ring(self):
        """ Nastaví parametr pro spline, aby to bylo uzavřeno"""
        global ringShape
        ringShape = 1

    def number_point(self):
        """ Metoda, která mi nastaví globální proměnou odpovídající počtu budů 
            pro intepolaci. """
        global num_points
        points = self.PointEntry.get()
        num_points = int(points)

    def ROI_select(self):
        """ Metoda využívající opencv pro výběr vnějšího a vnitřního obvodu pomocí
        naklikávání okraje. Body nemusí být rozloženy rovnoměrně, ale v případě
        větší křivosti je potřeba toto místo zaznamenat"""
        global img_shape, image, imCrop, crop_shape, r
        if len(path) > 0:
            image = cv2.imread(path)
        img_shape = image.shape
        cv2.namedWindow("Original image", cv2.WINDOW_NORMAL)
        cv2.imshow("Original image", image)
        # cv2.waitKey(0)    #Když to není, tak se to hned vypne. Nemusím tak zbytečně rozbrazovat origo pro potvrzení
        cv2.namedWindow("Select ROI", cv2.WINDOW_NORMAL)
        cv2.destroyWindow("Original image")
        r = cv2.selectROI("Select ROI", image, fromCenter=False)
        imCrop = image[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        cv2.namedWindow("Your choosen ROI", cv2.WINDOW_NORMAL)
        crop_shape = imCrop.shape
        cv2.destroyWindow("Select ROI")
        cv2.imshow("Your choosen ROI", imCrop)
        # cv2.waitKey(0)
        cv2.destroyWindow("Your choosen ROI")
        cv2.namedWindow("Outer boundary", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Outer boundary', draw_circle)
        while(1):
            cv2.imshow('Outer boundary',imCrop)
            k = cv2.waitKey(20) & 0xFF
            if k == 27:    # ESC to EXIT window
                break
            elif k == ord('a'):   # 32 odpovídá mezerníku, ENTER nemá unikátní číslo.. lze využít ord("a"), například
                cv2.destroyAllWindows()#
                cv2.namedWindow("Outer boundary", cv2.WINDOW_NORMAL)
                cv2.imshow('Outer boundary', imCrop)
                cv2.setMouseCallback('Outer boundary', draw_circle_1)    # přiřazení funkce k oknu#
        cv2.destroyAllWindows()

    def draw_results(self):
        """ Metoda DrawResult nedělá poue vykreslení grafu, ale také bere do sebe
        ostaní metody, které postupně upravují data, zíkaná z naklikaných bodů """
        # global curv_outer, curv_inner
        # global inter, inter_1, k_n, loc_out_radius, opening_angle, v1, v2
        # použití funkce SI_converter, která má za výstup souřadnice na ty dané body v daných jednotkách (dáno pixel pize)
        locX, locY, locX_1, locY_1 = self.SI_convert(mouseX, mouseY, mouseX_1, mouseY_1, r)   # převedení na SI
        inter = interparc(num_points, locX, locY, 'linear')    # interpolace na equidistant points
        inter_1 = interparc(num_points, locX_1, locY_1, 'linear')
        vzdalenost = []
        vzdalenost_1 = []
        for i in range(1, len(inter), 1):
            datax = inter[i][0] - inter[i - 1][0]
            datay = inter[i][1] - inter[i - 1][1]
            data = np.sqrt(datax**2 + datay**2)
            vzdalenost.append(data)
            datax_1 = inter_1[i][0] - inter_1[i - 1][0]
            datay_1 = inter_1[i][1] - inter_1[i - 1][1]
            data_1 = np.sqrt(datax_1**2 + datay_1**2)
            vzdalenost_1.append(data_1)
        self.len_out, self.len_inner = segment_len(vzdalenost, vzdalenost_1)   # určení délky segmentů
        # PARAMETR S SE MUSÍ ROVNAT jedničce! JINAK JE MOC VELKÉ VYHLAZENÍ A NEODPOVÍDÁ TO TVARU!!
        tck, u = interpolate.splprep([inter[:, 0], inter[:, 1]], s=1, u=None, per=ringShape)
        tck_1, u_1 = interpolate.splprep([inter_1[:, 0], inter_1[:, 1]], s=1, u=None, per=ringShape)
        """Parametr s u splprep určuje, zda je spline uzavřený, nebo ne. Takže 
        v případě, kdy budu interpolovat kruh, tak mohu dát s=1 a mělo by se to uzavřít."""
        # ynew = interpolate.splev(inter[:,0], tck, der=0)
        # ynew_1 = interpolate.splev(inter_1[:,0], tck_1, der=0)
        newpoints = np.transpose(np.asarray(interpolate.splev(u, tck)))
        newpoints_1 = np.transpose(np.asarray(interpolate.splev(u_1, tck_1)))
        # derivace interpolovaného splinu pro určení tečny a následně normály 
        """Tady pozor na vyjádření derivace. Tím, že používám splprep, tak mám B-spline 
        N-dimensional, takže mi to hodí diferenciál pro každou osu. JEstliže chci tečnu,
        tak musím ještě provést výpočet dy,dx. Stejný problém bude i u křivosti."""
        dx, dy = interpolate.splev(u, tck, der=1)
        dx_1, dy_1 = interpolate.splev(u_1, tck_1, der=1)
        derivative = dy / dx
        uhel = np.arctan(derivative)
        k_n = np.tan((uhel + np.pi / 2))    # pozor, v radiánech!

        b_coef, arr1 = normal_lines(newpoints, newpoints_1, k_n)
        x_inters, x_interss, y_inters, y_interss, x_locT, y_locT = innerIntersection(newpoints_1, arr1, newpoints)
        self.mean_thick = mean_thickness(x_locT, y_locT, x_interss, y_interss)

        dxx, dyy = interpolate.splev(u, tck, der=2)
        dxx_1, dyy_1 = interpolate.splev(u_1, tck_1, der=2)
        curv_outer = np.abs(dx * dyy - dy * dxx) / np.power(dx**2 + dy**2, 3 / 2)
        curv_inner = np.abs(dx_1 * dyy_1 - dy_1 * dxx_1) / np.power(dx_1**2 + dy_1**2, 3 / 2)
        self.curv_outer_mean = np.mean(curv_outer)
        self.curv_inner_mean = np.mean(curv_inner)
        loc_out_radius = 1 / curv_outer
        loc_in_radius = 1 / curv_inner
        self.mean_out_radius = np.mean(loc_out_radius)
        self.mean_in_radius = np.mean(loc_in_radius)
        if ringShape == 0:
            v1 = newpoints_1[0] - newpoints_1[round((num_points - 1) / 2)]
            v2 = newpoints_1[round(num_points - 1)] - newpoints_1[round((num_points - 1) / 2)]
            opening_angle = angle(v1, v2)

        screen_DPI = 156
        pixel_mm = 25.4 / screen_DPI
        pixel_in = pixel_mm / 25.4
        # Rozměry obrázku je potřeba naladit na určitý zařízení!!
        fig = Figure(figsize=((self.frame3_w) * pixel_in, (self.frame3_h - 35) * pixel_in), dpi=156)
        ax = fig.add_subplot(111)
        fig.subplots_adjust(wspace=0.6, hspace=0.6, left=0.15, bottom=0.22, right=0.96, top=0.96)
        ax.plot(newpoints[:, 0], newpoints[:, 1], 'x')
        ax.plot(newpoints_1[:, 0], newpoints_1[:, 1], 'rx')
        # interpolace splinem
        ax.plot(newpoints[:, 0], newpoints[:, 1], 'b-')
        ax.plot(newpoints_1[:, 0], newpoints_1[:, 1], 'r-')
        
        # for iiii in range (0,len(newpoints[:,0]), 1): 
        #     ax.plot(newpoints_1[:,0],arr1[:,iiii + len(newpoints)],"k:")
        ax.plot((newpoints_1[0][0], newpoints_1[round((num_points - 1) / 2)][0]),
                (newpoints_1[0][1], newpoints_1[round((num_points - 1) / 2)][1]), "g:")
        ax.plot((newpoints_1[round(num_points - 1)][0], newpoints_1[round((num_points - 1) / 2)][0]),
                (newpoints_1[round(num_points - 1)][1], newpoints_1[round((num_points - 1) / 2)][1]), "g:")
        ax.plot(x_interss, y_interss, "*k")
        ax.axis([0, (img_shape[1] * self.pixel_size), (img_shape[0] * self.pixel_size), 0])
        ax.set_xlabel("x axis length [mm]")
        ax.set_ylabel("y axis length [mm]")
        canvas = FigureCanvasTkAgg(fig, self.Frame3)
        canvas.get_tk_widget().pack(side=TOP, fill=NONE, expand=1)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, self.Frame3)
        toolbar.update()
        canvas._tkcanvas.pack(side=BOTTOM, fill=NONE, expand=1)
               
        self.OutLenRes.insert(END, ("Outer length=", "%.2f" % self.len_out))
        self.InnerLenRes.insert(END, ("Inner length=", "%.2f" % self.len_inner))
        self.OutRadRes.insert(END, ("Outer radius=", "%.2f" % self.mean_out_radius))
        self.InnerRadRes.insert(END, ("Inner radius=", "%.2f" % self.mean_in_radius))
        self.ThickRes.insert(END, ("Mean thickness=", "%.2f" % self.mean_thick))
        self.outer_mean_curv_res.insert(END, ("Mean_curv_O=", "%.3f" % self.curv_outer_mean))
        self.inner_mean_curv_res.insert(END, ("Mean_curv_I=", "%.3f" % self.curv_inner_mean))
        if ringShape == 0:
            self.AngleRes.insert(END, ("Opening angle:", "%.2f" % opening_angle))
        self.save_results()

    def save_results(self):
        file_name = Path(path).stem
        save_path = Path(path).parent.resolve() / file_name
        export = {
            'Outer length': self.len_out,
            'Inner length': self.len_inner,
            'Mean outer radius': self.mean_out_radius,
            'Mean inner radius': self.mean_in_radius,
            'Mean thickness': self.mean_thick,
            'Mean outer curvature': self.curv_outer_mean,
            'Mean inner curvature': self.curv_inner_mean
        }
        with open(f'{save_path}.txt', 'w') as file:
            file.write(json.dumps(export))

    def exit_window(self):
        root.quit()     # stops mainloop
        root.destroy()


root = Toplevel()
root.geometry("%dx%d+0+0" % (frame_width, frame_height))
app = Window(root)
root.config(bg="skyblue")
root.mainloop()
