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

    
def Request(path,x):
    host = "https://qyapi.weixin.qq.com"
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
    print(url)
    r = requests.post(url=url, data=data, headers=headers).text
    print(r)

def job():
    # path = "/cgi-bin/webhook/send?key=5115e492-67ea-4d23-897f-bf3597f183d0" #crm
    #path = "/cgi-bin/webhook/send?key=90131ff2-6df4-45fb-82a6-fe74a3f1e44d" #调试
    #path="/cgi-bin/webhook/send?key=80f90571-47c0-4d6c-b0d5-93b37b105a70" #自己调试
    #path="/cgi-bin/webhook/send?key=cdf257c2-22cb-43aa-a3b5-575637435395" #技术支持
    # path = "/cgi-bin/webhook/send?key=0e1b6833-ecf2-4752-aa68-53adac9c7adb" #jxc
    # path="/cgi-bin/webhook/send?key=68c5a730-dc91-48d3-95ed-cf97c7fb33d2" #skb
    #path = "/cgi-bin/webhook/send?key=88d98d7e-7d78-44ed-a512-930051ce747c"  # SCRM
    product = "crm"
    #conn = pymysql.connect(host="rm-m5eakra35e59hz3if8o.mysql.rds.aliyuncs.com", user="zentao_wangle",password="Ae26e6fc", database="zentao_pm", charset="utf8")#本地
    conn = pymysql.connect(host="rm-m5eakra35e59hz3if.mysql.rds.aliyuncs.com", user="zentao_wangle",password="Ae26e6fc", database="zentao_pm", charset="utf8")

    cursor = conn.cursor()
    sql_one = '''
SELECT
    zentao_pm.zt_bug.id,
    zentao_pm.zt_bug.title,
    zentao_pm.zt_bug.severity,
    zentao_pm.zt_bug.type,
    zentao_pm.zt_bug.STATUS,
    zentao_pm.zt_user.realname,
    zentao_pm.zt_bug.openedDate,
    TIMESTAMPDIFF(
			HOUR,
			zentao_pm.zt_bug.openedDate,
		now()),
    zentao_pm.zt_product.NAME ,
    (SELECT IF (actor='ts001','已备注','未备注') from zentao_pm.zt_action where zentao_pm.zt_action.objectID=zentao_pm.zt_bug.id  and action='commented' ORDER BY date desc limit 1),
    zentao_pm.zt_bug.resolution
FROM
    ( zentao_pm.zt_bug RIGHT JOIN zentao_pm.zt_product ON zentao_pm.zt_bug.product = zentao_pm.zt_product.id )
    RIGHT JOIN zentao_pm.zt_user ON zentao_pm.zt_user.account = zentao_pm.zt_bug.assignedTo 
WHERE
    zentao_pm.zt_product.NAME = '%s' 
    AND zentao_pm.zt_bug.deleted = 1 
    AND zentao_pm.zt_user.id = 651 
    AND zentao_pm.zt_bug.STATUS != "closed" 
ORDER BY
    zentao_pm.zt_bug.severity ASC,
    zentao_pm.zt_bug.openedDate ASC,
    zentao_pm.zt_bug.id ASC ''' % (product)

    # and  (((zentao_pm.zt_bug.severity =1  or zentao_pm.zt_bug.severity =2 )
    # and timediff(now(), zentao_pm.zt_bug.openedDate)>=12)
    # or((zentao_pm.zt_bug.severity !=1  or zentao_pm.zt_bug.severity !=2 )
    # and timediff(now(), zentao_pm.zt_bug.openedDate)>=336) )
    # 执行SQL语句
    cursor.execute(sql_one)
    # 获取多条查询数据
    ret = cursor.fetchall()
    print(ret)
    if ret == ():
        r = Request(path, "线上bug已经全部处理完了，棒棒哒~")

    else:
        '''数据库获取数据列表'''
        L1 = []
        L2 = []
        for i in ret:

            realname = i[5]
            '''指派给'''
            staus = str(i[4])
            severity = str(i[2])
            '''严重程度'''
            resolution=str(i[10])
            if str(i[9])=='None':
                action ='未备注'
            else:
                action = str(i[9])
            name = i[1].replace('[','').replace(']','')
            name = short_string(name, 21)
            '''标题,通过short_string省略函数进行省略,防止所有bug字数过长，企微机器人接口字数限制接口报错'''
            bug = str(i[0])
            '''L1未超时，L2已超时，同时L1/L2区分1&2级 、3&4&5级bug，一二级根据机器人接口，添加颜色提醒标识'''
            if (severity == "1" or severity == "2") and staus == "resolved" :
                day = str(format(-(i[7] / 24 - 0.5), '.2f'))
                a = "[bug#" + bug + " " + name + "]" + "(http://zentao.weiwenjia.com/bug-view-" + bug + ".html)\n" + "<font color=\"warning\">"   + " " + day + "天后超时"+" bug状态：已解决"+' '+resolution+' '+ action+"</font>"
                L2.append(a)

            elif (severity == "1" or severity == "2") and staus != "resolved" :
                day = str(format(i[7] / 24 - 0.5, '.2f'))
                b = "[bug#" + bug + " " + name + "]" + "(http://zentao.weiwenjia.com/bug-view-" + bug + ".html)\n" + "<font color=\"warning\">"   + " 超时" + day + "天"+" bug状态:"+staus+' '+ action+ "</font>"
                L1.append(b)

            elif (severity != "1" and severity != "2") and staus == "resolved" :
                day = str(format(-(i[7] / 24 - 14), '.2f'))
                c = "[bug#" + bug + " " + name + "]" + "(http://zentao.weiwenjia.com/bug-view-" + bug + ".html)\n"  + " " + day + "天后超时"+" bug状态：已解决"+' '+resolution+' '+ action
                L2.append(c)
            elif (severity != "1" and severity != "2") and staus != "resolved" :
                day = str(format(i[7] / 24 - 14, '.2f'))
                d = "[bug#" + bug + " " + name + "]" + "(http://zentao.weiwenjia.com/bug-view-" + bug + ".html)\n"  + " 超时" + day + "天"+" bug状态:"+staus+' '+ action
                L1.append(d)

        # namelist = []
        # '''----------------'''
        # '''以下把bug按照指派人进行分类'''
        #
        # for j in ret:
        #     namelist.append(j[5])
        #
        # namelist = set(namelist)
        # L3 = []
        # L4 = []
        # for h in namelist:
        #     for g in L1:
        #         if g.split("@")[1].split("</font>")[0] == h or g.split("@")[1].split(" ")[0] == h:
        #             L3.append(g)
        # for o in namelist:
        #     for p in L2:
        #         if p.split("@")[1].split("</font>")[0] == o or p.split("@")[1].split(" ")[0] == o:
        #             L4.append(p)
        '''----------------'''
        '''防止每日bug数较多，超出接口markdown方式字数限制，调用groups函数进行按len1条进行分割'''
        list3 = groups(L2, 30)
        list2 = groups(L1, 30)
        '''----------------'''

        '''把list拼接成str，分别对已超时，和未超时bug，进行发送请求'''
        for z in list2:
            x = '以下bug指派到 @技术支持001 请及时跟进哦！'

            for j in z:
                x = x + "\n\n" + str(j)

            print(x)
            r = Request(path, x)
        for w in list3:
            u = '@技术支持001以下bug已解决同测试确认是否已上线，同步上线时间给客户！'
            for M in w:
                u = u + "\n\n" + str(M)
            print(u)
            r = Request(path, u)

            '''----------------'''
        return r

if __name__ == '__main__':
    job()
