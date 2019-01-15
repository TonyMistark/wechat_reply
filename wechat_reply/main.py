#!/usr/bin/env python
# encoding: utf-8

import itchat
import requests
import json
from datetime import datetime
import time


def get_reply_data(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return json.loads(r.text)
    except:
        return {}


def check_account(msg, nickname):
    """
    :param msg: account dinner 12.0 / 记账 早餐 12.0
    :return:
    """
    vars = msg.split(msg)
    result = {}
    tips = "请不要在拉黑的边缘试探！"
    if len(vars) != 3:
        return -1, result
    if vars[0] not in ["account", "记账"]:
        return -1, result
    try:
        fee = float(vars[2])
    except Exception as e:
        print("str: %s" % e)
        return -1
    bill = vars[1]
    print("{bill}花费{fee}".format(bill=bill, fee=fee))
    result = {
        "nickname": nickname,
        "bill": bill,
        "fee": fee
    }
    return 0, result

@itchat.msg_register(["Text", "Map", "Card", "Note", "Sharing", "Picture"])
def text_reply(msg):
    text = msg["Text"]
    code, res = check_account(text, "我自己")
    if code != 0:
        return
    bill = res["bill"]
    fee = res["fee"]
    url = (
        "http://www.tuling123.com/openapi/api?key=9dd33d6c10694a34b3de086e1d1c9603&info=%s"
        % bill
    )
    response_msg = get_reply_data(url).get("text", "你可能在拉黑的边缘试探~")
    print(
        "%s: %s"
        % (
            msg["User"].get("RemarkName") or msg["User"].get("NickName", "someone"),
            msg.get("Text", ""),
        )
    )
    print("reply: %s" % response_msg)
    account_tips = "{bill}花费{fee}".format(bill=bill, fee=fee)
    res_msg = """记账成功：{account_tips}
    {response_msg}
    """.format(account_tips=account_tips, response_msg=response_msg)
    return res_msg

def sendChatroomMsg(roomName, context):
    itchat.get_chatrooms(update=True)
    roomNickName = roomName
    candidates = itchat.search_chatrooms(roomNickName)
    print("candidates", candidates)

    username = ''
    for candidate in candidates:
        if candidate['NickName'] == roomNickName:
            username = candidate['UserName']
            break
    if username:
        sendtime = datetime.now().strftime('%A %B %d,%Y')  # Tue June 08,2018
        sendtime = datetime.now().strftime('%m-%d-%Y %H:%M:%S,%A')
        msg = context + "Sending in " + sendtime
        print("Ready to send message to group %s,message as follows : \n%s" % (roomName, msg))
        itchat.send_msg(msg=context, toUserName=username)

context = """记得给大家带圣诞礼物
@邱敏 @YUYI @杨黎 @。"""

if __name__ == "__main__":
    itchat.auto_login()
    friends = itchat.get_friends(update=True)[0:]
    # grops = itchat.get_chatrooms(update=True)[0:]
    for g in friends:
        print(g["NickName"], g["UserName"])
    name = {}
    nickname = []
    user = []
    for i in range(len(friends)):
        nickname.append(friends[i]["NickName"])
        user.append(friends[i]["UserName"])
    for i in range(len(friends)):
        name[nickname[i]] = user[i]

    itchat.run()
    #
    # while True:
    #     time.sleep(60 * 5)
    #     sendChatroomMsg(roomName="Gino", context=context)
