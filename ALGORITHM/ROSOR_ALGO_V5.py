
from tendo import singleton
me = singleton.SingleInstance()

import cv2
import os
import numpy as np
import logging
import time
import datetime 
import glob
import json
import pymysql
from PIL import Image
from skimage.io import imread
import ast
import xml.etree.ElementTree as ET
from PIL import ImageFont, ImageDraw, Image
from fpdf import FPDF
import queue
import threading
from shapely.geometry import Point, Polygon
from PIL import Image, ImageDraw
#for maskrcnn 
# import some common detectron2 utilities
from detectron2.utils.logger import setup_logger
# from future.backports.test.pystone import FALSE
setup_logger()
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import BoxMode
from detectron2.engine import DefaultTrainer
from detectron2.utils.visualizer import ColorMode
# import pyautogui


#============================ CAMERA MODUAL ==============================#

import multiprocessing
from multiprocessing.dummy import Process

from pypylon import pylon
import cv2
import time
import os
import datetime
#from plc_communication_v1 import PLCCommunication
import logging
import pymysql

#-==========================PLC===========================================#
import traceback
import logging
pymc3e=None
import socket


#=============================== for pdf ========================================#
from fpdf import FPDF
import os
from PIL import ImageFont, ImageDraw, Image
import datetime
import pymysql

gMailObj = None

from PLC_COMMUINCATION_V1 import PLCCommunication




processID = os.getpid()
os.environ['CUDA_VISIBLE_DEVICED']='0'

''' Initializing Logger '''
fileName = os.path.basename(__file__).split(".")[0]
logger = None
log_format=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger(fileName)
logger.setLevel(logging.DEBUG)
logger_fh=logging.FileHandler(f"{fileName}.log",mode='a')
logger_fh.setFormatter(log_format)
logger_fh.setLevel(logging.DEBUG)
logger.addHandler(logger_fh)

CAM1_IMAGE = "C:/INSIGHTZZ/ROSR_ALGO/ALGORITHM/IMG/CAM1.jpg"#config_root[10].text
ImgDelPath = "C:/INSIGHTZZ/ROSR_ALGO/ALGORITHM/IMG"

SAVE_IMG_FILE_PATH="C:/INSIGHTZZ/ROSR_ALGO/UI/ROSR/UI_CODE/DEFECT_IMAGE/"
config_path = "C:/INSIGHTZZ/ROSR_ALGO/ALGORITHM/ROSR_CONFIG_New.xml"

saved_raw_image_path ="C:/INSIGHTZZ/ROSR_ALGO/UI/ROSR/UI_CODE/DEFECT_IMAGE/"
straightSealant_YminList_StraightTop_Ymin_list_base1_THR = 10
straightSealant_YminList_StraightTop_Ymin_list_base2_THR = 15

config_parse = ET.parse(config_path)
config_root = config_parse.getroot()
#========= gtting all variable from config file ========#
CODE_PATH = config_root[0].text
DB_USER = config_root[1].text
DB_PASS = config_root[2].text
DB_HOST = config_root[3].text
DB_NAME = config_root[4].text

NUMCLASSES = int(config_root[5].text)
DETECTTHRESH = float(config_root[6].text)
SAVED_FOLDER_PATH = config_root[7].text
MASK_MODEL_PATH = config_root[8].text
CONFIG_YAML_FL_PATH = config_root[9].text
ALL_CLASS_NAMES ="C:/INSIGHTZZ/ROSR_ALGO/ALGORITHM/ROSR_MODEL/CHAKAN_ROSR.json" #ast.literal_eval(config_root[10].text)
DEPLOYMENT_STATUS = int(config_root[11].text)
PROCESSED_IMAGE_DATA = config_root[12].text

DIESEL_TYPE = 1
GASOLINE_TYPE = 2

topSide_thinkNessXmin_cam2 = []
leftSide_thinkNessXmin_cam2 = []
rightSide_thinkNessXmin_cam2 = []

topSide_thinkNessXmin = []
leftSide_thinkNessXmin = []
rightSide_thinkNessXmin = []    


def __loadLablMap__():
    #load labelmap
    with open(ALL_CLASS_NAMES,"r") as fl:
        labelMap=json.load(fl)
    return labelMap

labelMap = __loadLablMap__()
label_classes=list(labelMap.values())

#------cam setup------------
CAM1 = '40378280'
camlist = pylon.TlFactory.GetInstance().EnumerateDevices()
for i in camlist:
    print(i.GetSerialNumber())
    if i.GetSerialNumber() == CAM1:

        try:
            cam1 = i

        except Exception as e:
            print(e)


# Grab and save frames from each camera
global cam_cap
cam_cap=False

#======================== PLC ===================================#
    
#=====================================PLC FUN END================================#

