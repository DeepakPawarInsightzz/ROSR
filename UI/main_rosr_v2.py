
import multiprocessing
import numpy as np
import threading
from multiprocessing.dummy import Process
import os,time
from datetime import datetime, timedelta
import sys
from tkinter import CURRENT
import datetime
from datetime import date, datetime, timedelta
# import pandas as pd
# from fpdf import FPDF
import matplotlib.pyplot as plt
import subprocess
import math
import time
import datetime 
 # import login
import pymysql
from subprocess import Popen, PIPE
import logging
import traceback
import shutil
from pypylon import genicam
from pypylon import pylon
import cv2
import random

#DB credentials
db_user = 'root'
db_pass = 'insightzz123'
db_host = 'localhost'
db_name = 'rosr_db'

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui ,QtWidgets, uic
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 

# from mainwindow import Ui_MainWindow
# from login import Login
from login11 import Ui_Login
from download_popup import Ui_download_window
from InspectTypeWindow import Ui_Inspection_type_Window
# from version_window import Ui_VersionWindow
#========import SOme Comman Library============#
import logging
import traceback
import matplotlib
from matplotlib import axes
""" Canvas Library Imports """
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.dates as mdates

""" Graph Library Import """
from plotnine.data import economics
from plotnine import ggplot, aes, geom_line, geom_bar
from plotnine.data import mpg
import pandas as pd
import numpy as np
import math

from matplotlib.dates import date2num
from matplotlib import pyplot as plt, dates as mdates
from matplotlib import style
import matplotlib.dates as mdates


logger = None
log_format=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("spring_UI")
logger.setLevel(logging.DEBUG)
logger_fh=logging.FileHandler("piston_arrow_UI.log",mode='a')
logger_fh.setFormatter(log_format)
logger_fh.setLevel(logging.DEBUG)
logger.addHandler(logger_fh)

UI_CODE_PATH = os.getcwd()+"/"
PDF_TEMP_PATH = UI_CODE_PATH

DEFAULT_PDF_PATH = f"/home/{os.getlogin()}/Desktop/"

NO_IMAGE_PATH = UI_CODE_PATH+"logo/No_image_found.png"
DOWNLOAD_PATH = os.path.join(os.getcwd(),"Download_Data")
Download_data_is=DOWNLOAD_PATH.replace("\\","/")
DOWNLOAD_PATH=Download_data_is
if not os.path.exists(DOWNLOAD_PATH):
    os.mkdir(DOWNLOAD_PATH)

