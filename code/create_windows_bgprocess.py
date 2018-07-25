import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os
import time 
import sys
from app import twitterCrawlingService

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "twitterCrawlingService"
    _svc_display_name_ = "Twitter Crawling Service"
    # tell win32serviceutil we have a custom executable and custom args
    # so registration does the right thing.
    _exe_name_ = sys.executable
    _exe_args_ = '"' + os.path.abspath(sys.argv[0]) + '"'

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self._logger.info("Service Is Starting")
        crawl()


def crawl():
   while True:
       twitterCrawlingService()
       # sleep(10)
        
if __name__ == '__main__':
   if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
   else:
       win32serviceutil.HandleCommandLine(AppServerSvc)


    
    
    