class MaskFRCNN_Mahindra:
    def __init__(self):
        global MASK_MODEL_PATH
        self.predictor=None
        self.mrcnn_config_fl=CONFIG_YAML_FL_PATH
        self.mrcnn_model_loc= MASK_MODEL_PATH
        self.mrcnn_model_fl="model_final.pth"
        self.detection_thresh=0.4
        self.register_modeldatasets()

    def register_modeldatasets(self):
        d="test"
        MetadataCatalog.get("brake_" + d).set(thing_classes=label_classes)
        self.railway_metadata = MetadataCatalog.get("brake_test")
        #Start config for inf
        cfg = get_cfg()
        cfg.merge_from_file(self.mrcnn_config_fl)
        cfg.merge_from_list(["MODEL.DEVICE", "cpu"]) 
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 6  # only has one class (ballon)
        cfg.OUTPUT_DIR=self.mrcnn_model_loc
        cfg.MODEL.WEIGHTS =os.path.join(cfg.OUTPUT_DIR,self.mrcnn_model_fl)
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.detection_thresh
        self.predictor = DefaultPredictor(cfg)

    #========================================== Run_inference ===============================================#
    def run_inference(self,img):
        try:
            output = self.predictor(img)
            predictions=output["instances"].to("cpu")
            classes = predictions.pred_classes.numpy()

            #for counting number of items
            class_list = []
            for i in classes:
                class_list.append(self.railway_metadata.get("thing_classes")[i])
            class_dict = {} 
            for item in class_list: 
                if (item in class_dict): 
                    class_dict[item] += 1
                else: 
                    class_dict[item] = 1        
            
            boxes_surface = output["instances"].pred_boxes.tensor.to("cpu").numpy()
            pred_class_surface = output["instances"].pred_classes.to("cpu").numpy()
            scores_surface = output["instances"].scores.to("cpu").numpy()
            mask_surface = output['instances'].pred_masks.to("cpu").numpy()
            masklist = []
            masks = None  
            if predictions.has("pred_masks"):
                masks = predictions.pred_masks.numpy() 

            labellist = []
            for i,box in enumerate(boxes_surface):
                class_name = self.railway_metadata.get("thing_classes")[pred_class_surface[i]]
                score = scores_surface[i]
                box = boxes_surface[i]
                ymin = int(box[1])
                xmin = int(box[0])
                ymax = int(box[3])
                xmax = int(box[2])
                #cx, cy = get_centroid(xmin, xmax, ymin, ymax)
                labellistsmall = []
                labellistsmall.append(score)
                labellistsmall.append(ymin)
                labellistsmall.append(ymax)
                labellistsmall.append(xmin)
                labellistsmall.append(xmax)
                labellistsmall.append(class_name)
                try:
                    masklist = np.column_stack(np.where(masks[i] == True))
                except:
                    masklist = []   
                cx,cy = get_centroid(xmin, xmax, ymin, ymax)
                labellistsmall.append(cx)
                labellistsmall.append(cy)
                labellistsmall.append(masklist)
                labellist.append(labellistsmall)

            return img, labellist
        except Exception as e:
            print(f"Exception in run inference : {e}")
            logger.critical(f"Exception in run inference : {e}")

#========================================== Run_inference End ===============================================#     

#============================== pdf =========================#
def start_pdf(STATUS,engine_number, dirname):
    #engine_number = "VK1234567890"#Part_number#getEngineNumberDetails()
    print(engine_number)
    TodaysDate = datetime.datetime.now().strftime('%Y_%m_%d')
    #dirName = "/home/viks/VIKS/CODE/PROJECT_ALGORITHAM/NEW_EGAL_PROJECT/pdfgenerate/DEFECT_IMAGES/2023_08_25/"
    dirName =dirname+"/"#f"/home/deepak/Desktop/TOX/OP_40/INF_IMAGES"

    #image_folder_link1 = os.path.join(dirName, TodaysDate)
    #image_folder_link=(dirName+"/"+engine_number)+"/"
    #print(image_folder_link)
    #Status = engine_number
    INF_IMAGE_PATH_LIST=os.listdir(dirName)
    INF_IMAGE_PATH_LIST.sort()
    image_file_list = []
    for image_file in INF_IMAGE_PATH_LIST:
        if image_file.lower().endswith(('.jpg','.jpeg')):
            INF_FOLDER_PATH=dirName+image_file
            image_file_list.append(INF_FOLDER_PATH)
            # Replace double slashes with a single slash in each element of the list
            image_file_list = [path.replace("//", "/") for path in image_file_list]
    
    DateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    SavedirName = dirName
    createPDF(image_file_list, STATUS,engine_number, DateTime, SavedirName)
    print("createPDF Completed++++++++++++++++++++++")   



def reduceImageQuality(image_file_list):
    for image in image_file_list:
        image_file = Image.open(image)
        image_file.save(image, quality=25)

