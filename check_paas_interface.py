__author__ = 'Xue Fei'
import requests
import json
import datetime

lis = [
    {"report_name": "客户分析", "report_id": "zHHvuvw7D1cNqMWp"},
    {"report_name": "客户类型统计", "report_id": "ftF8n5qn8z2k6emw"},
    {"report_name": "客户分配统计", "report_id": "QEMGcG3vPvq6XtiR"},
    {"report_name": "销售人效分析", "report_id": "Pr3P9ir3jSerMBxu"},
    {"report_name": "销售回款排名", "report_id": "Vd3H1u8HBvyMvuDS"},
    {"report_name": "客户数量排名", "report_id": "Q93D4feRXCZJPqP2"},
    {"report_name": "业绩目标完成度排名", "report_id": "ZeW9MJwyRevbSwJk"},
    {"report_name": "销售额排名", "report_id": "PAwssWNmMaLE4gfB"},
    {"report_name": "线索转化率", "report_id": "f1tR7h6pYcD1wMaZ"},
    {"report_name": "部门荣誉榜", "report_id": "2dJye6bLiWyeWH8q"},
    {"report_name": "个人荣誉榜", "report_id": "S99aoMZ9LsJ7Y5Y1"},
    {"report_name": "拜访签到", "report_id": "1fUHxTLSzGdeuP7a"},
    {"report_name": "跟进记录", "report_id": "DVZg7fLy8eENEoko"},
    {"report_name": "销售预测", "report_id": "QHKzMemqSjfZ53SL"},
    {"report_name": "销售漏斗", "report_id": "rQtRcf7eJsTzPPeM"},
    {"report_name": "业务新增汇总", "report_id": "j8eMzhgtocRFNCxK"},
    {"report_name": "广告助手ROI分析", "report_id": "FzQPGjhpWUHkUJ8y"},
    {"report_name": "业绩目标完成度", "report_id": "v4SasNekNwg6yGHv"},
    {"report_name": "回款计划汇总", "report_id": "NVWcQ2eK2ALWAC84"},
    {"report_name": "产品价格销售汇总", "report_id": "bWRVAcEn7sZi9PzZ"},
    {"report_name": "赢单商机汇总", "report_id": "1UR9Whj4teedNT4p"},
    {"report_name": "合同管理汇总", "report_id": "tcmV5UEvA3AqqfhK"},
    {"report_name": "机器人数据统计", "report_id": "8LciREaNgSypeLZ5"},
    {"report_name": "短信到达率", "report_id": "N79u7KSv2avvkin6"},
    {"report_name": "流量额度消耗统计", "report_id": "eBLJqEmzMJMkw11e"}
]


