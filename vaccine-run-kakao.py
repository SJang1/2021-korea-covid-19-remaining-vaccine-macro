#!/usr/bin/env python3.9 -m nuitka
# -*- coding: utf-8 -*-
import browser_cookie3
import requests
import configparser
import json
import os
import sys
import time
from playsound import playsound
from datetime import datetime
import telepot
import unicodedata
import urllib3
import re

search_time = 0.2  # 잔여백신을 해당 시간마다 한번씩 검색합니다. 단위: 초
urllib3.disable_warnings()

jar = browser_cookie3.chrome(domain_name=".kakao.com")


# 기존 입력 값 로딩
def load_config():
    config_parser = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        try:
            config_parser.read('config.ini')

            while True:
                skip_input = str.lower(input("기존에 입력한 정보로 재검색하시겠습니까? Y/N : "))
                if skip_input == "y":
                    skip_input = True
                    break
                elif skip_input == "n":
                    skip_input = False
                    break
                else:
                    print("Y 또는 N을 입력해 주세요.")

            if skip_input:
                # 설정 파일이 있으면 최근 로그인 정보 로딩
                configuration = config_parser['config']
                previous_used_type = configuration["VAC"]
                previous_top_x = configuration["topX"]
                previous_top_y = configuration["topY"]
                previous_bottom_x = configuration["botX"]
                previous_bottom_y = configuration["botY"]
                return previous_used_type, previous_top_x, previous_top_y, previous_bottom_x, previous_bottom_y
            else:
                return None, None, None, None, None
        except ValueError:
            return None, None, None, None, None
    return None, None, None, None, None


def check_user_info_loaded():
    user_info_api = 'https://vaccine.kakao.com/api/v1/user'
    user_info_response = requests.get(
        user_info_api, headers=Headers.headers_vacc, cookies=jar, verify=False)
    user_info_json = json.loads(user_info_response.text)
    if user_info_json.get('error'):
        print("사용자 정보를 불러오는데 실패하였습니다.")
        print("Chrome 브라우저에서 카카오에 제대로 로그인되어있는지 확인해주세요.")
        print("로그인이 되어 있는데도 안된다면, 카카오톡에 들어가서 잔여백신 알림 신청을 한번 해보세요. 정보제공 동의가 나온다면 동의 후 다시 시도해주세요.")
        close()
    else:
        user_info = user_info_json.get("user")
        for key in user_info:
            value = user_info[key]
            # print(key, value)
            if key != 'status':
                continue
            if key == 'status' and value == "NORMAL":
                print("사용자 정보를 불러오는데 성공했습니다.")
                break
            elif key == 'status' and value == "UNKNOWN":
                print("상태를 알 수 없는 사용자입니다. 1339 또는 보건소에 문의해주세요.")
                close()
            else:
                print("이미 접종이 완료되었거나 예약이 완료된 사용자입니다.")
                close(success=None)


def fill_str_with_space(input_s, max_size=40, fill_char=" "):
    """
    - 길이가 긴 문자는 2칸으로 체크하고, 짧으면 1칸으로 체크함.
    - 최대 길이(max_size)는 40이며, input_s의 실제 길이가 이보다 짧으면
    남은 문자를 fill_char로 채운다.
    """
    length = 0
    for c in input_s:
        if unicodedata.east_asian_width(c) in ["F", "W"]:
            length += 2
        else:
            length += 1
    return input_s + fill_char * (max_size - length)


def is_in_range(coord_type, coord, user_min_x=-180.0, user_max_y=90.0):
    korea_coordinate = {      #Republic of Korea coordinate
        "min_x": 124.965323,
        "max_x": 130.416515,
        "min_y": 34.082053,
        "max_y": 38.634065
    }
    try:
        if coord_type == "x":
            return max(korea_coordinate["min_x"], user_min_x) <= float(coord) <= korea_coordinate["max_x"]
        elif coord_type == "y":
            return korea_coordinate["min_y"] <= float(coord) <= min(korea_coordinate["max_y"], user_max_y)
        else:
            return False
    except ValueError:
        # float 이외 값 입력 방지
        return False