def createPDF(image_file_list,STATUS,engine_number,DateTime,SavedirName):
    global gMailObj
    pdf = FPDF()
    reduceImageQuality(image_file_list)
    pdf.add_page("L")
    pdf.rect(5.0,4.0,285.0,200.0)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(270,10,"DRISHTI PORTAL",0,1,'C')
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(270,15,"PISTON RING REPORT",0,1,'C')

    # pdf.image(mahindra_logo,x = 10, y =5, w = 50, h = 30, type = 'png', link = mahindra_logo)
    # pdf.image(insightzz_logo,x = 230, y = 5, w = 40, h =25, type = 'png', link = insightzz_logo)

    pdf.image("C:/INSIGHTZZ/ROSR_ALGO/UI_CODE/LOGO/Mahindra-Mahindra-New-Logo.png", x=10, y=5, w=50, h=30, type='png')
    pdf.image("C:/INSIGHTZZ/ROSR_ALGO/UI_CODE/LOGO/download.jpg", x=220, y=5, w=60, h=30, type='jpg')
               # c:\INSIGHTZZ\PISTON_DROPING_UI_MAIN\LOGO\uins.png

    pdf.rect(5.0,38.0,285.0,166.0)
    pdf.cell(270,30,"Engine Number : "+engine_number,0,1)
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(270,10,"Date & Time of Inspection : "+DateTime,0,1)
    pdf.cell(270,10,"Engine Status : "+STATUS,0,1)
    pdf.set_font("Times", size=13)   
    image_file_list1=[]
    image__file_list2=[]
    counter=0
    counter2=0
    for image in image_file_list:
        image_file_list1.append(image)
       
    if len(image_file_list1) >0:
        for image in image_file_list1:
            pdf.add_page("L")
            pdf.rect(5.0,4.0,285.0,200.0)
            fixed_height = 170
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(250,10,"IMAGE NAME : "+os.path.basename(image),0,1,'C')
            img = Image.open(image)
            height_percent = (fixed_height / float(img.size[1]))
            width_size = int((float(img.size[0]) * float(height_percent)))
            pdf.image(image,20,20,width_size,fixed_height)
            counter=counter+1
            print(counter)
            if counter==5:
                break
    
    pdf.output(SavedirName+"/"+engine_number+".pdf", "F")   


#=================== updateENGINE_NUMBER ============================# 
def updateENGINE_NUMBER(PLC_Engine_number):
    try:
        db_object = pymysql.connect(host = DB_HOST,user = DB_USER,password = DB_PASS,db = DB_NAME)
        cur = db_object.cursor() 
        query="select * from Engine_number_table;"
        cur.execute(query)
        values=cur.fetchall()
        values=values[0][1]
        print(values)
        query = f"update Engine_number_table set ENGINE_NUMBER = '{PLC_Engine_number}'"
        cur.execute(query)
        db_object.commit()
    except Exception as e:
        print("updateENGINE_NUMBER is:",e)
        logger.critical(f"updatePLCDBStatus() Exception is : {e} ")
    finally:
        cur.close()
        db_object.close()    
#=================== updateENGINE_NUMBER CLOSE ============================# 

def get_centroid(xmin, xmax, ymin, ymax):
    cx = int((xmin + xmax) / 2.0)
    cy = int((ymin + ymax) / 2.0)
    return(cx, cy)

def getDirectoryPath(ParentDirName):
        mydir = os.path.join(os.getcwd(), ParentDirName+datetime.datetime.now().strftime('%Y%m%d')+"/")
        if os.path.isdir(mydir) is not True:
            os.makedirs(mydir)
        return mydir

#========================================== insertDB_In_ROSR_DB Start ===============================================#
def insertDB_In_ROSR_DB(ENGINE_TYPE, DATE_TIME, ENGINE_NUMBER, CAM1_IMAGE_LINK, STATUS):
    try:
        db_insert = pymysql.connect(host=DB_HOST,user=DB_USER, passwd=DB_PASS,db= DB_NAME)
        cur = db_insert.cursor()
        query = f"insert into ROSR_PROCESSING_TABLE \
        (DATE_TIME, ENGINE_TYPE, ENGINE_NUMBER, DEFECT, CAM1_IMG_LINK)\
        values ('{DATE_TIME}','{ENGINE_TYPE}','{ENGINE_NUMBER}','{STATUS}','{CAM1_IMAGE_LINK}')"
        print(query)
        cur.execute(query)
        db_insert.commit()
        cur.close()
        db_insert.close()
    except Exception as e:
        print(e)
        logger.critical("ROSR_PROCESSING_TABLE Exception is : "+str(e))

#========================================== InsertDB_InOil_SumpDB End ===============================================#
def draw_rectangle(img_rd, ymin, ymax, xmin, xmax, score, color):
    fontsize_x = cv2.getTextSize( cv2.FONT_HERSHEY_SIMPLEX, 0.75, 1)[0][0]
    fontsize_y = cv2.getTextSize( cv2.FONT_HERSHEY_SIMPLEX, 0.75, 1)[0][1]
    cv2.rectangle(img_rd, (xmin,ymin), (xmax,ymax),( int(color[0]),int(color[1]),int(color[2])),2)   
    cv2.rectangle(img_rd, (xmin,ymin), ((xmin+fontsize_x),int(ymin-25)), ( int(color[0]),int(color[1]),int(color[2])),-1)
    #cv2.putText(img_rd, (xmin,int(ymin)) ,cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2, cv2.FILLED)
    return img_rd

#========================================= drawCV2Box ====================================================#
def drawCV2Box(frame, labelName, xmin, ymin, xmax, ymax):
    try:
        fontScale = 2# Adjust the font scale as needed
        cv2.putText(frame, labelName, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0, 0, 255), 4, cv2.LINE_AA + cv2.LINE_8)
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 7)
    except Exception as e:
        pass
        print("Exception in drawCV2Box() : "+ str(e))

