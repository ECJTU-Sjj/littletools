__author__ = 'Xue Fei'
import requests
import json
import datetime


class CheckInterface:

    def __init__(self):
        self.report_infos = {
            "lixiaoyun": [
                {
                    "report_id": "HiugjzFhjjmFmScV",
                    "report_name": "分库drds prod",
                },
                {
                    "report_id": "X5o6kHjBtWAX9Lve",
                    "report_name": "扩展库 prod",
                },
                {
                    "report_id": "bYPPBZsRAzEgRhP7",
                    "report_name": "UC prod",
                },
                {
                    "report_id": "hkC7B4ovmMk2Kpsu",
                    "report_name": "宽表 pro",
                }
            ],
            "dingtalk": [
                {
                    "report_id": "VWU4A6Lgoox7PNwr",
                    "report_name": "UC prod",
                },
                {
                    "report_id": "ff6zx2wGXJcCg5y3",
                    "report_name": "分库drds prod",
                },
                {
                    "report_id": "khsqQz1HBrC5J4vP",
                    "report_name": "宽表 prod",
                }

            ],
            "wxwork": [
                {
                    "report_id": "zmPoXrtAqPeHVpLF",
                    "report_name": "UC prod",
                },
                {
                    "report_id": "ye1gQA7hF84hF3rs",
                    "report_name": "扩展库 prod",
                },
                {
                    "report_id": "gVWmuJ9UPdoP8Q9f",
                    "report_name": "分库drds prod",
                },
                {
                    "report_id": "ya5EUfXnqpckcGvb",
                    "report_name": "宽表 prod",
                }
            ]
        }
        self.error_logs = {
            "lixiaoyun": [],
            "dingtalk": [],
            "wxwork": []
        }
        self.robot_url_error = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=eb6d6b95-fa37-4057-886f-5e831e2702e3"
        self.robot_url_success = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=44045ec1-60c2-41b6-9fa9-9742e8b3b181"
        self.header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        self.md_header = {
            'Content-Type': 'application/json'
        }

    def get_client_token_and_snippet_id(self, report_id, report_name, platform_key):
        """
        获取请求报表的client_token 和 snippet_uid
        :param platform_key: self.report_infos 的key
        :param report_name: 报表名称
        :param report_id: 报表id
        :return: res_info
        """
        url = "https://cloud-service.lixiaoyun.com/report/api/v1/notebooks/{}/share".format(report_id)
        try:
            res = requests.get(url=url, headers=self.header, timeout=10)

        # 获取请求报表的client_token 和 snippet_uid
            res_info = {
                "client_token": res.json()["data"]["client_token"],
                "snippet_uid": res.json()["data"]["body_used_snippet_uids"][0],
                "report_name": report_name
            }
            return res_info

        except Exception as E:
            print(E)
            # 请求异常的时候 获取报错信息
            self.error_logs[platform_key].append(
                "<font color='red'>{}</font>, 报错信息:{}".format(report_name, str(E)[:60].replace('\n', '')))
            return None

    def report_check(self, snippet_uid, client_token, report_name, platform_key):
        """
        检测每个报表
        :param snippet_uid: 报表id
        :param client_token: 请求token
        :param report_name:  报表名称
        :param platform_key: self.report_infos 的key
        :return:
        """

        url = "https://cloud-service.lixiaoyun.com/service-lowcode/api/v1/snippets/{}/share?client_token={}".format(
            snippet_uid, client_token)

        try:
            # 获取返回值
            res = requests.post(url=url, headers=self.header)
            # 如果接口success 值 是False 就获取报错 存到self.error_logs 里面
            if res.json()['success'] is False:
                self.error_logs[platform_key].append(
                    "<font color='red'>{}</font>, 报错信息:{}".format(report_name,
                                                                  res.json()['error'][:60].replace('\n', '')))
        except Exception as E:
            # 请求异常的时候 获取报错信息
            self.error_logs[platform_key].append(
                "<font color='red'>{}</font>, 报错信息:{}".format(report_name, str(E)[:60].replace('\n', '')))

    def run_check(self):
        """
        运行请求
        :return:
        """
        # 循环遍历每个环境的请求
        for platform_key in self.report_infos:
            print(self.report_infos[platform_key])
            for li in self.report_infos[platform_key]:
                res_info = self.get_client_token_and_snippet_id(li["report_id"], li["report_name"], platform_key)
                # 获取不到token 就不再请求
                if res_info is not None:
                    self.report_check(res_info["snippet_uid"], res_info["client_token"], res_info["report_name"],
                                      platform_key)
        print(self.error_logs)
        # error_log 都等于0 即为没有报错
        if len(self.error_logs["lixiaoyun"]) == 0 and len(self.error_logs["dingtalk"]) == 0 and len(
                self.error_logs["wxwork"]) == 0:
            markdown_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": '生产环境 独立，钉钉，企微 一级报表接口请求正常。\n'
                               '>快速脚本执行正常。\n'
                }
            }
            # 没有报错只有上午9点的检测才提示，其他时间不提示。
            if datetime.datetime.now().hour == 9 and 0 <= datetime.datetime.now().minute < 5:
                requests.post(self.robot_url_success, data=json.dumps(markdown_data))
                return
        # 独立版 报错
        if len(self.error_logs["lixiaoyun"]) > 0:
            error_att = '\n'.join(self.error_logs["lixiaoyun"])
            markdown_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": '生产环境 独立版以下报表报错，请相关同事注意。\n>'
                               '>' + error_att
                }
            }
            requests.post(self.robot_url_error, data=json.dumps(markdown_data))
        # 钉钉版报错
        if len(self.error_logs["dingtalk"]) > 0:
            error_att = '\n'.join(self.error_logs["dingtalk"])
            markdown_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": '生产环境 钉钉版以下报表报错，请相关同事注意。\n>'
                               '>' + error_att
                }
            }
            requests.post(self.robot_url_error, data=json.dumps(markdown_data))
        # 企微版本报错
        if len(self.error_logs["wxwork"]) > 0:
            error_att = '\n'.join(self.error_logs["wxwork"])
            markdown_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": '生产环境 企微版以下报表报错，请相关同事注意。\n>'
                               '>' + error_att
                }
            }
            requests.post(self.robot_url_error, data=json.dumps(markdown_data))


if __name__ == '__main__':
    ci = CheckInterface()
    ci.run_check()