class CheckInterface:

    def __init__(self):
        self.user_infos = [
            {
                "platform": "lixiaoyun",
                "user_token": "900d51024354f1e2deb11b0c905f0935",
                "host": "https://lxcrm.weiwenjia.com",
                "department_id": 11515617,
                "uid": 12897184,  # 机器人报表使用,
                "oid": 11524358,  # 电销使用,
                "platform_name": "独立版"
            },
            {
                "platform": "dingtalk",
                "user_token": "4ff8dc7c327414d3beac07a574849bef",
                "host": "https://dingtalk.e.ikcrm.com",
                "department_id": 1676598,
                "uid": 16285270,  # 机器人报表使用
                "oid": 11757214,  # 电销使用
                "platform_name": "钉钉版"
            },
            {
                "platform": "wxwork",
                "user_token": "c5bdbc4ba49c4f1127c687ffcc75c411",
                "host": "https://e.lixiaocrm.com",
                "department_id": 52496,
                "uid": 21083635,  # 机器人报表使用
                "oid": 11013718,  # 电销使用
                "platform_name": "企微版"
            }
        ]
        self.error_logs = {
            "lixiaoyun": [],
            "dingtalk": [],
            "wxwork": []
        }
        self.report_ids = []
        self.robot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=eb6d6b95-fa37-4057-886f-5e831e2702e3"
        self.robot_url_success = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=44045ec1-60c2-41b6-9fa9-9742e8b3b181"
        self.header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            'Connection': 'close'
        }
        self.md_header = {
            'Content-Type': 'application/json'
        }

    def get_client_token_and_snippet_id(self, report_id, report_name, **user_info):
        """
        获取请求报表的client_token 和 snippet_uid
        :param report_name: 报表名称
        :param report_id: 报表id
        :return: res_info
        """
        url = "https://cloud-service.lixiaoyun.com/report/api/v1/notebooks/{}/share?tag=prod".format(report_id)
        try:
            res = requests.get(url=url, headers=self.header, timeout=(10, 5))

            # 获取请求报表的client_token 和 snippet_uid
            res_info = {
                "client_token": res.json()["data"]["client_token"],
                "snippet_uid": res.json()["data"]["body_used_snippet_uids"][0],
                "report_name": report_name
            }
            return res_info
        except Exception as E:
            print("/############一条报错信息#############")
            print(report_name)
            print(E)
            print("############一条报错信息#############/")
            # 请求异常的时候 获取报错信息
            self.error_logs[user_info["platform"]].append(
                "<font color='red'>{}</font>, 报错信息:{}".format(report_name, str(E)[:60].replace('\n', '')))
            return None

    def report_check(self, snippet_uid, client_token, report_name, **user_info):
        """
        检测每个报表
        :param snippet_uid: 报表id
        :param client_token: 请求token
        :param report_name:  报表名称
        :param user_info: self.user_infos
        :return:
        """

        url = "https://cloud-service.lixiaoyun.com/service-lowcode/api/v1/snippets/{}/share?client_token={}".format(
            snippet_uid, client_token)
        if report_name in ["销售回款排名", "客户数量排名"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "times": [
                        "2022-03-01",
                        "2023-03-31"
                    ]
                },
                "meta": []
            }
        elif report_name in ["客户分析"]:
            body = {
                "low_code_params": {
                    "custom_fields": {},
                    "dimensions": [
                        {
                            "name": "CustomerDailyStatistics.category",
                            "label": "客户类型11"
                        },
                        {
                            "name": "CustomerDailyStatistics.departmentId",
                            "label": "所属部门"
                        }
                    ],
                    "measures": [
                        {
                            "name": "CustomerDailyStatistics.customerCount",
                            "label": "客户22数"
                        },
                        {
                            "name": "CustomerDailyStatistics.contractAmount",
                            "label": "合同钉钉2金额"
                        },
                        {
                            "name": "CustomerDailyStatistics.receivedPaymentPlansAmount",
                            "label": "计划回款金额"
                        },
                        {
                            "name": "CustomerDailyStatistics.receivedPaymentsAmount",
                            "label": "回款金额"
                        }
                    ]
                },
                "meta": []
            }

        elif report_name in ["销售人效分析"]:
            body = {
                "low_code_params": {
                    "dimensions": [
                        {
                            "name": "department_id",
                            "label": "员工所在部门"
                        }
                    ],
                    "measures": [
                        {
                            "name": "Leads.count",
                            "label": "新增线索数"
                        },
                        {
                            "name": "Customers.count",
                            "label": "新增客户22数"
                        },
                        {
                            "name": "RevisitLogs.count",
                            "label": "总跟进次数"
                        },
                        {
                            "name": "NewOpportunities.expectAmount",
                            "label": "新增商机123金额"
                        },
                        {
                            "name": "Contracts.totalAmount",
                            "label": "合同钉钉2金额"
                        },
                        {
                            "name": "ReceivedPaymentPlans.amount",
                            "label": "计划回款金额"
                        },
                        {
                            "name": "ReceivedPayments.amount",
                            "label": "回款金额"
                        }
                    ]
                },
                "meta": []
            }
        elif report_name in ["客户类型统计", "客户数量排名"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "status": ""
                },
                "meta": []
            }
        elif report_name in ["客户分配统计"]:
            body = {
                "low_code_params": {
                    "custom_fields": {},
                    "times": [
                        "2023-01-01",
                        "2023-03-31"
                    ],
                    "pagination": {
                        "current_page": 1,
                        "page_size": 10
                    },
                    "date_dimension": "month"
                },
                "meta": []
            }
        elif report_name in ["业绩目标完成度排名"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "months": [
                        "2023-01",
                        "2023-12"
                    ],
                    "goal_type": "win_money",
                    "product_category_id": 0,
                    "product_id": 0,
                    "department_ids": [
                        user_info["department_id"]
                    ],

                },
                "meta": []
            }
        elif report_name in ["销售额排名"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "months": [
                        "2022-01",
                        "2023-12"
                    ]
                },
                "meta": []
            }
        elif report_name in ["线索转化率"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "year": "2023"
                },
                "meta": []
            }
        elif report_name in ["部门荣誉榜"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "times": [
                        "2023-01-01",
                        "2023-12-31"
                    ],
                    "timesValue": "year",
                    "rank_type": "contract_amount",
                    "department_ids": [
                        user_info["department_id"]
                    ],
                    "include_child": True
                },
                "meta": []
            }
        elif report_name in ["个人荣誉榜"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "times": [
                        "2023-01-01",
                        "2023-12-31"
                    ],
                    "timesValue": "year",
                    "rank_type": "contract_amount",
                    "department_ids": [
                        user_info["department_id"]
                    ]
                },
                "meta": []
            }
        elif report_name in ["拜访签到"]:
            body = {
                "low_code_params": {
                    "custom_fields": {},
                    "pagination": {
                        "current_page": 1,
                        "page_size": 10
                    },
                    "date_dimension": "month"
                },
                "meta": []
            }
        elif report_name in ["跟进记录"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    }
                },
                "meta": []
            }
        elif report_name in ["销售预测"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    }
                },
                "meta": []
            }
        elif report_name in ["销售漏斗"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    }
                },
                "meta": []
            }
        elif report_name in ["业务新增汇总"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "timesValue": "month",
                    "times": [
                        "2023-03-01",
                        "2023-03-31"
                    ],
                    "dimension": "year"
                },
                "meta": []
            }
        elif report_name in ["广告助手ROI分析"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "dimension": "engine",
                    "year": "2023"
                },
                "meta": []
            }
        elif report_name in ["业绩目标完成度"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "goal_type": "win_money",
                    "product_category_id": 0,
                    "product_id": 0,
                    "user_ids": [],
                    "times": {
                        "value": "custom",
                        "values": [
                            "2023-01",
                            "2023-12"
                        ]
                    },
                    "months": [
                        "2023-01",
                        "2023-12"
                    ],
                    "department_ids": [
                        user_info["department_id"]
                    ]
                },
                "meta": []
            }
        elif report_name in ["回款计划汇总"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "year": "2023"
                },
                "meta": []
            }
        elif report_name in ["产品价格销售汇总"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "timesValue": "all",
                    "times": [],
                    "year": "2023"
                },
                "meta": []
            }
        elif report_name in ["赢单商机汇总"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "year": "2023"
                },
                "meta": []
            }
        elif report_name in ["合同管理汇总"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "user_ids": [],
                    "department_id": 0,
                    "year": "2023",
                    "time_type": "month",
                    "sign_date_type": "year",
                    "sign_date": [
                        "2023-01-01",
                        "2023-12-31"
                    ]
                },
                "meta": []
            }
        elif report_name in ["机器人数据统计"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "selectType": 1,
                    "queryTime": "day",
                    "uid": user_info["uid"],
                    "userIds": [],
                    "departmentId": 0,
                },
                "meta": []
            }
        elif report_name in ["短信到达率"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "year": "2023"
                },
                "meta": []
            }
        elif report_name in ["流量额度消耗统计"]:
            body = {
                "low_code_params": {
                    "pagination": {
                        "current_page": 1,
                        "page_size": 50
                    },
                    "times": [
                        "2022-01-01",
                        "2022-12-31"
                    ],
                    "timesValue": "month",
                    "dateType": "1",
                    "uid": 0,
                    "did": 0,
                    # "oid": 11524358,
                    "oid": user_info["oid"],
                    "auth": "c5bdbc4ba49c4f1127c687ffcc75c411",
                    "showDomain": 1
                },
                "meta": []
            }

        # 添加请求体参数
        body["low_code_params"].update({"env": "prod"})
        body["low_code_params"].update({"host": user_info["host"]})
        body["low_code_params"].update({"crm_platform_type": user_info["platform"]})
        body["low_code_params"].update({"user_token": user_info["user_token"]})
        try:
            # 获取返回值
            res = requests.post(url=url, headers=self.header, json=body, timeout=(10, 5))
            # 如果接口success 值 是False 就获取报错 存到self.error_logs 里面
            if res.json()['success'] is False:
                self.error_logs[user_info["platform"]].append(
                    "<font color='red'>{}</font>, 报错信息:{}".format(report_name,
                                                                  res.json()['error'][:60].replace('\n', '')))
                print("/############一条报错信息#############")
                print(report_name)
                print(res.json()['error'])
                print("############一条报错信息#############/")

        except Exception as E:
            print("/############一条报错信息#############")
            print(report_name)
            print(E)
            print("############一条报错信息#############/")
            # 请求异常的时候 获取报错信息
            self.error_logs[user_info["platform"]].append(
                "<font color='red'>{}</font>, 报错信息:{}".format(report_name, str(E)[:60].replace('\n', '')))

    def run_check(self):
        """
        运行请求
        :return:
        """
        # 循环遍历每个环境的请求
        for user_info in self.user_infos:
            print(user_info)
            for li in lis:
                res_info = self.get_client_token_and_snippet_id(li["report_id"], li["report_name"], **user_info)
                # 如果获取接口失败就不再请求
                if res_info is not None:
                    self.report_check(res_info["snippet_uid"], res_info["client_token"], res_info["report_name"],
                                      **user_info)
        print(self.error_logs)
        # error_log 都等于0 即为没有报错
        if len(self.error_logs["lixiaoyun"]) == 0 and len(self.error_logs["dingtalk"]) == 0 and len(
                self.error_logs["wxwork"]) == 0:
            markdown_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": '生产环境 独立，钉钉，企微 一级报表接口请求正常。\n'
                               '>脚本每个小时执行一次，没有报错只有上午9点的检测才提示，其他时间不提示。\n'
                               '脚本只能检测常规情况，特殊请求无法检测到。'
                }
            }
            # 没有报错只有上午9点的检测才提示，其他时间不提示。
            if datetime.datetime.now().hour == 9:
                requests.post(self.robot_url_success, data=json.dumps(markdown_data))
            return
        # 独立版 报错
        if len(self.error_logs["lixiaoyun"]) > 0:
            error_att = '\n'.join(self.error_logs["lixiaoyun"])
            markdown_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": '生产环境 独立版以下报表报错，请相关同事注意。\n>'
                               '>user_token:' + self.user_infos[0]["user_token"] + '\n' + error_att
                }
            }
            requests.post(self.robot_url, data=json.dumps(markdown_data))
        # 钉钉版报错
        if len(self.error_logs["dingtalk"]) > 0:
            error_att = '\n'.join(self.error_logs["dingtalk"])
            markdown_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": '生产环境 钉钉版以下报表报错，请相关同事注意。\n>'
                               '>user_token:' + self.user_infos[1]["user_token"] + '\n' + error_att
                }
            }
            requests.post(self.robot_url, data=json.dumps(markdown_data))
        # 企微版本报错
        if len(self.error_logs["wxwork"]) > 0:
            error_att = '\n'.join(self.error_logs["wxwork"])
            markdown_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": '生产环境 企微版以下报表报错，请相关同事注意。\n>'
                               '>user_token:' + self.user_infos[2]["user_token"] + '\n' + error_att
                }
            }
            requests.post(self.robot_url, data=json.dumps(markdown_data))


if __name__ == '__main__':
    ci = CheckInterface()
    ci.run_check()