#=============================== bulkSealant_leftRightTop_crrdCheck =================+#
def bulkSealant_leftRightTop_crrdCheck(image, left_bulkSealant, right_bulkSealant, top_bulkSealant, bulk_left_sealant,bulk_top_sealant,bulk_right_sealant):
    try:   
        if left_bulkSealant == True:
            print("bulk_left_sealant is :",bulk_left_sealant)
            for bulk_left in bulk_left_sealant:
                #drawCV2Box(image, class_name, xmin, ymin, xmax, ymax) #drawCV2Box(img, class_name, xmin, ymin, xmax, ymax)
                drawCV2Box(image, bulk_left[5],bulk_left[3],bulk_left[1],bulk_left[4],bulk_left[2])
    except Exception as e:
        print("Exception in check left_bulkSealant",e)               

    try:
        if right_bulkSealant == True:
            print("bulk_right_sealant is 1 :",bulk_right_sealant)
            for bulk_right in bulk_right_sealant:
                #drawCV2Box(image, class_name, xmin, ymin, xmax, ymax) #drawCV2Box(img, class_name, xmin, ymin, xmax, ymax)
                print("ulk_right[5] :",bulk_right[5])
                drawCV2Box(image, bulk_right[5],bulk_right[3],bulk_right[1],bulk_right[4],bulk_right[2])    
    except Exception as e:
        print("Exception in check right_bulkSealant",e)                
    try:
        if top_bulkSealant == True:
            print("bulk_top_sealant is :",bulk_top_sealant)
            for bulk_top in bulk_top_sealant:
                #drawCV2Box(image, class_name, xmin, ymin, xmax, ymax) #drawCV2Box(img, class_name, xmin, ymin, xmax, ymax)
                drawCV2Box(image, bulk_top[5],bulk_top[3],bulk_top[1],bulk_top[4],bulk_top[2])                

    except Exception as e:
        print("Exception in check top_bulkSealant",e)   

#=========================== Straight_sealantCordi ====================================#
straight_sealantCordi = []
cY = []
cXcY = []
def straightSealant_yminYmaxxminXmax(straight_sealant):
    for cordValue in straight_sealant:   
        element1 = cordValue[1]
        element2 = cordValue[2]
        element3 = cordValue[3]
        element4 = cordValue[4]
        cY_str1 = element1 #- element1 
        cY_str2 = element4 #- element3  #xmin + xmax) / 2.0

        cXcY.append((cY_str1,cY_str2))
        #cX.append(cX_str)
        straight_sealantCordi.append((element1, element2, element3, element4))
    print("straight_sealantCordi=========", straight_sealantCordi)
    return straight_sealantCordi,cXcY


#========================================== Craw_ThicknessCheck Start ============================================#
def Craw_ThicknessCheck(image, craw_Sealant_cam1):
    STATUS = True
    Craw_thinkNessXmin = []
    try:
        for vlu in craw_Sealant_cam1:        
            values = vlu
            print("values :",values)
            #if values[3] < 965:
            print(f"LEFT---------values[4]: {values[4]}, values[3]: {values[3]}")
            thinkNessXmin = values[4] - values[3]
            Craw_thinkNessXmin.append(thinkNessXmin)
            print("thinkNessXminXmax Top ======= ", thinkNessXmin)

        for TopSide in Craw_thinkNessXmin:
            if TopSide < 100:
            #if TopSide > 180 or TopSide < 80:
                drawCV2Box(image, "", values[3], values[1], values[4], values[2])
                STATUS =True
                break
            else:
                STATUS =False
                
    except Exception as e:
        print("Exception in SealantThicknessCheck_Top", e)
    return STATUS

#========================================== SealantThicknessCheck_TOP Start ============================================#
def SealantThicknessCheck_top(image, straightSealant_cam1_TOP):
    STATUS = True
    topSide_thinkNessXmin = []
    try:
        for vlu in straightSealant_cam1_TOP:        
            values = vlu
            print("values :",values)
            #if values[3] < 965:
            print(f"LEFT---------values[4]: {values[4]}, values[3]: {values[3]}")
            thinkNessXmin = values[4] - values[3]
            topSide_thinkNessXmin.append(thinkNessXmin)
            print("thinkNessXminXmax Top ======= ", thinkNessXmin)

        for TopSide in topSide_thinkNessXmin:
            if TopSide < 205:
            #if TopSide > 270 or TopSide < 100:
                drawCV2Box(image, "", values[3], values[1], values[4], values[2])
                STATUS =True
                break
            else:
                STATUS =False
                
    except Exception as e:
        print("Exception in SealantThicknessCheck_Top", e)
    return STATUS
#========================================== SealantThicknessCheck_left Start ============================================#
def SealantThicknessCheck_left(image, straightSealant_LEFT):
    leftSide_thinkNessXmin = []
    STATUS = True
    try:
        #return True 
        for vlu in straightSealant_LEFT:        
            values = vlu
            print("values :",values)
           # if values[1] < 180:
            print(f"LEFT---------values[4]: {values[4]}, values[3]: {values[3]}")
            thinkNessXmin = values[4] - values[3]
            leftSide_thinkNessXmin.append(thinkNessXmin)
            print("thinkNessXminXmax LEFT ======= ", thinkNessXmin)

        for leftSide in leftSide_thinkNessXmin:
            if leftSide < 50:
           # if leftSide > 175 or leftSide < 40:
                drawCV2Box(image, "", values[3], values[1], values[4], values[2])
                STATUS =True
                break
            else:
                STATUS= False
    except Exception as e:
        print("Exception in SealantThicknessCheck_left", e)
    return STATUS
