#!/usr/bin/env python
# encoding: utf-8

import itchat
import requests
import json
from datetime import datetime
import time
import pymongo


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
    result = {}
    try:
        vars = msg.split(" ")
    except Exception as e:
        print("str: %s" % e)
        return -4, result
    print("")
    if len(vars) != 3:
        return -1, result
    if vars[0] not in ["bill", "记账"]:
        return -2, result
    try:
        fee = float(vars[2])
    except Exception as e:
        print("str: %s" % e)
        return -3, result
    bill = vars[1]
    print("{bill}花费{fee}".format(bill=bill, fee=fee))
    result = {
        "nickname": nickname,
        "bill": bill,
        "fee": fee
    }
    return 0, result


def save_data(username, bill_name, bill_fee, user_id):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["bill"]
    mycol = mydb["day_bill"]
    create_time = int(time.time())
    my_bill = {
        "username": username,
        "bill_name": bill_name,
        "bill_fee": bill_fee,
        "user_id": user_id,
        "create_time": create_time,
        "update_time": create_time
    }
    x = mycol.insert_one(my_bill)
    print("mongo_result: ", x)


def today_bill(user_id):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["bill"]
    mycol = mydb["day_bill"]
    today = int(time.mktime(datetime.now().date().timetuple()))
    result = mycol.find({"user_id": user_id, "create_time": {"$gte": today, "$lt": (today + (24*60*60))}})
    return [i for i in result]


def all_bill(user_id):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["bill"]
    mycol = mydb["day_bill"]
    result = mycol.find({"user_id": user_id})
    return [i for i in result]

def to_string(bills):
    bill_strings = []
    total = 0
    for b in bills:
        bill_strings.append(b["bill_name"] + str("%.2f" % b["bill_fee"]) + "于" + datetime.fromtimestamp(b["create_time"]).strftime("%Y-%m-%d %H:%M:%S"))
        total += b["bill_fee"]
    if total > 0:
        bill_strings.append("总计：%.2f" % total)
    return "\n".join(bill_strings)

@itchat.msg_register(["Text", "Map", "Card", "Note", "Sharing", "Picture"])
def text_reply(msg):
    text = msg["Text"]
    print("text:", text, text == "今日账单", text == "全部账单", msg)
    username = msg["User"].get("RemarkName") or msg["User"].get("NickName", "someone")
    user_id = msg["User"]["Uin"]
    if text == "今日账单":
        bills = today_bill(user_id)
        print("bills:", bills)
        return to_string(bills)
    if text == "全部账单":
        bills = all_bill(user_id)
        print("bills:", bills)
        return to_string(bills)
    code, res = check_account(text, "我自己")
    print("===>", code, res, text)
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
            username,
            msg.get("Text", ""),
        )
    )
    print("reply: %s" % response_msg)
    account_tips = "%s %.2f" % (bill, fee)
    res_msg = """{response_msg}
记账成功：{account_tips}""".format(account_tips=account_tips, response_msg=response_msg)
    print("===>", res_msg)
    save_data(username=username, bill_name=bill, bill_fee=fee, user_id=user_id)
    return res_msg


if __name__ == "__main__":
    try:
        itchat.auto_login()
    except Exception as e:
        print(f"{e}")
    friends = itchat.get_friends(update=True)[0:]
    itchat.run()
    #
    # while True:
    #     time.sleep(60 * 5)
    #     sendChatroomMsg(roomName="Gino", context=context)