def input_config():
    vaccine_candidates = [
        {"name": "아무거나", "code": "ANY"},
        {"name": "화이자", "code": "VEN00013"},
        {"name": "모더나", "code": "VEN00014"},
        {"name": "아스트라제네카", "code": "VEN00015"},
        {"name": "얀센", "code": "VEN00016"},
        {"name": "(미사용)", "code": "VEN00017"},
        {"name": "(미사용)", "code": "VEN00018"},
        {"name": "(미사용)", "code": "VEN00019"},
        {"name": "(미사용)", "code": "VEN00020"},
    ]
    vaccine_type = None
    while True:
        print("=== 백신 목록 ===")
        for vaccine in vaccine_candidates:
            if vaccine["name"] == "(미사용)":
                continue
            print(
                f"{fill_str_with_space(vaccine['name'], 10)} : {vaccine['code']}")

        vaccine_type = str.upper(input("예약시도할 백신 코드를 알려주세요: ").strip())
        if any(x["code"] == vaccine_type for x in vaccine_candidates) or vaccine_type.startswith("FORCE:"):
            if vaccine_type.startswith("FORCE:"):
                vaccine_type = vaccine_type[6:]

                print("경고: 강제 코드 입력모드를 사용하셨습니다.\n" +
                      "이 모드는 새로운 백신이 예약된 코드로 **등록되지 않은 경우에만** 사용해야 합니다.\n" +
                      "입력하신 코드가 정상적으로 작동하는 백신 코드인지 필히 확인해주세요.\n" +
                      f"현재 코드: '{vaccine_type}'\n")

                if (len(vaccine_type) != 8 or not vaccine_type.startswith("VEN") or not vaccine_type[3:].isdigit()):
                    print("입력하신 코드가 현재 알려진 백신 코드 형식이랑 맞지 않습니다.")
                    proceed = str.lower(input("진행하시겠습니까? Y/N : "))
                    if proceed == "y":
                        pass
                    elif proceed == "n":
                        continue
                    else:
                        print("Y 또는 N을 입력해 주세요.")
                        continue

            if next((x for x in vaccine_candidates if x["code"] == vaccine_type), {"name":""})["name"] == "(미사용)":
                print("현재 프로그램 버전에서 백신 이름이 등록되지 않은, 추후를 위해 미리 넣어둔 백신 코드입니다.\n" +
                      "입력하신 코드가 정상적으로 작동하는 백신 코드인지 필히 확인해주세요.\n" +
                      f"현재 코드: '{vaccine_type}'\n")

            break
        else:
            print("백신 코드를 확인해주세요.")

    print("사각형 모양으로 백신범위를 지정한 뒤, 해당 범위 안에 있는 백신을 조회해서 남은 백신이 있으면 Chrome 브라우저를 엽니다.")
    top_x = None
    while top_x is None:
        top_x = input("사각형의 위쪽 좌측 x값을 넣어주세요. 127.xxxxxx: ").strip()
        if not is_in_range(coord_type="x", coord=top_x):
            print(f"올바른 좌표 값이 아닙니다. 입력 값 : {top_x}")
            top_x = None

    top_y = None
    while top_y is None:
        top_y = input("사각형의 위쪽 좌측 y값을 넣어주세요 37.xxxxxx: ").strip()
        if not is_in_range(coord_type="y", coord=top_y):
            print(f"올바른 좌표 값이 아닙니다. 입력 값 : {top_y}")
            top_y = None

    bottom_x = None
    while bottom_x is None:
        bottom_x = input("사각형의 아래쪽 우측 x값을 넣어주세요 127.xxxxxx: ").strip()
        if not is_in_range(coord_type="x", coord=bottom_x, user_min_x=float(top_x)):
            print(f"올바른 좌표 값이 아닙니다. 입력 값 : {bottom_x}")
            bottom_x = None

    bottom_y = None
    while bottom_y is None:
        bottom_y = input("사각형의 아래쪽 우측 y값을 넣어주세요 37.xxxxxx: ").strip()
        if not is_in_range(coord_type="y", coord=bottom_y, user_max_y=float(top_y)):
            print(f"올바른 좌표 값이 아닙니다. 입력 값 : {bottom_y}")
            bottom_y = None

    dump_config(vaccine_type, top_x, top_y, bottom_x, bottom_y)
    return vaccine_type, top_x, top_y, bottom_x, bottom_y


def dump_config(vaccine_type, top_x, top_y, bottom_x, bottom_y):
    config_parser = configparser.ConfigParser()
    config_parser['config'] = {}
    conf = config_parser['config']
    conf['VAC'] = vaccine_type
    conf["topX"] = top_x
    conf["topY"] = top_y
    conf["botX"] = bottom_x
    conf["botY"] = bottom_y

    with open("config.ini", "w") as config_file:
        config_parser.write(config_file)