#========================================== SealantThicknessCheck_right Start ===============================================#
def SealantThicknessCheck_right(image, straightSealant_RIGHT):
    STATUS = True
    rightSide_thinkNessXmin = []
    try:
        for vlu in straightSealant_RIGHT:
            print("vlu is ++++++++++++",vlu)
            values = vlu
            #if values[1] > 725:
            print("values===",values)
            print(f"RIGHT-------values[4] :{values[4]} , values[0][3] : {values[3]}")
            thinkNessXmin = values[4] - values[3]
            #print("RIGHT thinkNessXmin=========",thinkNessXmin)
            rightSide_thinkNessXmin.append(thinkNessXmin)
            print("thinkNessXminXmax RIGHT ======= ",thinkNessXmin)
    
        for rightSide in rightSide_thinkNessXmin:
            if rightSide < 50:
           # if rightSide > 170 or rightSide < 40:
                drawCV2Box(image, "",values[3],values[1],values[4],values[2])  
                STATUS = True  
            else:
                STATUS =  False
                
    except Exception as e:
        print("Exception in SealantThicknessCheck_right",e)     
#========================================== SealantThicknessCheck_right End ===============================================#

#================================= holeCheck_List Start =============================#
def holeCheck_List(image, hole_nok_list):
    try:
        for hole_NotOk in hole_nok_list:
            drawCV2Box(image, hole_NotOk[5],hole_NotOk[3],hole_NotOk[1],hole_NotOk[4],hole_NotOk[2])    
    except Exception as e:
        print("Exception in holeCheck_List",e)                 

#================================= sealantCut_check Start =============================#
def sealantCut_check(image, sealant_cut_list):
    try:
        for sealant_cut in sealant_cut_list:
            drawCV2Box(image, sealant_cut[5],sealant_cut[3],sealant_cut[1],sealant_cut[4],sealant_cut[2])    
    except Exception as e:
        print("Exception in sealant_cut",e) 

#=============================== GetEngineNumberDetails Start==================================#
def getEngineNumberDetails():
    engineNumber = ""
    # engineModel = ""
    try:
        db_fetch = pymysql.connect(host=DB_HOST,user=DB_USER, passwd=DB_PASS,db= DB_NAME)
        cur = db_fetch.cursor()
        query = "select ENGINE_NUMBER from ENGINE_NUMBER_TABLE order by ID desc limit 1"
        cur.execute(query)
        data_set = cur.fetchall()
        for row in range(0,len(data_set)):
            engineNumber = str(data_set[row][0])
            engineModel = str(data_set[row][0][0]+data_set[row][0][1])
    except Exception as e:
        print("Exception in getEngineNumberDetails :",e)
        logger.critical("getEngineNumberDetails() Exception is : "+ str(e))
    # finally:
    #     cur.close()
        # dbConnection.close()
    return engineNumber
#=============================== GetEngineNumberDetails End==================================#

def drawPolygonPoints(image,data_list):
    # Set the polygon points
    points = np.array(data_list, np.int32)
    # Reshape the points array to match the required format for cv2.polylines()
    points = points.reshape((-1, 1, 2))
    # Set the color and thickness of the polygon outline
    color = (0, 255, 0)  # BGR color format (red)
    thickness = 6
    # Draw the polygon on the image
    cv2.polylines(image, [points], isClosed=True, color=color, thickness=thickness)

def getMinMaxValues(values):
    minX = float('inf')
    minY = float('inf')
    maxX = float('-inf')
    maxY = float('-inf')
    
    for point in values:
        x, y = point
        if x < minX:
            minX = x
        if y < minY:
            minY = y
        if x > maxX:
            maxX = x
        if y > maxY:
            maxY = y
    return minX,minY,maxX,maxY


        


def config(camera_1):
        try:
            if camera_1 is  None:    
                camera_1 = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(cam1))
                camera_1.Open()
                camera_1.GevSCPSPacketSize.SetValue(1500)          
                camera_1.GevSCPD.SetValue(1000)          
                camera_1.GevSCFTD.SetValue(1000)          
                camera_1.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                camera_1.AcquisitionFrameRateEnable=True
        except Exception as e:
            print("Exception in",e)
        return camera_1

def capture():
    camera_1=None
    grab_1=None
    SAVE_IMG_FILE_PATH="C:/INSIGHTZZ/ROSR_ALGO/ALGORITHM/IMG/"
    camera_1=config(camera_1)
    img_listCheck = os.listdir(SAVE_IMG_FILE_PATH)
    img_listCheck.sort()              
    try:
        if camera_1.IsGrabbing():
                #if grab_1 is None:
            grab_1 = camera_1.RetrieveResult(2000, pylon.TimeoutHandling_ThrowException)
            converter = pylon.ImageFormatConverter()
            converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
                #continue
    except Exception as e:
            camera_1=None
            print("camera_1 Exception in",e)
            
