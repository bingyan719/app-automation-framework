import datetime

import MySQLdb

from ui.utils import constant
from ui.utils.config import Settings
from ui.utils.log import Logging


def get_db_connection(mode):
    host = constant.DB_HOST
    port = int(constant.DB_PORT)
    user = constant.DB_USER
    pswd = constant.DB_PASSWROD
    if mode == 'debug':
        dbname = 'icyiy_site_debug'
    else:
        dbname = 'icyiy_site'
    conn = MySQLdb.connect(
        host=host,
        port=port,
        user=user,
        passwd=pswd,
        db=dbname,
        charset='utf8'
    )
    return conn

def get_test_platform_db_connection(mode):
    host = constant.DB_HOST
    port = int(constant.DB_PORT)
    user = constant.DB_USER
    pswd = constant.DB_PASSWROD
    if mode == 'debug':
        dbname = 'test_platform_debug'
    else:
        dbname = 'test_platform'
    conn = MySQLdb.connect(
        host=host,
        port=port,
        user=user,
        passwd=pswd,
        db=dbname,
        charset='utf8'
    )
    return conn

def select_version(mode, platform, device_brand, device_name, project_name):
    try:
        conn = get_db_connection(mode)
        with conn.cursor() as cursor:
            sql_select = "SELECT version FROM project_version where project_name ='{0}' and " \
                        "platform = '{1}' and device_brand = '{2}' and device_name= '{3}' order by id desc limit 1".format(
                        project_name, platform, device_brand, device_name)
            cursor.execute(sql_select)
            for version in cursor:
                return version[0]
        return ''
    finally:
        if conn:
            conn.close()

def insert_version(mode, version, platform, device_brand, device_name, project_name):
    try:
        conn = get_db_connection(mode)
        same_sql = 'select count(*) from project_version where project_name="{}" and version="{}" and platform="{}" and device_brand="{}" and device_name="{}"'.format(project_name, version, platform, device_brand, device_name)
        with conn.cursor() as cursor:
            # first query is there same version exist or not
            cursor.execute(same_sql)
            conn.commit()
            results = cursor.fetchall()
            is_exist = False
            print(results)
            if len(results) > 0:
                print(results[0])
                print('results[0]: {}'.format(results[0][0]))
                is_exist = True if int(results[0][0]) > 0 else False
            print('is exist: {}'.format(is_exist))
            if not is_exist:
                params = {"project_name": project_name, "version": version, "platform":platform, "device_brand":device_brand,"device_name":device_name,
                    "created_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                sql_insert = "insert into project_version(`project_name`,`version`,`platform`,`device_brand`," \
                            "`device_name`,`created_time`) values (%(project_name)s,%(version)s,%(platform)s," \
                            "%(device_brand)s,%(device_name)s,%(created_time)s)"
                cursor.execute(sql_insert, params)
                conn.commit()
    finally:
        if conn:
            conn.close()