def clear():
    if 'win' in sys.platform.lower():
        os.system('cls')
    else:
        os.system('clear')


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def play_tada():
    playsound(resource_path('tada.mp3'))


def play_xylophon():
    playsound(resource_path('xylophon.mp3'))


def close(success=False):
    if success is True:
        play_tada()
        send_msg("잔여백신 예약 성공!! \n 카카오톡지갑을 확인하세요.")
    elif success is False:
        play_xylophon()
        send_msg("오류와 함께 잔여백신 예약 프로그램이 종료되었습니다.")
    else:
        pass
    input("Press Enter to close...")
    sys.exit()


def pretty_print(json_object):
    for org in json_object["organizations"]:
        if org.get('status') == "CLOSED" or org.get('status') == "EXHAUSTED" or org.get('status') == "UNAVAILABLE":
            continue
        print(
            f"잔여갯수: {org.get('leftCounts')}\t상태: {org.get('status')}\t기관명: {org.get('orgName')}\t주소: {org.get('address')}")


class Headers:
    headers_map = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://vaccine-map.kakao.com",
        "Accept-Language": "en-us",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KAKAOTALK 9.4.2",
        "Referer": "https://vaccine-map.kakao.com/",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Keep-Alive": "timeout=5, max=1000"
    }
    headers_vacc = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://vaccine.kakao.com",
        "Accept-Language": "en-us",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KAKAOTALK 9.4.2",
        "Referer": "https://vaccine.kakao.com/",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Keep-Alive": "timeout=5, max=1000"
    }


def try_reservation(organization_code, vaccine_type):
    reservation_url = 'https://vaccine.kakao.com/api/v1/reservation'
    data = {"from": "Map", "vaccineCode": vaccine_type,
            "orgCode": organization_code, "distance": None}
    response = requests.post(reservation_url, data=json.dumps(
        data), headers=Headers.headers_vacc, cookies=jar, verify=False)
    response_json = json.loads(response.text)
    for key in response_json:
        value = response_json[key]
        if key != 'code':
            continue
        if key == 'code' and value == "NO_VACANCY":
            print("잔여백신 접종 신청이 선착순 마감되었습니다.")
            time.sleep(0.08)
        elif key == 'code' and value == "TIMEOUT":
            print("TIMEOUT, 예약을 재시도합니다.")
            retry_reservation(organization_code, vaccine_type)
        elif key == 'code' and value == "SUCCESS":
            print("백신접종신청 성공!!!")
            organization_code_success = response_json.get("organization")
            print(
                f"병원이름: {organization_code_success.get('orgName')}\t" +
                f"전화번호: {organization_code_success.get('phoneNumber')}\t" +
                f"주소: {organization_code_success.get('address')}")
            close(success=True)
        else:
            print("ERROR. 아래 메시지를 보고, 예약이 신청된 병원 또는 1339에 예약이 되었는지 확인해보세요.")
            print(response.text)
            close()


def retry_reservation(organization_code, vaccine_type):
    reservation_url = 'https://vaccine.kakao.com/api/v1/reservation/retry'

    data = {"from": "Map", "vaccineCode": vaccine_type,
            "orgCode": organization_code, "distance": None}
    response = requests.post(reservation_url, data=json.dumps(
        data), headers=Headers.headers_vacc, cookies=jar, verify=False)
    response_json = json.loads(response.text)
    for key in response_json:
        value = response_json[key]
        if key != 'code':
            continue
        if key == 'code' and value == "NO_VACANCY":
            print("잔여백신 접종 신청이 선착순 마감되었습니다.")
            time.sleep(0.08)
        elif key == 'code' and value == "SUCCESS":
            print("백신접종신청 성공!!!")
            organization_code_success = response_json.get("organization")
            print(
                f"병원이름: {organization_code_success.get('orgName')}\t" +
                f"전화번호: {organization_code_success.get('phoneNumber')}\t" +
                f"주소: {organization_code_success.get('address')}")
            close(success=True)
        else:
            print("ERROR. 아래 메시지를 보고, 예약이 신청된 병원 또는 1339에 예약이 되었는지 확인해보세요.")
            print(response.text)
            close()

# ===================================== def ===================================== #


