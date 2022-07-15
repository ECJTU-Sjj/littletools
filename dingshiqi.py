# -*- coding: utf-8 -*-
import time

import requests as requests
from apscheduler.schedulers.background import BackgroundScheduler
import pymysql
import json

import warnings
warnings.filterwarnings('ignore')


def groups(L1, len1):
    groups = zip(*(iter(L1),) * len1)
    L2 = [list(i) for i in groups]
    n = len(L1) % len1
    L2.append(L1[-n:]) if n != 0 else L2
    return L2
def short_string(shortStr, len3):
    if "【"  or "】" in shortStr:
        len3=len3-2
    shortStr2 = shortStr[:len3] + (shortStr[len3:] and '...')
    return shortStr2

def job():
    product = "crm"
    conn = pymysql.connect(host="rm-m5eakra35e59hz3if8o.mysql.rds.aliyuncs.com", user="zentao_wangle",
                           password="Ae26e6fc", database="zentao_pm", charset="utf8")
    cursor = conn.cursor()
    sql_one = '''Select zentao_pm.zt_bug.id,
    zentao_pm.zt_bug.title,
    zentao_pm.zt_bug.severity,
     zentao_pm.zt_bug.type,
     zentao_pm.zt_bug.status,zentao_pm.zt_user.realname, 
     zentao_pm.zt_bug.openedDate,
     TIMESTAMPDIFF(HOUR,zentao_pm.zt_bug.openedDate,now()),   
     zentao_pm.zt_product.name 
     from (zentao_pm.zt_bug 
     right join zentao_pm.zt_product 
     on zentao_pm.zt_bug.product = zentao_pm.zt_product.id )
     right join zentao_pm.zt_user  
     on zentao_pm.zt_user.account=zentao_pm.zt_bug.assignedTo
     where zentao_pm.zt_product.name='%s'
     and zentao_pm.zt_bug.type="production"
     and zentao_pm.zt_bug.status ="active"
     and zentao_pm.zt_bug.deleted = 1 
     and  (zentao_pm.zt_bug.severity =1  or zentao_pm.zt_bug.severity =2 or zentao_pm.zt_bug.severity =3)
     order by zentao_pm.zt_bug.severity asc,zentao_pm.zt_bug.openedDate asc,zentao_pm.zt_bug.id asc ;''' % (product)

    # and  (((zentao_pm.zt_bug.severity =1  or zentao_pm.zt_bug.severity =2 )
    # and timediff(now(), zentao_pm.zt_bug.openedDate)>=12)
    # or((zentao_pm.zt_bug.severity !=1  or zentao_pm.zt_bug.severity !=2 )
    # and timediff(now(), zentao_pm.zt_bug.openedDate)>=336) )
    # 执行SQL语句
    cursor.execute(sql_one)
    # 获取多条查询数据
    ret = cursor.fetchall()
    '''数据库获取数据列表'''
    L1 = []
    L2 = []
    for i in ret:

        realname = i[5]
        '''指派给'''

        severity = str(i[2])
        '''严重程度'''
        name = i[1]
        name = short_string(name, 21)
        '''标题,通过short_string省略函数进行省略,防止所有bug字数过长，企微机器人接口字数限制接口报错'''

        bug = str(i[0])
        '''L1未超时，L2已超时，同时L1/L2区分1&2级 、3&4&5级bug，一二级根据机器人接口，添加颜色提醒标识'''
        if (severity == "1" or severity == "2") and i[7] / 24 - 0.5 < 0:
            day = str(format(-(i[7] / 24 - 0.5), '.2f'))
            a = "[bug#" + bug + " " + name + "]" + "(http://zentao.weiwenjia.com/bug-view-" + bug + ".html)\n" + "<font color=\"warning\">" + "@" + realname + "</font>" + " " + day + "天后超时"
            L2.append(a)

        elif (severity == "1" or severity == "2") and i[7] / 24 - 0.5 >= 0:
            day = str(format(i[7] / 24 - 0.5, '.2f'))
            b = "[bug#" + bug + " " + name + "]" + "(http://zentao.weiwenjia.com/bug-view-" + bug + ".html)\n" + "<font color=\"warning\">" + "@" + realname + "</font>" + " 超时" + day + "天"
            L1.append(b)

        elif (severity != "1" and severity != "2") and i[7] / 24 - 14 < 0:
            day = str(format(-(i[7] / 24 - 14), '.2f'))
            c = "[bug#" + bug + " " + name + "]" + "(http://zentao.weiwenjia.com/bug-view-" + bug + ".html)\n" + "@" + realname + " " + day + "天后超时"
            L2.append(c)
        elif (severity != "1" and severity != "2") and i[7] / 24 - 14 >= 0:
            day = str(format(i[7] / 24 - 14, '.2f'))
            d = "[bug#" + bug + " " + name + "]" + "(http://zentao.weiwenjia.com/bug-view-" + bug + ".html)\n" + "@" + realname + " 超时" + day + "天"
            L1.append(d)
    namelist=[]
    '''----------------'''
    '''以下把bug按照指派人进行分类'''
    for j in ret:
        namelist.append(j[5])

    namelist = set(namelist)
    L3 = []
    L4 = []
    for h in namelist:
        for g in L1:
            if g.split("@")[1].split("</font>")[0] == h or g.split("@")[1].split(" ")[0] == h:
                L3.append(g)
    for o in namelist:
        for p in L2:
            if p.split("@")[1].split("</font>")[0] == o or p.split("@")[1].split(" ")[0] == o:
                L4.append(p)
    '''----------------'''
    '''防止每日bug数较多，超出接口markdown方式字数限制，调用groups函数进行按len1条进行分割'''
    list3 = groups(L4, 30)
    list2 = groups(L3, 30)
    '''----------------'''

    '''把list拼接成str，分别对已超时，和未超时bug，进行发送请求'''
    for z in list2:
        x = '以下bug已超时，请相关人员尽快处理！'

        for j in z:
            x = x + "\n\n" + str(j)

        print(x)

        host = "https://qyapi.weixin.qq.com"
        path = "/cgi-bin/webhook/send?key=5115e492-67ea-4d23-897f-bf3597f183d0"
        # path = "/cgi-bin/webhook/send?key=90131ff2-6df4-45fb-82a6-fe74a3f1e44d"
        data = json.dumps(
            {
                "msgtype": "markdown",
                "markdown": {
                    "content": x
                }
            }
        )

        headers = {
            'Content-Type': 'application/json',

        }
        url = host + path

        r = requests.post(url=url, data=data, headers=headers)
        print(r.text)
    for w in list3:

        u = '以下bug即将超时，请相关人员尽快处理！'
        for M in w:
            u = u + "\n\n" + str(M)
        print(u)

        host = "https://qyapi.weixin.qq.com"
        path = "/cgi-bin/webhook/send?key=5115e492-67ea-4d23-897f-bf3597f183d0"
        # path = "/cgi-bin/webhook/send?key=90131ff2-6df4-45fb-82a6-fe74a3f1e44d"
        data = json.dumps(
            {
                "msgtype": "markdown",
                "markdown": {
                    "content": u
                }
            }
        )

        headers = {
            'Content-Type': 'application/json',

        }
        url = host + path

        r = requests.post(url=url, data=data, headers=headers)
        print(r.text)
        '''----------------'''
    return r.text

