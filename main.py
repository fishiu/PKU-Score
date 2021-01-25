import requests
import json
from configparser import ConfigParser
from time import time, sleep

config = ConfigParser()
config.read('./config.ini')

known_course_list = []


def get_debug_data():
    with open("debug.json") as f:
        return json.load(f)


def get_term_course_list(xnd="20-21", xq="1"):
    """
    获取一个学期的课程成绩信息
    :param xnd: 学年度
    :param xq: 学期
    :return: 课程列表
    """
    url = f'https://pkuhelper.pku.edu.cn/api_xmcp/isop/scores?user_token={config["token"]["helperToken"]}'
    res = requests.get(url).content
    res_dict = json.loads(res)
    # res_dict = get_debug_data()
    term_course_list = list(filter(lambda x: x["xnd"] == xnd and x["xq"] == xq, res_dict["cjxx"]))
    return term_course_list


def send_message(title, content):
    # title and content must be string.
    url = 'https://sc.ftqq.com/' + config["token"]["ScToken"] + '.send'
    data = {'text': title, 'desp': content}
    result = requests.post(url, data).content
    result_dict = json.loads(result)
    print(f"[MSG] 发送消息: 标题为「{title}」")
    print(f"[MSG] 发送状态: {result_dict['errmsg']}")


def inform_course(course):
    course_title = "出分啦～" + course['kcmc']
    course_content = "成绩为 " + course['xqcj']
    if course["jd"]:
        course_content += " ，绩点为 " + course['jd']
    course_content += f"\n\n目前出分{len(known_course_list)}门课程，加油加油！"
    if course["jd"] and int(course['xqcj']) >= 90:
        course_content += "\n\n考这么好，赏我点零花钱呗～，谢谢老爷！\n\n![支付二维码](http://pic.fishiu.com/uPic/NglUkI.jpg)"
    send_message(course_title, course_content)


def refresh_course_list():
    """
    获取新增课程
    :return: 返回新课程列表
    """
    new_course_list = list()
    course_list = get_term_course_list()
    known_course_id_list = [i["kch"] for i in known_course_list]
    for course in course_list:
        if course["kch"] not in known_course_id_list:
            new_course_list.append(course)
            known_course_list.append(course)
    return new_course_list


def init():
    global known_course_list
    known_course_list = get_term_course_list()

    init_title = f"{config['info']['name']}的监控初始化成功～"
    init_content = f"目前已出分{len(known_course_list)}门课程"
    send_message(init_title, init_content)

    cnt = 0
    while time() < int(config["time"]["stopTime"]):
        print(f"[LOOP] 第{cnt}次查询")
        refresh_res_list = refresh_course_list()
        if refresh_res_list:
            print("出分啦！！！！！")
            for refresh_course in refresh_res_list:
                inform_course(refresh_course)
        sleep(int(config["time"]["timeGap"]))
        cnt += 1


if __name__ == '__main__':
    init()
