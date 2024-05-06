import snap7
from snap7 import util
import time
MAX_RETRY_ATTEMPTS = 1
RETRY_DELAY = 0.1
import logging
import os
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
class PLCCommunication:
    def __init__(self):
        self.PLC_IP_ADDRESS = '10.192.243.21' 
        self.DB_READ_NUMBER = 4036
        start=28
        part_present=30
        readecnnumber=0
        readenginenumber=10
        readheart=26

        writehear=74
        writeecnnumber=50
        writeenginnumber=60
        writeresult=76
    
    def createConnection(self):
        # logger.debug("Inside createCOnnection")
        client = None
        try:
            client = snap7.client.Client()
            # client.connect(self.PLC_IP_ADDRESS,0,1)
            client.connect(self.PLC_IP_ADDRESS,0,2)
        except Exception as e:
            print(e)
            logger.critical("createCOnnection() Exception is : "+ str(e))
        
        return client

    def isPLCConnected(self, clientConn):
        isConnected = False
        try:
            clientConn.get_connected()
            #time.sleep(0.2)
            clientConn.get_connected()
            isConnected = True
           # print("PLC CONNECT")
        except Exception as e:
            logger.critical("isPLCConnected() Exception is : "+ str(e))
            isConnected = False
        
        return isConnected

    def closePLCConnection(self, clientConn):
        try:
            clientConn.destroy()
        except Exception as e:
            logger.critical("closePLCConnection() Exception is : "+ str(e))

    ''' Read PLC Functions '''
    def readIntFromPLC(self, clientConn, db_col_start_buffer_pos): 
        row_data = None
        # db_col_start_buffer_pos = 258
        try:
            if self.isPLCConnected(clientConn) is True:
                db = clientConn.db_read(self.DB_READ_NUMBER, db_col_start_buffer_pos, 2) 
                row_data = util.get_int(db, 0)
             #   print(row_data)
            else:

                logger.debug("PLC not connected")
        except Exception as e:
            logger.critical("readIntFromPLC() Exception is : "+ str(e))
        return row_data

    def readBoolFromPLC(self, clientConn, db_col_start_buffer_pos):
        time.sleep(0.2)
        row_data = None
       # db_col_start_buffer_pos = 18.1
        try:
            if self.isPLCConnected(clientConn) is True:
                db = clientConn.db_read(self.DB_READ_NUMBER, db_col_start_buffer_pos, 1) #1
                print(db)
                row_data = util.get_bool(db, 0 ,0)
                print(f"Read Bool value {row_data}")
            else:
                logger.debug("PLC not connected")
        except Exception as e:
            logger.critical("readBoolFromPLC() Exception is : "+ str(e))
        return row_data

    def readDoubleFromPLC(self, clientConn, db_col_start_buffer_pos):
        row_data = None
        # db_col_start_buffer_pos = 260
        try:
            if self.isPLCConnected(clientConn) is True:
                db = clientConn.db_read(self.DB_READ_NUMBER, db_col_start_buffer_pos, 4) 
                #print(db)
                row_data = util.get_dint(db, 0)
                print(f"Read Double value {row_data}")
            else:
                logger.debug("PLC not connected")
        except Exception as e:
            logger.critical("readDoubleFromPLC() Exception is : "+ str(e))
        return row_data

    def readStringFromPLC(self, clientConn, db_col_start_buffer_pos):
        row_data = None
        ERROR_CODE=0
        # db_col_start_buffer_pos = 2
        try:
            for _ in range(MAX_RETRY_ATTEMPTS):
                time.sleep(0.2)
                if self.isPLCConnected(clientConn) is True:
                    db = clientConn.db_read(self.DB_READ_NUMBER, db_col_start_buffer_pos, 25)  
                    row_data = db[2:].decode("utf-8")
                else:
                    print("PLC isPLCConnected(clientConn) is False ")
                    logger.debug("PLC not connected")
        except Exception as e:
            print("readStringFromPLC() Exception is :",e)
            ERROR_CODE=1
            logger.critical("readStringFromPLC() Exception is : "+ str(e))
            time.sleep(0.2)
        return row_data,ERROR_CODE

    ''' Write PLC Functions '''        
    def writeBoolToPLC(self, clientConn, db_col_start_buffer_pos , bool_value):
        try:
            for _ in range(MAX_RETRY_ATTEMPTS):
                if self.isPLCConnected(clientConn) is True:
                    data = bytearray(1)
                    util.set_int(data,db_col_start_buffer_pos,0,bool_value)
                    clientConn.db_write(self.DB_READ_NUMBER,db_col_start_buffer_pos,data)
                    # print("Writing Done")
                else:
                    logger.debug("PLC not connected")
        except Exception as e:
            logger.critical("writeBoolToPLC() Exception is : "+ str(e))
            print("writeBoolToPLC() Exception is : "+ str(e))

    def writeIntToPLC(self, clientConn, db_col_start_buffer_pos , int_value,):
        try:
            if self.isPLCConnected(clientConn) is True:
                data = bytearray(2)
                util.set_int(data,db_col_start_buffer_pos,int_value)
                clientConn.db_write(self.DB_READ_NUMBER,db_col_start_buffer_pos,data)
                # print("Writing Done")
            else:
                logger.debug("PLC not connected")
        except Exception as e:
            logger.critical("writeIntToPLC() Exception is : "+ str(e))

    def writeDoubleToPLC(self, clientConn, db_col_start_buffer_pos, double_value):
        try:
            if self.isPLCConnected(clientConn) is True:
                data = bytearray(4)
                util.set_dint(data,db_col_start_buffer_pos,double_value)
                clientConn.db_write(self.DB_READ_NUMBER,db_col_start_buffer_pos,data)
                # print("Writing Done")
            else:
                time.sleep(0.2)
                logger.debug("PLC not connected")
        except Exception as e:
            time.sleep(0.2)
            logger.critical("writeDoubleToPLC() Exception is : "+ str(e))
            print("writeDoubleToPLC() Exception is : "+ str(e))

    def writeStringToPLC(self, clientConn, db_col_start_buffer_pos,string_value):
        try:
            if self.isPLCConnected(clientConn) is True:
                SPACE_START = " "
                SPACE_END = "  "
                concat_string = string_value + SPACE_END
                byte_value = concat_string.encode('utf-8')
                clientConn.db_write(self.DB_READ_NUMBER,db_col_start_buffer_pos, data=bytearray(byte_value))
                # str1 = byte_value.decode('UTF-8')  
                # print("Writing Done : "+ str1)
            else:
                logger.debug("PLC not connected")
        except Exception as e:
            logger.critical("writeStringToPLC() Exception is : "+ str(e))