if __name__ == '__main__':
    #以下是定时器函数
    # BackgroundScheduler: 适合于要求任何在程序后台运行的情况，当希望调度器在应用后台执行时使用
    scheduler = BackgroundScheduler()
    # 采用非阻塞的方式

    # 采用corn的方式
    flag=1
    if flag ==1:
        scheduler.add_job(job, 'cron',day_of_week='mon,tue,wed,thu,fri,sat', hour='9', minute='40', second='16')
        flag=0
    if flag==1:
        scheduler.add_job(job, 'cron', day_of_week='mon,tue,wed,thu,fri,sat', hour='9', minute='40', second='17')
        flag=0
    '''
    year (int|str) – 4-digit year
    month (int|str) – month (1-12)
    day (int|str) – day of the (1-31)
    week (int|str) – ISO week (1-53)
    day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    hour (int|str) – hour (0-23)
    minute (int|str) – minute (0-59)
    econd (int|str) – second (0-59)

    start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
    end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
    timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)

    *    any    Fire on every value
    */a    any    Fire every a values, starting from the minimum
    a-b    any    Fire on any value within the a-b range (a must be smaller than b)
    a-b/c    any    Fire every c values within the a-b range
    xth y    day    Fire on the x -th occurrence of weekday y within the month
    last x    day    Fire on the last occurrence of weekday x within the month
    last    day    Fire on the last day within the month
    x,y,z    any    Fire on any matching expression; can combine any number of any of the above expressions
    '''

    scheduler.start()
    try:
        # 模拟主进程持续运行
        while True:
            time.sleep(2)
            print('main-start:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    except(KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
        print('Exit The Job!')

    # 其他任务是独立的线程
    # while True:
    #     print('main-start:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    #     time.sleep(60)
    #     print('main-end:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    #     time.sleep(1)