# filename_1 = SAVE_IMG_FILE_PATH+"/CAM1_.jpg" 
    try:
        if grab_1.GrabSucceeded():
            image = converter.Convert(grab_1).GetArray()
            filename_1 = os.path.join(SAVE_IMG_FILE_PATH, f"IMG_.jpg")
            cv2.imwrite(filename_1, image)
        
    except Exception as e:
        camera_1=None
        print("except Exception in camera01",e)
        logger.error("Exception in camera 1 grabbing: " + str(e))
    # Release camera resources
    if grab_1:
        grab_1.Release()
        

#PLC_OBJ = MITSUBISHI_PLC_COMMUNICATION("192.168.37.237",5007,"binary")
#=============================== Start Main Func ==================================#
def main():
    # try:
    global list_of_image,ENGINE_TYPE,CAM1_IMAGE_LINK,ENGINE_NUMBER
    logger.debug(f"Starting Inference Process")
    mask_obj = MaskFRCNN_Mahindra()


    previosuenginnumber=""
    #============================FRAME CAPTURE END==============================#
    plcobj=PLCCommunication()
    createconnection=plcobj.createConnection()
    capturedone=True
    while True:
        try:
            heartbitwrite=plcobj.writeIntToPLC(createconnection,74,1)
            time.sleep(0.02)
            heartbitwrite=plcobj.writeIntToPLC(createconnection,74,0)
            cycleStartValue = plcobj.readIntFromPLC(createconnection,28)
            print("cycleStartValue value is =================:",cycleStartValue)
            try:      
                if cycleStartValue == 0:
                    cam_cap1 = True
                    time.sleep(0.1)
                    continue
                elif cycleStartValue ==1 :#and capturedone==True:
                    try:
                        #time.sleep(1.2)
                        capture()
                        PLC_Engine_number =plcobj.readStringFromPLC(createconnection,0)
                        PLC_Engine_number=PLC_Engine_number[0]
                        plcobj.writeIntToPLC(createconnection,28,0)
                        Engine_number=PLC_Engine_number[0:10]
                        updateENGINE_NUMBER(Engine_number)
                        capturedone=False
                    except Exception as e:
                        logger.debug("cam cap is True section: "+str(e))   
            except Exception as e:
                print("Exception is :",e)
                logger.debug("Cycle Start value Exception is : "+str(e))   

             # headStatus = "NOT_OK"
            headStatus_list=[]
            cam1_DefectStatus = False
            cam1_DefectStatus_cut = False
        
            imageSave1 = False
            class_names_to_check_img1 = ['straight_sealant','hole_ok','craw_sealant'] #'scissor_spring',
           
            list_of_image=[]
           
            straight_sealant_cam1 = []
        
            sealant_cut_list_cam1 = []
            if len(os.listdir("C:/INSIGHTZZ/ROSR_ALGO/ALGORITHM/IMG/"))==1 and Engine_number!=previosuenginnumber:
                ENGINE_TYPE=plcobj.readStringFromPLC(createconnection,10)
                ENGINE_TYPE=ENGINE_TYPE[0]
                ENGINE_TYPE=ENGINE_TYPE[0:12]
                previosuenginnumber=Engine_number
                heartbitwrite=plcobj.writeIntToPLC(createconnection,74,1)
                time.sleep(0.02)
                heartbitwrite=plcobj.writeIntToPLC(createconnection,74,0)
                try:
                    TodaysDate = datetime.datetime.now().strftime('%Y_%m_%d')
                    if os.path.exists(os.path.join(SAVE_IMG_FILE_PATH, TodaysDate)) is False: 
                        os.mkdir(os.path.join(SAVE_IMG_FILE_PATH, TodaysDate))
                    if os.path.exists(os.path.join(os.path.join(SAVE_IMG_FILE_PATH, TodaysDate),Engine_number)) is False:
                        os.mkdir(os.path.join(os.path.join(SAVE_IMG_FILE_PATH, TodaysDate),Engine_number))
                    image_folder_link1 = os.path.join(SAVE_IMG_FILE_PATH, TodaysDate)
                    image_folder_link=(image_folder_link1+"/"+Engine_number)+"/"

                    CAM1_IMAGE_LINK = ""
                    #================================= CAMERA -01 START======================================#
                    POSITION_WISE_DETECTION_POSITION = {}
                    # POSITION_WISE_DETECTION_POSITION["1"] = [[658,10],[654,1835],[2554,1816],[2562,25]]
                    POSITION_WISE_DETECTION_POSITION["1"] = [[759,63],[761,249],[753,455],[744,714],[738,1008],[732,1294],[734,1551],[738,1731],[738,1763],[1010,1778],[1283,1774],[1614,1767],[1938,1769],[2293,1767],[2306,1455],[2314,1127],[2298,835],[2279,563],[2263,298],[2249,118],[2251,71],[2030,61],[1806,45],[1514,35],[1181,45],[944,31],[787,31],[751,39]]
                
                    POLYGON_MAP = {}
                    POLYGON_MAP["1"]= [[717,171],[719,186],[715,210],[715,218],[716,236],[716,257],[716,269],[716,295],[717,321],[723,338],[746,356],[775,365],[805,368],[838,362],[858,348],[875,330],[899,319],[939,314],[979,314],[1018,310],[1063,314],[1112,308],[1169,313],[1195,328],[1236,356],[1266,360],[1303,351],[1320,334],[1333,328],[1352,346],[1378,358],[1414,365],[1446,363],[1475,347],[1492,334],[1502,328],[1517,322],[1553,331],[1575,334],[1601,352],[1640,365],[1669,378],[1702,389],[1716,399],[1721,436],[1726,461],[1742,487],[1769,506],[1792,511],[1834,518],[1853,516],[1882,541],[1915,583],[1936,621],[1960,674],[1992,741],[2006,786],[2015,851],[2000,889],[1976,920],[1969,945],[1977,978],[1998,1006],[2014,1031],[2030,1053],[2015,1093],[2003,1153],[1990,1193],[1969,1224],[1956,1263],[1942,1282],[1928,1312],[1907,1340],[1883,1371],[1863,1387],[1830,1392],[1804,1398],[1780,1420],[1760,1448],[1748,1484],[1727,1516],[1698,1535],[1654,1563],[1607,1583],[1569,1596],[1536,1605],[1513,1578],[1486,1566],[1456,1556],[1428,1555],[1395,1572],[1377,1594],[1363,1595],[1339,1580],[1301,1567],[1266,1575],[1240,1586],[1220,1614],[1203,1627],[1171,1637],[1128,1635],[1073,1632],[1020,1641],[945,1637],[903,1628],[875,1590],[831,1584],[792,1595],[755,1616],[745,1657],[747,1706],[748,1752],[750,1780],[782,1786],[812,1782],[812,1735],[808,1684],[820,1660],[853,1662],[869,1679],[896,1686],[933,1683],[977,1683],[1043,1685],[1085,1681],[1137,1682],[1185,1675],[1228,1678],[1254,1677],[1269,1639],[1290,1622],[1319,1624],[1341,1652],[1357,1671],[1388,1674],[1412,1671],[1414,1638],[1417,1627],[1435,1615],[1466,1616],[1482,1619],[1500,1639],[1514,1656],[1560,1649],[1602,1631],[1646,1619],[1676,1599],[1710,1577],[1769,1549],[1800,1516],[1800,1492],[1799,1468],[1821,1450],[1855,1456],[1883,1454],[1927,1402],[1958,1360],[1984,1309],[2031,1229],[2054,1138],[2068,1091],[2079,1040],[2086,997],[2041,987],[2028,959],[2026,933],[2036,915],[2071,903],[2075,877],[2078,845],[2068,813],[2057,765],[2042,723],[2017,671],[1995,624],[1967,575],[1940,533],[1895,481],[1861,457],[1849,454],[1828,454],[1800,462],[1770,445],[1765,418],[1774,392],[1771,369],[1702,341],[1671,317],[1627,299],[1563,278],[1527,276],[1490,261],[1459,273],[1441,304],[1407,317],[1390,300],[1376,272],[1359,254],[1329,246],[1302,253],[1292,287],[1279,309],[1254,305],[1232,280],[1221,263],[1180,254],[1134,256],[1093,259],[1059,256],[986,256],[928,261],[878,267],[834,270],[829,297],[813,315],[782,318],[763,294],[757,233],[766,201],[758,166],[756,160],[736,156],[720,160]]
                    LABEL_LIST_MAP = {}
                    ERROR_LIST_MAP = {}
                
                    CAM1_IMAGE = "C:/INSIGHTZZ/ROSR_ALGO/ALGORITHM/IMG/IMG_.jpg"#config_root[10].text
                    img_list = os.listdir(saved_raw_image_path)
                    img_list.sort()
                    if len(img_list) == 0:
                        print("=================Image not found===================")
                        continue
                    
                    # print("CAM1_IMAGE is :",CAM1_IMAGE)
                    time.sleep(0.1)
                    
                    im = cv2.imread(CAM1_IMAGE)
                    imreal = im.copy()
                    image, labellist  = mask_obj.run_inference(im)
                    # print("cam1 labellist is :",labellist)
                    if all(any(class_name in sublist for sublist in labellist) for class_name in class_names_to_check_img1):
                        # print(" OK")
                        class_present_img1 = False
                    else:
                        print("NOT OK")
                        class_present_img1 = True
                
                    for index, (key, value) in enumerate(POSITION_WISE_DETECTION_POSITION.items()):
                        ''' Create a polygon object '''
                        polygon = Polygon(value)
                        for item in labellist:
                            labelname = item[5]
                            if "hole" in labelname or "base" in labelname:
                                continue
                            cx = item[6]
                            cy = item[7]
                            ''' Point outside '''
                            point = Point(cx, cy)
                            # Check if the point lies inside the polygon
                            if polygon.contains(point):
                                LABEL_LIST_MAP[key] = item
                            else:
                                continue

                    #===========================================================================================#        
                    for index, (key, value) in enumerate(POLYGON_MAP.items()):
                        exsitingPoints = []
                        minX,minY,maxX,maxY = getMinMaxValues(value)
                        if key in LABEL_LIST_MAP.keys():
                            drawPolygonPoints(image,value)
                            labelItems = LABEL_LIST_MAP.get(key)
                            # minY = labelItems[1]
                            # maxY = labelItems[2]
                            polygon = Polygon(value)
                            mask_points = labelItems[8]
                            for points in mask_points:
                                px = points[1]
                                py = points[0]
                                
                                if py > minY and py < maxY:
                                    
                                    ''' Point outside '''
                                    point = Point(px, py)
                                    # Check if the point lies inside the polygon
                                    if polygon.contains(point):
                                        LABEL_LIST_MAP[key] = item
                                    else:
                                        if key in ERROR_LIST_MAP.keys():
                                            exsitingPoints = ERROR_LIST_MAP.get(key)
                                            exsitingPoints.append([px,py])
                                            ERROR_LIST_MAP[key] = exsitingPoints

                                            # cv2.circle(image, (px, py), radius=1, color=(0,0,255), thickness=3)
                                            # cam1_DefectStatus = True
                                        else:
                                            ERROR_LIST_MAP[key] = [[px,px]]
                                        cv2.circle(image, (px, py), radius=3, color=(0,0,255), thickness=9)
                                        cam1_DefectStatus = True
                                else:
                                    pass
                        
                    #===========================================================================================#
                    for index, labelsmalllist in enumerate(labellist):
                        values = labelsmalllist[:6]

                        if values[5] == "cut_sealant" or values[5] == "dry_area":
                            sealant_cut_list_cam1.append(labelsmalllist)
                            # print("sealant_cut_list_cam1 :", sealant_cut_list_cam1)

                        elif values[5] == "straight_sealant" or values[5] == "craw_sealant":
                            straight_sealant_cam1.append(values)
                            #print("straight_sealant_cam1:", straight_sealant_cam1)

                    #===========================================================================================#
                    try:
                        if len(sealant_cut_list_cam1) > 0:
                            sealantCut_check(image, sealant_cut_list_cam1)
                            cam1_DefectStatus_cut = True

                        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                        cv2.imwrite(image_folder_link + "/Realcam1.jpg", imreal)
                        cv2.imwrite(image_folder_link + "/Cam1.jpg", image)
                        CAM1_IMAGE_LINK = image_folder_link + "/Cam1.jpg"
                        print("IMAGE SAVE SUCCESS CAM1")
                        imageSave1 = True
                    except Exception as e:
                        print("Exception in CAM1 Defect sort:", e)
                        logger.critical("Exception in CAM1 Defect sort: " + str(e))


                except Exception as e:
                    print("Exception IN CAM2 check cord",e)   
                    logger.critical("Exception IN CAM2 check cord : "+str(e))   

                #==================================== imageSave1 =============================================#
                try:
                    if imageSave1 == True:
                        #if len(ERROR_LIST_MAP) > 0:
                        if cam1_DefectStatus == True or cam1_DefectStatus_cut==True:
                            headStatus = "NOT_OK"
                            headStatus_list.append(headStatus) 
                            plcobj.writeStringToPLC(createconnection,50,Engine_number)
                            plcobj.writeIntToPLC(createconnection,76,1)
                            
                        else:
                            headStatus = "OK"    
                            headStatus_list.append(headStatus) 
                            plcobj.writeStringToPLC(createconnection,50,Engine_number)
                            plcobj.writeIntToPLC(createconnection,76,1)

                        print("headStatus :",headStatus)
                        if 'NOT_OK' in headStatus_list:
                            print("send 2 not ok head")
                            current_datetime = datetime.datetime.now()
                            formatted_dateime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

                            realcam1_image_path = os.path.join(image_folder_link, formatted_dateime+"_RealCam1.jpg")
                            cam1_image_path = os.path.join(image_folder_link,formatted_dateime+"_Cam1.jpg")
                            cv2.imwrite(realcam1_image_path, imreal)
                            cv2.imwrite(cam1_image_path, image)
                        
                        else:
                            print("send 1 ok Engine")
                            #plcCommunicationObj.writeIntToPLC(clientConn,PLC_READ_DB_COLUMN_BUFFER_POSITION_OK.result_write_buffer_offset_ok,PLC_Write_Trigger_Value.PLC_TRIGGER_INSP_OK)
                
                        DATE_TIME = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        ENGINE_NUMBER = Engine_number        # CAM1_IMAGE_LINK : Initialized Above
                        STATUS	= headStatus
                    
                        # if imageDel == True:
                        insertDB_In_ROSR_DB(ENGINE_TYPE, DATE_TIME, ENGINE_NUMBER, CAM1_IMAGE_LINK, STATUS)
                        heartbitwrite=plcobj.writeIntToPLC(createconnection,74,1)
                        time.sleep(0.02)
                        heartbitwrite=plcobj.writeIntToPLC(createconnection,74,0)

                        imgpath=os.listdir(ImgDelPath)
                    #  time.sleep(0.3)
                        imageSave1 = False
                        try:
                            for i in imgpath :
                                if "IMG_.jpg" in i:
                                    os.remove(os.path.join(ImgDelPath,i))
                        except Exception as e:
                            pass
                            print(f"Exception in main remove : {e}")  
                        
                        # start_pdf(STATUS, Engine_number,image_folder_link)
                    else:
                        print("Image not save")
                        pass  

                    
                except Exception as e:
                    print("Exception in headStatus_list:",e)
                    logger.critical("Exception in headStatus_list: "+str(e))    
                    pass
        except Exception as e:
            print("Except Exception in main algo:", e)
            logger.debug("Except Exception in main algo: " + str(e))


if __name__ == '__main__':
    main()

