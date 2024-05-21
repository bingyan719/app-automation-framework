import sys
import os
from ftplib import FTP

_XFER_FILE = 'FILE'
_XFER_DIR = 'DIR'


class Xfer(object):
    '''''
    @note: upload local file or dirs recursively to ftp server
    '''

    def __init__(self):
        self.ftp = None

    def __del__(self):
        pass

    def setFtpParams(self, ip, uname, pwd, port=2121, timeout=120):
        self.ip = ip
        self.uname = uname
        self.pwd = pwd
        self.port = port
        self.timeout = timeout

    def initEnv(self):
        if self.ftp is None:
            self.ftp = FTP()
            print('### connect ftp server: %s ...' % self.ip)
            self.ftp.encoding = 'UTF-8'
            self.ftp.connect(self.ip, self.port, self.timeout)
            self.ftp.login(self.uname, self.pwd)
            print(self.ftp.getwelcome())

    def clearEnv(self):
        if self.ftp:
            self.ftp.close()
            print('### disconnect ftp server: %s!' % self.ip)
            self.ftp = None

    def uploadDir(self, localdir='./', remotedir='./screenshots'):
        try:
            if not os.path.isdir(localdir):
                return
            self.ftp.cwd(remotedir)
            for file in os.listdir(localdir):
                src = os.path.join(localdir, file)
                if os.path.isfile(src):
                    self.uploadFile(src, file)
                elif os.path.isdir(src):
                    try:
                        self.ftp.mkd(file)
                    except Exception:
                        sys.stderr.write('the dir is exists %s' % file)
                    self.uploadDir(src, file)
            self.ftp.cwd('..')
        except Exception:
             print ("Upload  error")

    def uploadFile(self, localpath, remotepath='./screenshots'):
        if not os.path.isfile(localpath):
            return

        print('+++ upload %s to %s:%s' % (localpath, self.ip, remotepath))
        self.ftp.storbinary('STOR ' + remotepath, open(localpath, 'rb'))

    def __filetype(self, src):
        if os.path.isfile(src):
            index = src.rfind('\\')
            if index == -1:
                index = src.rfind('/')
            return _XFER_FILE, src[index + 1:]
        elif os.path.isdir(src):
            return _XFER_DIR, ''

    def upload(self, src, remotepath='./screenshots'):
        filetype, filename = self.__filetype(src)
        self.initEnv()
        if filetype == _XFER_DIR:
            self.srcDir = src
            self.uploadDir(self.srcDir, remotepath)
        elif filetype == _XFER_FILE:
            self.uploadFile(src, remotepath)

    def isExist(self, path):
        self.initEnv()
        L = self.ftp.nlst(path)
        if len(L) > 0:
            return True
        else:
            return False
        self.clearEnv()

    def DownLoadFile(self, LocalFile, RemoteFile):
        file_handler = open(LocalFile, 'wb')
        print(file_handler)
        self.ftp.retrbinary('RETR ' + RemoteFile, file_handler.write)
        file_handler.close()
        return True

    def DownLoadFileTree(self, LocalDir, RemoteDir):
        try:
            self.initEnv()
            print("remoteDir:", RemoteDir)
            if not os.path.exists(LocalDir):
                os.makedirs(LocalDir)
            self.ftp.cwd(RemoteDir)
            RemoteNames = self.ftp.nlst()
            print("RemoteNames", RemoteNames)
            for file in RemoteNames:
                Local = os.path.join(LocalDir, file)
                print(self.ftp.nlst(file))
                if file.find(".") == -1:
                    if not os.path.exists(Local):
                        os.makedirs(Local)
                    self.DownLoadFileTree(Local, file)
                else:
                    self.DownLoadFile(Local, file)
            self.ftp.cwd("..")
            self.ftp.getwelcome

        except Exception:
             print ("Download Baseline error")
        return