not_detected_var = "Needs Review"
UI_CODE_PATH = "C:\INSIGHTZZ/ROSR_ALGO/UI/ROSR/UI_CODE/"
#============================main window class===========================#
class mainwindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mainwindow,self).__init__()
        uic.loadUi(UI_CODE_PATH + 'mainwindowROSR.ui',self)

        # self.setupUi(self)        
        self.setWindowTitle("Drishti - Machine Vision Plateform")
        self.fetch_details_button.clicked.connect(self.fetch_details)
        self.pushButton_search.clicked.connect(self.search)

        # self.fetch_details_button.clicked.connect(self.fetch_details1)
        # self.download_details_button_2.clicked.connect(self.logout_clicked)
        self.download_details_button.clicked.connect(self.Download_report)
        self.Graph_btn.clicked.connect(self.Graph)
        self.pushButton_cycletart.clicked.connect(self.pushotton_cycletart)






        self.cam_Health()
        self.main_tab.tabBarClicked.connect(self.handle_tabbar_clicked)
        self.Print_Engine_number()
        self.Count_all_Engine()

        self.Total_Ok_Engine()
        self.Total_Notok_Engine()

        self.Start_process()
        
        self.main_tab_home=QTimer(self)
        self.main_tab_camhealth=QTimer(self)
        self.main_tab_home.timeout.connect(self.Start_process)
        self.main_tab_home.start(300)

        # set prev date in from date and today's date in to date field for report and analysis
        date1 = datetime.datetime.now()
        tday = QDate(date1.year, date1.month, date1.day)
        date2 = date1 - timedelta(days=1)
        prevDate = QDate(date2.year, date2.month, date2.day)

        self.from_dateEdit_reportDump.setDate(prevDate)
        self.to_dateEdit_reportDump.setDate(tday)

        self.from_dateEdit_reportDump.setDate(prevDate)
        self.to_dateEdit_reportDump.setDate(tday)


        # self.cam_health()
        # self.timer_health=QTimer(self)
        # self.timer_health.timeout.connect(self.cam_health)
        # self.timer_health.start(5000)
        
        #====================Getting current date time====================#
        current_date = date.today()
        d = QDate(current_date.year, current_date.month, current_date.day) 
        dd = QDate(current_date.year, current_date.month, current_date.day)
        # self.summary_from_date.setDate(d)
        # self.summary_to_date.setDate(dd)
        
        self.details_from_date.setDate(d)
        self.details_to_date.setDate(dd)

        now = datetime.datetime.now()
        self.figure = plt.figure()
        # self.canvas1 = FigureCanvas(self.figure)
        self.canvas1 = FigureCanvas(self.figure)
        

    def handle_tabbar_clicked(self, index):
        if index == 0:
            self.main_tab_home=QTimer(self)
            self.main_tab_home.timeout.connect(self.Start_process)
            self.Start_process()
            self.main_tab_home.start(100)
        else:
            self.main_tab_home.stop()
    def Print_Engine_number(self):
        try:
            Engine_number=""
            db_fetch = pymysql.connect(host = db_host,
                                        user = db_user,
                                        password = db_pass,
                                        db = db_name)
            cur = db_fetch.cursor()
            current_time = datetime.datetime.now()
            toDate=current_time.strftime("%Y-%m-%d")
            first_date=toDate+" 00:00:00"
            second_date=toDate+" 23:59:59"       
            query="SELECT * FROM rosr_db.ENGINE_NUMBER_TABLE ORDER BY ID desc limit 1;"       
            # query = "select count(ID) as TOTAL_COUNT, date(DATE_TIME) as DATE_TIME from PISTON_PROCESSING_TABLE group by date(DATE_TIME)"
        
            cur.execute(query)
            values=cur.fetchall()
            # print(values)
            Engine_number = values[0][1]
            # print(Engine_number)
            self.Total_label_5.setText(str(Engine_number))
        except Exception as e:
            print(e)
        return Engine_number

        #self.pushButton_cycletart.clicked.connect(self.pushotton_cycletart)
    def pushotton_cycletart(self):
        buttonReply = QMessageBox.question(self, 'Message', "Are you sure you want to update?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        self.customer_value = "1"
        if buttonReply == QMessageBox.Yes:                
            db_update = None
            cur = None
            START_INSPECTION= 1
            try:
                db_update = pymysql.connect(host=db_host, user=db_user, passwd=db_pass, db= db_name)
                cur = db_update.cursor()
                query = "UPDATE manual_trigger_table SET STATUS = %s WHERE ID = 1"
                cur.execute(query, (START_INSPECTION,))
                db_update.commit()
            except Exception as e:
                # print("Update_Program_No() Exception is : "+ str(e))
                logger.critical(f"Update_Program_No() Exception is : {e}, Traceback : {traceback.format_exc()}")
            finally:
                if cur is not None:
                    cur.close()
                if db_update is not None:
                    db_update.close()




    def Count_all_Engine(self):
        db_fetch = pymysql.connect(host = db_host,
                                    user = db_user,
                                    password = db_pass,
                                    db = db_name)
        cur = db_fetch.cursor()
        current_time = datetime.datetime.now()
        toDate=current_time.strftime("%Y-%m-%d")
        first_date=toDate+" 00:00:00"
        second_date=toDate+" 23:59:59"       
        query="SELECT COUNT(*) FROM rosr_db.rosr_processing_table where DATE_TIME between "+'"'+first_date+'"'+" and "+'"'+second_date+'"'+";"
        # query = "select count(ID) as TOTAL_COUNT, date(DATE_TIME) as DATE_TIME from PISTON_PROCESSING_TABLE group by date(DATE_TIME)"
       
        cur.execute(query)
        values=cur.fetchall()
        # print(values)
        Total_eng_count = values[0][0]
        # print("Total_eng_count",Total_eng_count)
        self.label_7.setText(str(Total_eng_count))

    def Total_Ok_Engine(self):
        global Total_ok_count
        db_fetch = pymysql.connect(host = db_host,
                                    user = db_user,
                                    password = db_pass,
                                    db = db_name)
        cur = db_fetch.cursor()
        current_time = datetime.datetime.now()
        toDate=current_time.strftime("%Y-%m-%d")
        first_date=toDate+" 00:00:00"
        second_date=toDate+" 23:59:59"  
        
        # if PISTON_1_STATUS_OK==None:
        query="SELECT COUNT(*) FROM rosr_db.rosr_processing_table where DEFECT LIKE 'OK' and DATE_TIME between "+'"'+first_date+'"'+" and "+'"'+second_date+'"'+" ;"
   
        cur.execute(query)
        values=cur.fetchall()
        # print(values)
        Total_ok_count = values[0][0]
        # print("Total_ok_count",Total_ok_count)
        self.label_5.setText(str(Total_ok_count))

        return Total_ok_count

    def Total_Notok_Engine(self):
        global Total_Notok_count
        db_fetch = pymysql.connect(host = db_host,
                                    user = db_user,
                                    password = db_pass,
                                    db = db_name)
        cur = db_fetch.cursor()
        current_time = datetime.datetime.now()
        toDate=current_time.strftime("%Y-%m-%d")
        first_date=toDate+" 00:00:00"
        second_date=toDate+" 23:59:59"    
        # query="SELECT COUNT(IS_OK) FROM PISTON_PROCESSING_TABLE;" 
        query="SELECT COUNT(*) FROM rosr_db.rosr_processing_table where DEFECT LIKE 'NOT_OK' and DATE_TIME between "+'"'+first_date+'"'+" and "+'"'+second_date+'"'+" ;"
            
        # query="SELECT COUNT(IS_OK) FROM PISTON_PROCESSING_TABLE WHERE IS_OK LIKE 'NOT OK' ;"        
        cur.execute(query)
        values=cur.fetchall()
        # print(values)
        Total_Notok_count = values[0][0]
        # print(Total_img_count)
        self.label_3.setText(str(Total_Notok_count))
        return Total_Notok_count



    def Start_process(self):
        plc_status = 0
        try:
            current_time = datetime.datetime.now()
            logger.debug("Start time : "+str(current_time))
            db_fetch = pymysql.connect(host = db_host,user = db_user,password = db_pass, db = db_name)
            cur = db_fetch.cursor()
            current_time = datetime.datetime.now() 
            secDiff = datetime.timedelta(seconds=10)
            logger.debug("Head is Visible")
            self.Count_all_Engine()
            self.Total_Ok_Engine()
            self.Total_Notok_Engine()
            imagelink,status=self.getROSORdaat()
            engine_number=self.Print_Engine_number()
            image=imagelink.replace("\\","/")
            self.label_2.setPixmap(QPixmap(image))
            #self.label_4.setPixmap(QPixmap(image_link_2))
            if status=="OK":
                self.label_8.setText(status)
                self.label_8.setAlignment(QtCore.Qt.AlignCenter)
                self.label_8.setStyleSheet("background-color: green; color: white;")
            elif status=="NOT_OK":
                self.label_8.setText(status)
                self.label_8.setAlignment(QtCore.Qt.AlignCenter)
                self.label_8.setStyleSheet("background-color: red; color: white;")
            self.fetch_details()
        except Exception as e:
            logger.critical(f"Start_process() Exception is : {e}")    
    
    def getPLCDBStatus(self):
        PLC_STATUS = 0
        try:
            db_object = pymysql.connect(host = db_host,user = db_user,password = db_pass, db = db_name)
            cur = db_object.cursor()
            query="SELECT PLC_STATUS FROM plc_status_table"
            cur.execute(query)
            data_set = cur.fetchall()
             
            for i in range(0, len(data_set)):
                PLC_STATUS = int(data_set[i][0]) 
    
        except Exception as e:
            logger.critical(f"getPLCDBStatus() Exception is : {e}")
        finally:
            cur.close()
            db_object.close()
        return PLC_STATUS

    def logout_clicked(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(" ")
        dlg.setText("Are you sure want to exit ?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec_()

        if button == QMessageBox.Yes:
            # print("Yes!")
            self.close()
        else:
            print("No!")

    def Download_report(self):
        from datetime import date, datetime

        fromDate=self.details_from_date.date()
        fromDate = fromDate.toString("yyyy-MM-dd")
        fromDate= fromDate+" 00:00:00"
        toDate=self.details_to_date.date()
        toDate = toDate.toString("yyyy-MM-dd")
        toDate = toDate+" 23:59:59"
        DefectWiseData = self.comboBox_2.currentText() 

        try:

            db_fetch = pymysql.connect(host = db_host,
                                        user = db_user,
                                        password = db_pass,
                                        db = db_name)
            cur = db_fetch.cursor()

            if DefectWiseData == "ALL":
                query="SELECT * FROM rosr_db.rosr_processing_table where DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"
                # query="SELECT DATE_TIME,ENGINE_TYPE,DEFECT,CAM1_IMG_LINK,CAM2_IMG_LINK FROM rosr_db.rosr_processing_table where DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"
        
            elif DefectWiseData == "OK":
                query="SELECT * FROM rosr_db.rosr_processing_table where DEFECT LIKE 'OK' and DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"

            elif DefectWiseData == "NOT_OK":
                query="SELECT * FROM rosr_db.rosr_processing_table where DEFECT LIKE 'NOT_OK' and  DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"    
            
            cur.execute(query)
            data_set = cur.fetchall()
            # print("Download data is :",data_set)
            cur.close()



            if not os.path.exists(DOWNLOAD_PATH+"/"+str(date.today())):
                # os.makedirs(DOWNLOAD_PATH+str(date.today()))
                os.mkdir(DOWNLOAD_PATH+"/"+str(date.today()))
            csv_path = DOWNLOAD_PATH+"/"+str(date.today())+"/"+str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            if not os.path.exists(csv_path):
                # os.makedirs(DOWNLOAD_PATH+str(date.today()))
                os.mkdir(csv_path)
            # csv_path = DOWNLOAD_PATH+"/"+str(date.today())+"/"+str(datetime.now())
            image_path = csv_path+"/Images"
            if not os.path.exists(image_path):
                # os.makedirs(image_path)   
                os.mkdir(image_path)         
            f = open(csv_path+"/"+'CSV_DATA.csv','w')
            dataStr = "DATE_TIME"+','+"ENGINE_TYPE"+','+"ENGINE_NUMBER"+','+"DEFECT"+','+"IMG_LINK",'+"IMG_LINK_2"+'
            f.write(str(dataStr) + '\n')
 
            for row in range(len(data_set)):                       
                dateTime = str(data_set[row][1])
                engineType = str(data_set[row][2])
                #opertor_label= str(data_set[row][2])
                engineNumber = str(data_set[row][3])
                defect = str(data_set[row][4])
                IMAGE_LINK_cam1 = str(data_set[row][5])
                #IMAGE_LINK_cam2 = str(data_set[row][6])
                IMAGE_LINK1 = os.path.basename(IMAGE_LINK_cam1)
                #IMAGE_LINK2 = os.path.basename(IMAGE_LINK_cam2)
                try:
                    shutil.copyfile(IMAGE_LINK_cam1,image_path+os.path.basename(os.path.normpath(IMAGE_LINK_cam1)))
                    #shutil.copyfile(IMAGE_LINK_cam2,image_path+os.path.basename(os.path.normpath(IMAGE_LINK_cam2)))
                except Exception as e:
                    print("Exception in copying image:",e)

                dataStr = dateTime+','+engineType+','+engineNumber+','+defect+','+os.path.basename(IMAGE_LINK1) 
                dataStr = str(dataStr)
                f.write(dataStr + '\n')    

            f.close()
           # self.show_message("The data has been downloaded ")     
           # QtWidgets.QMessageBox.information(self,"The data has been downloaded.#") 
            QtWidgets.QMessageBox.information(self,"Data Downloded","Data downloded in reports folder.")
        except Exception as e:
            print('Download_Data Exception :',e)       

    def getROSORdaat(self):
        try:
            imagelink=""
            status=""
            db_fetch = pymysql.connect(host ="localhost",
                                            user = "root",
                                            password = "insightzz123",
                                            db = "rosr_db") 
            cur = db_fetch.cursor()
            query="SELECT * FROM rosr_db.rosr_processing_table  order by id desc limit 1;;"
            cur.execute(query)
            data=cur.fetchall()
            for row in data:
                imagelink=row[5]
                status=row[4]
        except Exception as e:
            print(e)
        return imagelink,status


       
     

    def search(self):
        
        x=self.search_input.toPlainText()
        db_fetch = pymysql.connect(host = db_host,
                                user = db_user,
                                password = db_pass,
                                db = db_name)
        cur = db_fetch.cursor()
        # fromDate = str(self.de_fromDate.date().toPyDate())+ " 00:00:00"
        # toDate = str(self.de_toDate.date().toPyDate())+ " 23:59:00"
        # today = datetime.date.today()
        # self.fromDate.setDate(today)
        # self.todate_2.setDate(today)
        fromDate=self.details_from_date.date()
        fromDate = fromDate.toString("yyyy-MM-dd")
        fromDate =fromDate+" 00:00:00"
        toDate=self.details_to_date.date()
        toDate = toDate.toString("yyyy-MM-dd")
        toDate = toDate+" 23:59:59"

        query="SELECT * FROM rosr_db.rosr_processing_table where ENGINE_NUMBER = "+'"'+x+'"'+" and DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"
        try:
            cur.execute(query)
            values=cur.fetchall()
            # print(values)
            
            cur.close() 
            i=0
            self.details_tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(values):
                self.details_tableWidget.insertRow(row_number)

                DATE_TIME=row_data[1]
                ENGINE_TYPE=row_data[2]
                ENGINE_NUMBER=row_data[3] 
                DEFECT=row_data[4]               
                IMG_LINK=str(row_data[5])
                IMG_LINK_2=str(row_data[6])


                # self.details_tableWidget.setRowHeight(0,80)
                # self.details_tableWidget.setRowHeight(1,80)
                # self.details_tableWidget.setRowHeight(2,80)
                self.details_tableWidget.setItem(row_number,0, QtWidgets.QTableWidgetItem(str(DATE_TIME)))
                self.details_tableWidget.setItem(row_number,1, QtWidgets.QTableWidgetItem(str(ENGINE_TYPE)))
                self.details_tableWidget.setItem(row_number,2, QtWidgets.QTableWidgetItem(str(ENGINE_NUMBER)))
                self.details_tableWidget.setItem(row_number,3, QtWidgets.QTableWidgetItem(str(DEFECT)))
                self.details_tableWidget.setItem(row_number,5, QtWidgets.QTableWidgetItem(str(IMG_LINK)))
                self.details_tableWidget.setItem(row_number,6, QtWidgets.QTableWidgetItem(str(IMG_LINK_2)))
                # if IS_OK=="OK":
                #     self.details_tableWidget.setItem(row_number,4, QtWidgets.QTableWidgetItem(str(IS_OK)))
                # else:
                #     IS_OK=="NOT OK"
                #     self.details_tableWidget.setItem(row_number,4, QtWidgets.QTableWidgetItem(str(IS_OK)))


                qSelectButton = QtWidgets.QPushButton("VIEW_Image_Cam1")
                qSelectButton.clicked.connect(lambda checked, arg2=IMG_LINK: self.showIMAGE(arg2))                              
                        
                self.details_tableWidget.setCellWidget(row_number,4, qSelectButton) 

                # qSelectButton = QtWidgets.QPushButton("VIEW_Image_Cam2")               

                # qSelectButton.clicked.connect(lambda checked, arg2=IMG_LINK_2: self.showIMAGE_1(arg2))                              
                        
                self.details_tableWidget.setCellWidget(row_number,5, qSelectButton) 

        except Exception as e:
                QtWidgets.QMessageBox.about(self.frame,"Error Occured", str(e))       


    def fetch_details(self):
        global Total_img_count,Total_ok_img_count,Total_NOT_ok_img_count
     
        fromDate=self.details_from_date.date()
        fromDate = fromDate.toString("yyyy-MM-dd")
        fromDate= fromDate+" 00:00:00"
        toDate=self.details_to_date.date()
        toDate = toDate.toString("yyyy-MM-dd")
        toDate = toDate+" 23:59:59"
        DefectWiseData = self.comboBox_2.currentText() 

        db_fetch = pymysql.connect(host = db_host,
                                        user = db_user,
                                        password = db_pass,
                                        db = db_name)
        cur = db_fetch.cursor()
        if DefectWiseData == "ALL":
            query="SELECT * FROM rosr_db.rosr_processing_table where DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"
            # query="SELECT DATE_TIME,ENGINE_TYPE,DEFECT,CAM1_IMG_LINK,CAM2_IMG_LINK FROM rosr_db.rosr_processing_table where DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"
        
        elif DefectWiseData == "OK":
            query="SELECT * FROM rosr_db.rosr_processing_table where DEFECT LIKE 'OK' and DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"

        elif DefectWiseData == "NOT_OK":
            query="SELECT * FROM rosr_db.rosr_processing_table where DEFECT LIKE 'NOT_OK' and  DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"    
        try:
            cur.execute(query)
            values=cur.fetchall()
            # print(values)
            
            cur.close() 
            i=0
            self.details_tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(values):
                self.details_tableWidget.insertRow(row_number)
                #ID=row_data[0]
                DATE_TIME=row_data[1]
                ENGINE_TYPE=row_data[2]
                ENGINE_NUMBER=row_data[3] 
                DEFECT=row_data[4]               
                IMG_LINK=str(row_data[5])
                IMG_LINK_2=str(row_data[6])
                #PISTON_1_STATUS=str(row_data[5])
                # CAMERA_TYPE=str(row_data[5])


                
                self.details_tableWidget.setItem(row_number,0, QtWidgets.QTableWidgetItem(str(DATE_TIME)))
                self.details_tableWidget.setItem(row_number,1, QtWidgets.QTableWidgetItem(str(ENGINE_TYPE)))
                self.details_tableWidget.setItem(row_number,2, QtWidgets.QTableWidgetItem(str(ENGINE_NUMBER)))
                self.details_tableWidget.setItem(row_number,3, QtWidgets.QTableWidgetItem(str(DEFECT)))
                self.details_tableWidget.setItem(row_number,4, QtWidgets.QTableWidgetItem(str(IMG_LINK)))
                self.details_tableWidget.setItem(row_number,5, QtWidgets.QTableWidgetItem(str(IMG_LINK_2)))

                qSelectButton = QtWidgets.QPushButton("VIEW_Image_Cam_1")
                qSelectButton.clicked.connect(lambda checked, arg1=IMG_LINK: self.showIMAGE(arg1))                              
                        
                self.details_tableWidget.setCellWidget(row_number,4, qSelectButton) 


                #self.details_tableWidget.setItem(row_number,6, QtWidgets.QTableWidgetItem(str(IMG_LINK_2)))
                # qSelectButton = QtWidgets.QPushButton("VIEW_Image_Cam_2")               

                # qSelectButton.clicked.connect(lambda checked, arg2=IMG_LINK_2: self.showIMAGE_1(arg2))                              
                        
                # self.details_tableWidget.setCellWidget(row_number,5, qSelectButton) 

        except Exception as e:
            print(e)
        
    #is_window_open = 7
    def Graph(self):
        try:    
            plt.close()   
            now = datetime.datetime.now()
            current_date = now.strftime("%Y-%m-%d")

            # print("current_date :",current_date)
            from_date = self.from_dateEdit_reportDump.date().toPyDate()
            from_date_temp = from_date.strftime('%Y-%m-%d')

            to_date = self.to_dateEdit_reportDump.date().toPyDate() + timedelta(days=1)
            to_date_temp = to_date.strftime('%Y-%m-%d')
            
            fromDate = from_date_temp
            toDate = to_date_temp

            # print(f"fromDate : {fromDate}, to Date : {toDate}")

            db_fetch = pymysql.connect(host = db_host,
                                       user = db_user,
                                       passwd = db_pass,
                                       db = db_name)
            cur = db_fetch.cursor() 
            query = f'''SELECT 
                   SUM(IFNULL(CASE WHEN DEFECT = 'OK' THEN 1 END, 0)) AS ok_count,
                   SUM(IFNULL(CASE WHEN DEFECT = 'NOT OK' THEN 1 END, 0)) AS not_ok_count,
                   DATE_FORMAT(DATE_TIME, '%d_%m_%Y') AS fdate 
                   FROM rosr_db.rosr_processing_table 
                   WHERE DATE_TIME BETWEEN "{fromDate}" and "{toDate}" 
                   GROUP BY fdate;'''

            cur.execute(query)
            
            # data_set = cur.fetchall()
            # print("Graph dataset:",data_set)
            # cur.close()  
            # data_by_date = {}
            # # if data_set == " ":
            # #     self.summary_data_label.setText("No Data Found")
            # #if data_set[] > 0:
            # if data_set == " ":   
            #     self.summary_data_label.setText("No Data Found")   

            # else:
                  
            #     self.summary_data_label.setText("Graph Ploted")
            #     for row in data_set:
            #         date = datetime.datetime.strptime(row[2], '%d_%m_%Y').date()
            #         print("date :",date)
            #         ok_count = row[0]
            #         not_ok_count = row[1]
            #         if date in data_by_date:
            #             data_by_date[date]['ok_count'] += ok_count
            #             data_by_date[date]['not_ok_count'] += not_ok_count
            #         else:
            #             data_by_date[date] = {'ok_count': ok_count, 'not_ok_count': not_ok_count}

            #     # Create list of dates and corresponding OK and NOT OK counts
            #     date_list = []
            #     ok_count_list = []
            #     not_ok_count_list = []
            #     for date, counts in data_by_date.items():
            #         date_datetime = datetime.datetime.combine(date, datetime.time.min)
                    
            #         date_list.append(date_datetime)
            #         ok_count_list.append(counts['ok_count'])
            #         not_ok_count_list.append(counts['not_ok_count'])

            #     # Plot bar graph
            #     fig, ax = plt.subplots()
            #     width = 0.4
            #     ax.bar([d - datetime.timedelta(days=width/2) for d in date_list], ok_count_list, width=width, color='g', align='center', label='OK')
            #     ax.bar([d + datetime.timedelta(days=width/2) for d in date_list], not_ok_count_list, width=width, color='r', align='center', label='NOT OK')

            #     # Formatting date axis
            #     date_format = mdates.DateFormatter('%d-%m-%Y')
            #     ax.xaxis.set_major_formatter(date_format)
                
            #     ax.xaxis_date()
            #     ax.autoscale(tight=True)
            #     # Adding labels and legend
            #     ax.set_xlabel('Date')
            #     ax.set_ylabel('Count')
            #     ax.set_title('Engines Status')
            #     ax.legend()
            #     # Displaying graph
            #     plt.show()
            data_set = cur.fetchall()
            # print("Graph dataset:",data_set)
            cur.close()  
            data_by_date = {}
            if not data_set:   
                self.summary_data_label.setText("No Data Found")   
            else:
                self.summary_data_label.setText("Graph Plotted")
                for row in data_set:
                    date = datetime.datetime.strptime(row[2], '%d_%m_%Y').date()
                    ok_count = row[0]
                    not_ok_count = row[1]
                    if date in data_by_date:
                        data_by_date[date]['ok_count'] += ok_count
                        data_by_date[date]['not_ok_count'] += not_ok_count
                    else:
                        data_by_date[date] = {'ok_count': ok_count, 'not_ok_count': not_ok_count}

                # Create list of dates and corresponding OK and NOT OK counts
                date_list = []
                ok_count_list = []
                not_ok_count_list = []
                for date, counts in data_by_date.items():
                    date_datetime = datetime.datetime.combine(date, datetime.time.min)
                    
                    date_list.append(date_datetime)
                    ok_count_list.append(counts['ok_count'])
                    not_ok_count_list.append(counts['not_ok_count'])

                # Plot bar graph
                fig, ax = plt.subplots()
                width = 0.4
                
                # Filter out the dates for which there is no data
                filtered_dates = []
                filtered_ok_counts = []
                filtered_not_ok_counts = []
                xticks = []
                for i, date in enumerate(date_list):
                    if ok_count_list[i] or not_ok_count_list[i]:
                        filtered_dates.append(date - datetime.timedelta(days=width/2))
                        filtered_ok_counts.append(ok_count_list[i])
                        filtered_not_ok_counts.append(not_ok_count_list[i])
                        xticks.append(date)

                ax.bar(filtered_dates, filtered_ok_counts, width=width, color='g', align='center', label='OK')
                ax.bar([d + datetime.timedelta(days=width/2) for d in filtered_dates], filtered_not_ok_counts, width=width, color='r', align='center', label='NOT OK')

                # Formatting date axis
                date_format = mdates.DateFormatter('%d-%m-%Y')
                ax.xaxis.set_major_formatter(date_format)
                ax.set_xticks(xticks)
                ax.xaxis_date()
                ax.autoscale(tight=True)
                # Adding labels and legend
                ax.set_xlabel('Date')
                ax.set_ylabel('Count')
                ax.set_title('Engines Status')
                ax.legend()
                # Displaying graph
                plt.show()  


        except Exception as e:
            print("Exception is graph :",e)    
        
    def fetch_details1(self):
        
        db_fetch = pymysql.connect(host = db_host,
                                       user = db_user,
                                       password = db_pass,
                                       db = db_name)
        cur = db_fetch.cursor()
        fromDate=self.details_from_date.date()
        fromDate = fromDate.toString("yyyy-MM-dd")
        fromDate= fromDate+" 00:00:00"
        toDate=self.details_to_date.date()
        toDate = toDate.toString("yyyy-MM-dd")
        toDate = toDate+" 23:59:59"
        query="SELECT * FROM rosr_db.rosr_processing_table where DATE_TIME between "+'"'+fromDate+'"'+" and "+'"'+toDate+'"'+";"
        
        try:
            cur.execute(query)
            values=cur.fetchall()
            # print(values)
            
            cur.close() 
            i=0
            self.details_tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(values):
                self.details_tableWidget.insertRow(row_number)
                ID=row_data[0]
                ENGINE_TYPE=row_data[1]
                DATE_TIME=row_data[2]
                ENGINE_NUMBER=row_data[3]                
                IMG_LINK=str(row_data[4])
                IS_OK=str(row_data[5])
                # CAMERA_TYPE=str(row_data[5])


                # self.details_tableWidget.setRowHeight(0,80)
                # self.details_tableWidget.setRowHeight(1,80)
                # self.details_tableWidget.setRowHeight(2,80)
                self.details_tableWidget.setItem(row_number,0, QtWidgets.QTableWidgetItem(str(ID)))
                self.details_tableWidget.setItem(row_number,1, QtWidgets.QTableWidgetItem(str(ENGINE_TYPE)))
                self.details_tableWidget.setItem(row_number,2, QtWidgets.QTableWidgetItem(str(DATE_TIME)))
                self.details_tableWidget.setItem(row_number,3, QtWidgets.QTableWidgetItem(str(ENGINE_NUMBER)))
                self.details_tableWidget.setItem(row_number,4, QtWidgets.QTableWidgetItem(str(IS_OK)))


                self.details_tableWidget.setItem(row_number,5, QtWidgets.QTableWidgetItem(str(IMG_LINK)))
                qSelectButton = QtWidgets.QPushButton("VIEW_Image")
                qSelectButton.clicked.connect(lambda checked, arg2=IMG_LINK: self.showIMAGE(arg2))                              
                        
                self.details_tableWidget.setCellWidget(row_number,5, qSelectButton) 
        except Exception as e:
                QtWidgets.QMessageBox.about(self.frame,"Error Occured", str(e))  

    
    def cam_Health(self):
        device_info_list = pylon.TlFactory.GetInstance().EnumerateDevices()
        # print(len(device_info_list))
        if len(device_info_list) > 0:
            db_update = pymysql.connect(host = db_host,
                                       user = db_user,
                                       password = db_pass,
                                       db = db_name)
            cur = db_update.cursor()
            query = "UPDATE CAM_HEALTH_TABLE set HEALTH_STATUS = 'CONNECTED';"
            cur.execute(query)
            db_update.commit()
            cur.close()
        else:
            db_update = pymysql.connect(host = db_host,
                                       user = db_user,
                                       password = db_pass,
                                       db = db_name)
            cur = db_update.cursor()
            query = "UPDATE CAM_HEALTH_TABLE set HEALTH_STATUS = 'NOT CONNECTED';"
            cur.execute(query)
            db_update.commit()
            cur.close()

        db_fetch = pymysql.connect(host = db_host,
                                       user = db_user,
                                       password = db_pass,
                                       db = db_name)
        cur = db_fetch.cursor()        
        query="SELECT * FROM rosr_db.CAM_HEALTH_TABLE;"
        try:
            cur.execute(query)
            values=cur.fetchall()
            # print(values)
            cur.close()             
            self.details_tableWidget_cam_health.setRowCount(0)
            for row_number, row_data in enumerate(values):
                self.details_tableWidget_cam_health.insertRow(row_number)
                cam=row_data[1]
                status=row_data[2]  
                
                self.details_tableWidget_cam_health.setRowHeight(0,80)
                self.details_tableWidget_cam_health.setRowHeight(1,80)
                # self.details_tableWidget_cam_health.setRowHeight(2,80)
                # self.details_tableWidget_cam_health.setRowHeight(3,80)


                self.details_tableWidget_cam_health.setItem(row_number,0, QtWidgets.QTableWidgetItem(str(cam)))
                self.details_tableWidget_cam_health.setItem(row_number,1, QtWidgets.QTableWidgetItem(str(status)))
                if "CONNECTED" != status:
                    self.details_tableWidget_cam_health.item(row_number,1).setBackground(QtGui.QColor(255,0,0))
                else:
                    self.details_tableWidget_cam_health.item(row_number,1).setBackground(QtGui.QColor(0,255,0))
                      
                        
        except Exception as e:
                QtWidgets.QMessageBox.about(self.inf_frame,"Error Occured", str(e))  

   
    def showIMAGE(self,arg1):
        global imagewindow_object
        # print("Inside showIMAGE")
        imagewindow_object.loadImage(arg1)
    
    def showIMAGE_1(self,arg2):
        global imagewindow_object
        # print("Inside showIMAGE")
        imagewindow_object.loadImage_cam1(arg2)


    

  
#===========================Login Window===================================#
class login(QtWidgets.QMainWindow, Ui_Login):
    def __init__(self, *args, obj=None, **kwargs):
        super(login, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Drishti - Machine Vision Plateform")
        self.Enter_pushButton.clicked.connect(self.login)
        self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        
    #=====================Enter key press event============================#
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.login()    
    
    #===================== Login func start===============================#    
    def login(self):
        username = str(self.username_lineEdit.text())
        print(username)
        password = str(self.password_lineEdit.text())
        print(password)
        if username == "MHEL" and password == "mhel@123":
            # mainwindow_object.show()
            # login_object.close()
            pass
        
        elif username == "" and password == "":
            self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Login", "Username or Password can not be empty!"))
        elif username != "MHEL":
            self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Login", "Username wrong!"))
        elif password != "":
            self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Login", "Password wrong!"))
        else:
            try:
                db_fetch = pymysql.connect(host = db_host,
                                           user = db_user,
                                           passwd = db_pass,
                                           db = db_name)
                cur = db_fetch.cursor()
                query = "select USER_NAME, PASSWORD from login"
                cur.execute(query)
                data_set = cur.fetchall()
                # print(data_set)
                cur.close()
                for row in range (0, len(data_set)):
                    if username == data_set[row][1] and password == data_set[row][2]:
                        
                        self.username_label.clear()
                        self.password_label.clear()
                        self.wrong_cred_label.clear()
                    elif username == data_set[row][0] and password != data_set[row][1]:
                        self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Please, enter valid password"))
                    elif username != data_set[row][0] and password == data_set[row][1]:
                        self.wrong_cred_label.setText(QtCore.QCoreApplication.translate("Please, enter valid username"))
                        
                    #mainwindow_object.update_cam_health()
                    #mainwindow_object.timer_cam_health.start(5000)                    
                        
            except Exception as e:
                print('Exception in Login:', e)
                

#============================Image window class=============================#
class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)      

#============================Image window class=============================#
class ImageWindow(QtWidgets.QWidget):
    def __init__(self):
        super(ImageWindow, self).__init__()
        self.viewer = PhotoViewer(self)
        self.imagepath = "" 
        self.update_button = QtWidgets.QPushButton(self)
        self.update_button.setGeometry(QtCore.QRect(200, 0, 130, 40))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.update_button.setFont(font)
        self.update_button.setObjectName("update_button")
        self.update_button.setText(QtCore.QCoreApplication.translate("ImageviewWindow", ""))
        # self.update_button.clicked.connect(self.update_table)

        font = QtGui.QFont()
        font.setPointSize(15)
        self.notdefect_checkbox = QtWidgets.QCheckBox(self)
        self.notdefect_checkbox.setFont(font)
        self.notdefect_checkbox.setAutoFillBackground(True)
        self.notdefect_checkbox.setIconSize(QtCore.QSize(30, 30))
        # self.notdefect_checkbox.setObjectName("notdefect_checkbox")
        # self.notdefect_checkbox.setText(QtCore.QCoreApplication.translate("ImageviewWindow", "Not a deftect"))        
       
        self.viewer.photoClicked.connect(self.photoClicked)
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        HBlayout.addWidget(self.update_button)                
        HBlayout.addWidget(self.notdefect_checkbox)        
        VBlayout.addLayout(HBlayout)
        self.imagepath = ""        

    def loadImage(self, imagelink):
        self.close()        
        self.setGeometry(100, 100, 800, 600)
        self.show()
        self.notdefect_checkbox.setChecked(False)        
        self.imagepath = imagelink        
        self.viewer.setPhoto(QtGui.QPixmap(imagelink))

    def loadImage_cam1(self, imagelink):
        self.close()        
        self.setGeometry(100, 100, 800, 600)
        self.show()
        self.notdefect_checkbox.setChecked(False)        
        self.imagepath = imagelink        
        self.viewer.setPhoto(QtGui.QPixmap(imagelink))

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode()  == QtWidgets.QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))
 
        
    def show_message(self, message):
        choice = QMessageBox.information(self, 'Message!',message)

 
  
#=============================Report parameters class=========================#
class VersionWindow(QtWidgets.QMainWindow):
    def __init__(self,*args,**kwargs):
        super(VersionWindow,self).__init__(*args,**kwargs)
        self.setupUi(self)
# def location_on_screen(self):
#     ag=QtWidgets.QDesktopWidget().availableGeometry()
#     x=ag.width()
#     y=0
#     mainwindow.move(x,y)

def call_algo():
    p1=subprocess.run(['python',"C:/INSIGHTZZ/ROSR_ALGO/ALGORITHM/ROSOR_ALGO_V5.py"])

def call_frame_cap():
    #pass
    p=subprocess.run(['python','C:/INSIGHTZZ/ROSR_ALGO/ALGORITHM/FRAME_capture_v4.py'])
#========================class object defined=============================#    
if __name__=='__main__':
    # app = QtWidgets.QApplication(sys.argv)
    # mainwindow = QtWidgets.QMainWindow()
    # ui=mainwindow()
    # ui.setupUi(mainwindow)
    # ui.location_on_screen()
    # mainwindow.show()
    # p=Process(target=call_algo)
    # p.start()

    

    # # p2=threading.Thread(target=ui.startLoop)
    # # p2.start()
    # sys.exit(app.exec_())
    #global imagewindow_object

    app = QtWidgets.QApplication(sys.argv)   
    # login_object = login()
    
    mainwindow_object = mainwindow()
    # mainwindow_object.location_on_screen()
    mainwindow_object.show()
    imagewindow_object= ImageWindow()

    # p=Process(target=call_frame_cap)
    # p.start()
    p1=Process(target=call_algo)
    p1.start()
    # imagewindow_object= ImageWindow()
    app.exec()      