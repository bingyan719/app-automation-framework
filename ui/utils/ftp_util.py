import getopt
import sys
import ftplib
import os
import traceback
from enum import Enum, unique

from ui.utils import constant


class FTPError(object):

    def __init__(self, path, error, file_directory, du_type):
        """
        Create an instance of this class if an error occur while downloading and uploading.
        :param path: File/folder path which reasoned error.
        :param error: Error explanation.
        :param file_directory: 'f' for file, 'd' for folder.
        :param du_type: 'u' for upload, 'd' for download.
        :return: None
        """
        self.path = path
        self.error = error
        self.file_directory = file_directory
        self.du_type = du_type


@unique
class DUType(Enum):
    upload_file = 0
    upload_dir = 1
    download_file = 2
    download_dir = 3


class FTPClient(object):

    def __init__(self):
        """
        FTPClient class that establishes connection to the FTP server.
        Downloads all the files in the current folder (and sub folders if specified).
        Uploads all the files in the current folder to remote server
        :return: None
        """
        self.connection_status = 0  # 1 connected, 0 not connected
        self._connection = None
        self.error_list = []

    def cwd(self, home_dir):
        if self.connection_status != 1:
            print('A connection to FTP server must be established first.')
            return
        self._connection.cwd(home_dir)

    def connect(self, url, port=21, username="", password=""):
        """
        Establishes connection to the FTP server with username and password
        :param url: FTP server address, do not add "ftp://" to beginning.
        :param port: port for FTP server, default is 21.
        :param username: Username for FTP server, leave blank if there is not.
        :param password: Password for FTP server, leave blank if there is not.
        :return: Returns True if connection is established successfully.
        """
        print('url: {}'.format(url))
        print('port: {}'.format(port))
        print('username: {}'.format(username))
        print('password: {}'.format(password))
        # Check if connection is still alive and if not, drop it.
        if self._connection is not None:
            try:
                self._connection.pwd()
            except ftplib.all_errors:
                self._connection = None

        # Real reconnect
        if not (self._connection is None):
            self.connection_status = 1
            return
        ftp = ftplib.FTP()
        try:
            ftp.encoding = 'UTF-8'
            ftp.connect(url, port=port)
            # if FTP server is public, there is no need to use username
            # and password parameters
            if username == "" and password == "":
                ftp.login()
            else:
                ftp.login(user=username, passwd=password)
            self._connection = ftp
            self.connection_status = 1
            # connection established successfully to the server.
        except ftplib.all_errors as e:
            msg = 'connect ftp server has an problem, aborting...'
            print(msg)
            raise RuntimeError(msg)

    def download(self, remote, local, sub_folders='R', du_type=0):
        if self.connection_status != 1:
            print('A connection to FTP server must be established first.')
            return
        del self.error_list[:]
        # first create local directory if need
        if not os.path.exists(local):
            print('Create local directory')
            os.makedirs(local)
        print('du_type:{} type: {}'.format(du_type, type(du_type)))
        if du_type == 2:
            self.__download_file(remote, local)
        elif du_type == 3:
            self.__download_dir(remote, local, sub_folders)
        else:
            print('Unknown download type')
        return self.error_list

    def upload(self, local, remote, du_type=0):
        if self.connection_status != 1:
            print('A connection to FTP server must be established first.')
            return
        del self.error_list[:]
        if os.path.isfile(local) and du_type == 0:
            self._upload_file(local, remote)
        elif os.path.isdir(local) and du_type == 1:
            self._upload_dir(local, remote)
        else:
            print('upload must be a file or directory')
        return self.error_list

    def disconnect(self):
        """
        Closes connection to the FTP server
        :return: None
        """
        if not isinstance(self._connection, type(None)):
            self._connection.close()
            self._connection = None

    def _upload_file(self, local_file, remote_dir):
        try:
            # first, route to the given remote directory
            self.__route_to_remote_directory(remote_dir)
            current_remote_dir = self._connection.pwd()
            print('current entered remote directory:{}'.format(current_remote_dir))
            base_name = os.path.basename(local_file)
            print('base_name: ' + base_name)
            self.__upload_file_without_route(local_file, base_name)
        except:
            self.error_list.append(FTPError(local_file, sys.exc_info()[1], 'f', 'u'))

    def _upload_dir(self, local_dir, remote_dir):
        try:
            print('begin upload directory from {} to {}'.format(local_dir, remote_dir))
            if not os.path.exists(local_dir):
                print('local directory: {} not exist, abort it.'.format(local_dir))
                return
            # first, route to the given remote directory
            self.__route_to_remote_directory(remote_dir)
            current_remote_dir = self._connection.pwd()
            print('current entered remote directory:{}'.format(current_remote_dir))
            for item in os.listdir(local_dir):
                item_path = os.path.join(local_dir, item)
                print('item_path:{}, item:{}'.format(item_path, item))
                if os.path.isfile(item_path):
                    self.__upload_file_without_route(item_path, item)
                else:
                    # exclude apk resources directory
                    if item == 'resources':
                        continue
                    # create remote directory first
                    try:
                        self._connection.mkd(item)
                    except:
                        print('bad thing happen, should never throw this...')
                    self._upload_dir(item_path, item)
        except:
            traceback.print_exc()
            self.error_list.append(FTPError(local_dir, sys.exc_info()[1], 'd', 'u'))
        finally:
            # back to last directory
            self._connection.cwd('..')

    def __upload_file_without_route(self, local, remote_file_name):
        print('begin upload file from {} to {}'.format(local, remote_file_name))
        with open(local, 'rb') as lf:
            self._connection.storbinary('STOR {}'.format(remote_file_name), lf, 8 * 1024)
        print('end upload file from {} to {}'.format(local, remote_file_name))

    def __route_to_remote_directory(self, to_remote_dir):
        # judge remote directory has sub-directory or not
        try:
            to_remote_dir.index('/')
        except:
            # means that maybe just a directory
            print("route to remote directory except")
            self.__try_cwd_fail_to_create(to_remote_dir)
        else:
            # if has sub directory, split it and enter it
            print("route to remote directory else")
            remote_dirs = to_remote_dir.split('/')
            for remote_dir in remote_dirs:
                self.__try_cwd_fail_to_create(remote_dir)

    def __try_cwd_fail_to_create(self, remote_dir):
        print("try cwd to remote directory.")
        try:
            self._connection.cwd(remote_dir)
            return
        except:
            print('try to change current directory:{} has failed.'.format(remote_dir))
        # create remote directory
        print('try to create remote directory')
        try:
            self._connection.mkd(remote_dir)
            # enter remote directory again
            print('create remote directory:{} success, and enter it again.'.format(remote_dir))
            self._connection.cwd(remote_dir)
        except:
            print('create remote directory:{} has failed, should never happen.'.format(remote_dir))

    def __download_file(self, remote_file, local_dir):
        try:
            # change current path to download file's directory
            remote_path_dirs = remote_file.split('/')
            size = len(remote_path_dirs)
            c_size = 0
            # means that there are a directory in path
            if size >= 2:
                # iterator all remote path directory and cwd it
                for remote_path_dir in remote_path_dirs:
                    print('Change workspace to {}'.format(remote_path_dir))
                    self._connection.cwd(remote_path_dir)
                    c_size += 1
                    # reach end, jump out of this for loop
                    if c_size == size - 1:
                        break
            print('current path: {}'.format(self._connection.pwd()))
            # changing working directory in local machine
            os.chdir(local_dir)
            # download target file in current folder
            base_name = os.path.basename(remote_file)
            self.__download_one_file(base_name)
        except:
            self.error_list.append(FTPError(remote_file, sys.exc_info()[1], 'f', 'd'))

    def __download_dir(self, remote_dir, local_dir, sub_folders='R'):
        try:
            print('downloading remote directory : {}'.format(remote_dir))
            # changing working directory at FTP server
            self._connection.cwd(remote_dir)
            # changing working directory in local machine
            os.chdir(local_dir)
            files = self.__get_file_list()
            # download each file in current folder
            for file in files:
                self.__download_one_file(file)
            if sub_folders == 'R':
                folders = self.__get_folder_list()
                for folder in folders:
                    if folder not in ('.', '..'):
                        if remote_dir == '/':
                            remote_dir = ''
                        os.chdir(local_dir)
                        if not os.path.exists(folder):
                            os.mkdir(folder)
                        if os.name == 'nt':
                            self.__download_dir(folder, local_dir + '\\' + folder)
                        else:
                            self.__download_dir(folder, local_dir + '/' + folder)
        except:
            self.error_list.append(FTPError(remote_dir, sys.exc_info()[1], 'd', 'd'))
        else:
            # when all done successfully, back to parent folder
            self._connection.cwd('..')

    def __download_one_file(self, remote_file_name):
        try:
            with open(remote_file_name, 'wb') as f:
                self._connection.retrbinary('RETR {}'.format(remote_file_name), f.write)
                print('File copied : {}'.format(remote_file_name))
        except Exception as e:
            print(e)
            print('Error occurred : {}'.format(remote_file_name))
            raise RuntimeError('Download file has an exception.')

    def __get_file_list(self):
        """
        Gets file list in the current working directory at FTP server.
        :return: File list in current directory.
        """
        files = []

        def file_callback(line):
            items = line.split()
            if items[0][0] != 'd':  # not 'd' if item is file
                # ninth (index 8) and later elements creates file name
                # joining with ' ', if file name has blank space
                files.append(' '.join(items[8:]))

        self._connection.dir(file_callback)
        return files

    def __get_folder_list(self):
        """
        Gets folder list in the current working directory at FTP server.
        :return: Folder list in current directory.
        """
        folders = []

        def dir_callback(line):
            items = line.split()
            if items[0][0] == 'd':  # 'd' if item is folder
                # ninth (index 8) and later elements creates folder name
                # joining with ' ', if folder name has blank space
                folders.append(' '.join(items[8:]))

        self._connection.dir(dir_callback)
        return folders

def connect_ftp():
    print('enter connect ftp server')
    try:
        ftp_client = FTPClient()
        ftp_client.connect(constant.FTP_SERVER, port=constant.FTP_PORT, username=constant.FTP_USER,
                           password=constant.FTP_PASSWORD)
        return ftp_client
    except:
        print('connect ftp server failed...')
        exit()