# Get Cookie
# driver = selenium.webdriver.Firefox()
# driver.get("https://cs.kakao.com")
# pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
# cookies = pickle.load(open("cookies.pkl", "rb"))
# for cookie in cookies:
#     driver.add_cookie(cookie)
#     print(cookie)

# pylint: disable=too-many-locals,too-many-statements,too-many-branches
def find_vaccine(vaccine_type, top_x, top_y, bottom_x, bottom_y):
    url = 'https://vaccine-map.kakao.com/api/v2/vaccine/left_count_by_coords'
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "onlyLeft": False, "order": "latitude",
            "topLeft": {"x": top_x, "y": top_y}}
    done = False
    found = None

    while not done:
        try:
            time.sleep(search_time)
            response = requests.post(url, data=json.dumps(
                data), headers=Headers.headers_map, verify=False, timeout=5)

            json_data = json.loads(response.text)

            pretty_print(json_data)
            print(datetime.now())

            for x in json_data.get("organizations"):
                if x.get('status') == "AVAILABLE" or x.get('leftCounts') != 0:
                    found = x
                    done = True
                    break

        except json.decoder.JSONDecodeError as decodeerror:
            print("JSONDecodeError : ", decodeerror)
            print("JSON string : ", response.text)
            close()

        except requests.exceptions.Timeout as timeouterror:
            print("Timeout Error : ", timeouterror)

        except requests.exceptions.SSLError as sslerror:
            print("SSL Error : ", sslerror)
            close()

        except requests.exceptions.ConnectionError as connectionerror:
            print("Connection Error : ", connectionerror)
            # See psf/requests#5430 to know why this is necessary.
            if not re.search('Read timed out', str(connectionerror), re.IGNORECASE):
                close()

        except requests.exceptions.HTTPError as httperror:
            print("Http Error : ", httperror)
            close()

        except requests.exceptions.RequestException as error:
            print("AnyException : ", error)
            close()

    if found is None:
        find_vaccine(vaccine_type, top_x, top_y, bottom_x, bottom_y)
    print(f"{found.get('orgName')} 에서 백신을 {found.get('leftCounts')}개 발견했습니다.")
    print(f"주소는 : {found.get('address')} 입니다.")
    organization_code = found.get('orgCode')

    # 실제 백신 남은수량 확인
    vaccine_found_code = None

    if vaccine_type == "ANY":  # ANY 백신 선택
        check_organization_url = f'https://vaccine.kakao.com/api/v2/org/org_code/{organization_code}'
        check_organization_response = requests.get(check_organization_url, headers=Headers.headers_vacc, cookies=jar,
                                                   verify=False)
        check_organization_data = json.loads(
            check_organization_response.text).get("lefts")
        for x in check_organization_data:
            if x.get('leftCount') != 0:
                found = x
                print(f"{x.get('vaccineName')} 백신을 {x.get('leftCount')}개 발견했습니다.")
                vaccine_found_code = x.get('vaccineCode')
                break
            else:
                print(f"{x.get('vaccineName')} 백신이 없습니다.")

    else:
        vaccine_found_code = vaccine_type
        print(f"{vaccine_found_code} 으로 예약을 시도합니다.")

    if vaccine_found_code and try_reservation(organization_code, vaccine_found_code):
        return None
    else:
        find_vaccine(vaccine_type, top_x, top_y, bottom_x, bottom_y)


def main_function():
    check_user_info_loaded()
    previous_used_type, previous_top_x, previous_top_y, previous_bottom_x, previous_bottom_y = load_config()
    if previous_used_type is None:
        vaccine_type, top_x, top_y, bottom_x, bottom_y = input_config()
    else:
        vaccine_type, top_x, top_y, bottom_x, bottom_y = previous_used_type, previous_top_x, previous_top_y, previous_bottom_x, previous_bottom_y
    find_vaccine(vaccine_type, top_x, top_y, bottom_x, bottom_y)
    close()


def send_msg(msg):
    config_parser = configparser.ConfigParser()
    if os.path.exists('telegram.txt'):
        try:
            config_parser.read('telegram.txt')
            print("Telegram으로 결과를 전송합니다.")
            tgtoken = config_parser["telegram"]["token"]
            tgid = config_parser["telegram"]["chatid"]
            bot = telepot.Bot(tgtoken)
            bot.sendMessage(tgid, msg)
            return
        except Exception as e:
            print("Telegram Error : ", e)
            return


# ===================================== run ===================================== #
if __name__ == '__main__':
    main_function()
