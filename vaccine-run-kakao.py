#!/usr/bin/python
# -*- coding: utf-8 -*-


search_time = 0.26    # 잔여백신을 해당 시간마다 한번씩 검색합니다. 단위: 초


import requests
import json
import urllib3
import os
import time
import datetime
import configparser
import sys
import browser_cookie3
import http.cookiejar
from pygame import mixer
from sys import platform
urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5
urllib3.util.Retry.allowed_methods=frozenset(['GET', 'POST'])
jar = http.cookiejar.CookieJar()
jar = browser_cookie3.chrome(domain_name=".kakao.com")

skip_input = False


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def close():
    input("Press Enter to close...")
    sys.exit()

def clear():
    if 'win' in sys.platform.lower():
        os.system('cls')
    else:
        os.system('clear')

def play_sound():
    mixer.init()
    mixer.music.load(resource_path('tada.mp3'))
    mixer.music.play()


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
        if skip_input == "y":
            skip_input = True
        elif skip_input == "n":
            skip_input = False
        else:
            print("Y 또는 N을 입력해 주세요.")
            close()
        
    except ValueError:
        pass


def pretty_print(json_string):
    json_object = json.loads(json_string)
    for org in json_object["organizations"]:
        if org.get('status') == "CLOSED" or org.get('status') == "EXHAUSTED":
            continue
        print(f"잔여갯수: {org.get('leftCounts')}\t상태: {org.get('status')}\t기관명: {org.get('orgName')}\t주소: {org.get('address')}")

class headers:
    headers_map = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://vaccine-map.kakao.com",
        "Accept-Language": "en-us",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KAKAOTALK 9.3.8",
        "Referer":"https://vaccine-map.kakao.com/",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Keep-Alive": "timeout=5, max=1000"
    }
    headers_vacc = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://vaccine.kakao.com",
        "Accept-Language": "en-us",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KAKAOTALK 9.3.8",
        "Referer":"https://vaccine.kakao.com/",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Keep-Alive": "timeout=5, max=1000"
    }

def try_reservation(orgCdCode, vacc_code):
    for i in range(6):
        ReservationURL = 'https://vaccine.kakao.com/api/v1/reservation'
        Reservation_APIdata = {"from":"Map","vaccineCode":vacc_code,"orgCode":orgCdCode,"distance":"null"}
        Reservation_Response = requests.post(ReservationURL, data=json.dumps(Reservation_APIdata), headers=headers.headers_vacc, cookies=jar, verify=False)
        Reservation_Response_jsonloaded = json.loads(Reservation_Response.text)
        print(Reservation_Response_jsonloaded)
        for key in Reservation_Response_jsonloaded:
            value = Reservation_Response_jsonloaded[key]
            if key != 'code':
                continue
            if key == 'code' and value == "NO_VACANCY":
                print("잔여백신 접종 신청이 선착순 마감되었습니다.")
                time.sleep(0.08)
            elif key == 'code' and value == "SUCCESS":
                print("백신접종신청 성공!!!")
                Success_Org = Reservation_Response_jsonloaded["organization"]
                print(f"병원이름: {Success_Org.get('orgName')}\t전화번호: {Success_Org.get('phoneNumber')}\t주소: {Success_Org.get('address')}\t운영시간: {Success_Org.get('openHour')}")
                play_sound()
                close()
            else:
                print("ERROR. 아래 메시지를 보고, 예약이 신청된 병원 또는 1339에 예약이 되었는지 확인해보세요.")
                print(Reservation_Response.text)
                play_sound()
                close()

    find_vaccine() # Close 안되면 다시 백신검색


# ===================================== def ===================================== #



# Get Cookie
# driver = selenium.webdriver.Firefox()
# driver.get("https://cs.kakao.com")
# pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
# cookies = pickle.load(open("cookies.pkl", "rb"))
# for cookie in cookies:
#     driver.add_cookie(cookie)
#     print(cookie)


UserInfoAPI = 'https://vaccine.kakao.com/api/v1/user'
# print(jar)
UserInfo_response = requests.get(UserInfoAPI, headers=headers.headers_vacc, cookies=jar, verify=False)
# print(UserInfo_response.text)

# {"error":"error occurred"}
UserInfoJsonLoaded = json.loads(UserInfo_response.text)
if UserInfoJsonLoaded.get('error'):
    print("사용자 정보를 불러오는데 실패하였습니다.")
    print("Chrome 브라우저에서 카카오에 제대로 로그인되어있는지 확인해주세요.")
    print("로그인이 되어 있는데도 안된다면, 카카오톡에 들어가서 잔여백신 알림 신청을 한번 해보세요. 정보제공 동의가 나온다면 동의 후 다시 시도해주세요.")
    close()
else:
    UserInfojsonData = UserInfoJsonLoaded.get("user")
    for key in UserInfojsonData:
        value = UserInfojsonData[key]
        # print(key, value)
        if key != 'status':
            continue
        if key == 'status' and value == "NORMAL":
            print("사용자 정보를 불러오는데 성공했습니다.")
            break
        else:
            print("이미 접종이 완료되었거나 예약이 완료된 사용자입니다.")
            close()


if skip_input == False:
    VAC = None
    while VAC == None:
        print("예약시도할 백신 코드를 알려주세요.")
        print("화이자         : VEN00013")
        print("모더나         : VEN00014")
        print("아스크라제네카   : VEN00015")
        print("얀센          : VEN00016")
        print("아무거나       : ANY")
        VAC = str.upper(input(f"예약시도할 백신 코드를 알려주세요. (최근 사용 : {prevVAC}): "))
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
elif skip_input == True:
    VAC = prevVAC
    topx = prevtopx
    topy = prevtopy
    botx = prevbotx
    boty = prevboty
else:
    print("문제가 발생했습니다. 프로그램을 종료합니다.")
    close()



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

def find_vaccine():
    print(APIdata)

    done = False
    while done == False:
        time.sleep(search_time)
        response = requests.post(APIURL, data=json.dumps(APIdata), headers=headers.headers_map, cookies=jar, verify=False)

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




    # 실제 백신 남은수량 확인
    VAC_found_code = ''

    if VAC != "ANY": # 특정 백신 선택
        VAC_found_code = VAC
    else: # ANY 백신 선택
        Check_Org_URL = 'https://vaccine.kakao.com/api/v2/org/org_code/'+ orgCdCode
        Check_Org_response = requests.get(Check_Org_URL, headers=headers.headers_vacc, cookies=jar, verify=False)
        # print(Check_Org_response.text)
        Check_Org_jsonloaded = json.loads(Check_Org_response.text)
        Check_Org_jsonData = Check_Org_jsonloaded["lefts"]
        for x in Check_Org_jsonData:
            if x.get('leftCount') != 0:
                found = x
                print(found)
                VAC_found_code = x.get('vaccineCode')
                break
            else:
                print("검색 도중 백신이 모두 소진되었습니다.")
    

    if VAC_found_code != '':
        try_reservation(orgCdCode, VAC_found_code)
    else:
        find_vaccine()


# ===================================== run ===================================== #

find_vaccine()
close()