# plcIPAddress = '10.192.243.21'
# Read_postion = 4036
# # Write_Position = 4035
# plcCommunicationObj = PLCCommunication(plcIPAddress, Read_postion) 
# clientConn = plcCommunicationObj.createConnection()
# start=plcCommunicationObj.readIntFromPLC(clientConn,28,Read_postion)
# print(start)
# esn=plcCommunicationObj.readStringFromPLC(clientConn,0,Read_postion)
# print(esn)
# engine=plcCommunicationObj.readStringFromPLC(clientConn,10,Read_postion)
# print(engine)
# part_present=plcCommunicationObj.readIntFromPLC(clientConn,30,Read_postion)
# print(part_present)
# # engine="0301BAM06570N"
# # writeenginenumer=plcCommunicationObj.writeStringToPLC(clientConn,)
# heart=plcCommunicationObj.readIntFromPLC(clientConn,26,Read_postion)
# print(heart)
# ecn="TVR6D613960301BAM06570N"
# enginenumber="0301BAM06570N"
# writeesn=plcCommunicationObj.writeStringToPLC(clientConn,50,ecn)
# writeesn=plcCommunicationObj.writeStringToPLC(clientConn,60,enginenumber)

# writeresult=plcCommunicationObj.writeIntToPLC(clientConn,76,5,Read_postion)
# # counter=0
# while True:
#     time.sleep(0.4)
#     counter=1
#     writehb=plcCommunicationObj.writeIntToPLC(clientConn,74,counter,Read_postion)
#     counter=counter+1
#     writehb=plcCommunicationObj.writeIntToPLC(clientConn,74,counter,Read_postion)
    
    
