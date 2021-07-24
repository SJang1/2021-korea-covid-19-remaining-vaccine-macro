#!/usr/bin/python
# -*- coding: utf-8 -*-


search_time = 0.3    # 잔여백신을 해당 시간마다 한번씩 검색합니다. 단위: 초
open_delay = 0        # 잔여백신 발생 시 브라우저를 열기 전 지연시간. 단위: 초




import requests
import json
import urllib3
import os
import time
import datetime
import configparser
from sys import platform
urllib3.disable_warnings()

skip_input = "n"
config_parser = configparser.ConfigParser()
prevVAC = None
prevtopx = None
prevtopy = None
prevbotx = None
prevboty = None
if os.path.exists('config.ini'):
    try:
        config_parser.read('config.ini')

        # 설정 파일이 있으면 최근 로그인 정보 로딩
        configuration = config_parser['config']
        prevVAC = configuration["VAC"]
        prevtopx = configuration["topX"]
        prevtopy = configuration["topY"]
        prevbotx = configuration["botX"]
        prevboty = configuration["botY"]
        
        skip_input = str.lower(input("기존에 입력한 정보로 재검색하시겠습니까? Y/N : "))
        
    except ValueError:
        pass

def pretty_print(json_string):
    json_object = json.loads(json_string)
    for org in json_object["organizations"]:
        if org.get('status') == "CLOSED" or org.get('status') == "EXHAUSTED":
            continue
        print(f"잔여갯수: {org.get('leftCounts')}\t상태: {org.get('status')}\t기관명: {org.get('orgName')}\t주소: {org.get('address')}")

# ===================================== def ===================================== #
if skip_input != "y":
    VAC = None
    while VAC == None:
        print("예약시도할 백신 코드를 알려주세요.")
        print("화이자         : VEN00013")
        print("모더나         : VEN00014")
        print("아스크라제네카   : VEN00015")
        print("얀센          : VEN00016")
        VAC = input(f"예약시도할 백신 코드를 알려주세요.(최근 사용 : {prevVAC}): ")
        if not VAC.strip():
            VAC = prevVAC
            
    print("사각형 모양으로 백신범위를 지정한 뒤, 해당 범위 안에 있는 백신을 조회해서 남은 백신이 있으면 Chrome 브라우저를 엽니다.")
    topx = None
    while topx == None:
        topx = input(f"사각형의 위쪽 좌측 x값을 넣어주세요. 127.xxxxxx(최근 사용 : {prevtopx}): ")
        if not topx.strip():
            topx = prevtopx
    topy = None
    while topy == None:
        topy = input(f"사각형의 위쪽 좌측 y값을 넣어주세요 37.xxxxx(최근 사용 : {prevtopy}): ")
        if not topy.strip():
            topy = prevtopy
    botx = None
    while botx == None:
        botx = input(f"사각형의 아래쪽 우측 x값을 넣어주세요 127.xxxxx(최근 사용 : {prevbotx}): ")
        if not botx.strip():
            botx = prevbotx
    boty = None
    while boty == None:
        boty = input(f"사각형의 아래쪽 우측 y값을 넣어주세요 37.xxxxx(최근 사용 : {prevboty}): ")
        if not boty.strip():
            boty = prevboty
else:
    VAC = prevVAC
    topx = prevtopx
    topy = prevtopy
    botx = prevbotx
    boty = prevboty

    
APIURL = 'https://vaccine-map.kakao.com/api/v2/vaccine/left_count_by_coords'
APIdata = {"bottomRight":{"x":botx ,"y":boty},"onlyLeft": False,"order":"latitude","topLeft":{"x":topx,"y":topy}}
config_parser['config'] = {}
conf = config_parser['config']
conf['VAC'] = VAC
conf["topX"] = topx
conf["topY"] = topy
conf["botX"] = botx
conf["botY"] = boty

with open("config.ini", "w") as config_file:
    config_parser.write(config_file)

print(APIdata)
headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=utf-8",
    "Origin": "https://vaccine-map.kakao.com",
    "Accept-Language": "en-us",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KAKAOTALK 9.3.8",
    "Referer":"https://vaccine-map.kakao.com/",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close"
}

done = False
while done == False:
    time.sleep(search_time)
    response = requests.post(APIURL, data=json.dumps(APIdata), headers=headers, verify=False)

    received_API_status_code = response.status_code
    received_API_data = response.text

    pretty_print(received_API_data)
    print(datetime.datetime.now())

    jsonloaded = json.loads(received_API_data)
    jsonData = jsonloaded["organizations"]
    found = False
    for x in jsonData:
        if x.get('status') == "AVAILABLE" or x.get('leftCounts') != 0:
            found = x
            done = True
            break
        # keys = x.keys()
        # print(keys)
        # values = x.values()
        # print(values)


print("--- found")
print(found)
orgCdCode = x.get('orgCode')
latkey = x.get('y')
lngkey = x.get('x')

time.sleep(open_delay)
    os.system(f'start chrome.exe "https://vaccine.kakao.com/detail/{orgCdCode}?let=&ing=&from" '')
    os.system(f'start chrome.exe "https://vaccine.kakao.com/reservation/{orgCdCode}?from=Map&code={VAC}"')

input("Press Enter to continue...")
