import json
import re
import time
from datetime import datetime

import requests
import urllib3

from kakao.common import pretty_print, close

urllib3.disable_warnings()
header_map = {
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

headers_vaccine = {
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

prevSearch = None

# pylint: disable=too-many-locals,too-many-statements,too-many-branches,too-many-arguments
def find_vaccine(cookie, search_time, vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left):
    global prevSearch
    url = 'https://vaccine-map.kakao.com/api/v3/vaccine/left_count_by_coords'
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "onlyLeft": only_left, "order": "count",
            "topLeft": {"x": top_x, "y": top_y}}
    done = False
    all_list = []

    while not done:
        try:
            time.sleep(search_time)
            response = requests.post(url, data=json.dumps(data), headers=header_map, verify=False, timeout=5)

            try:
                json_data = json.loads(response.text)
                for x in json_data.get("organizations"):
                    orgName = x.get('orgName')
                    if x.get('status') == "AVAILABLE" or x.get('leftCounts') != 0:
                        if prevSearch:
                            prev = list(filter(lambda org: org.get('orgName') == x.get('orgName'), prevSearch))
                            if len(prev) and prev[0].get('leftCounts') == x.get('leftCounts'):
                                continue

                        all_list.append(x)
                        done = True

                prevSearch = json_data.get("organizations")
                if not done:
                    pretty_print(json_data)
                    print(datetime.now())
                else:
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

    # 실제 백신 남은수량 확인
    vaccine_found_code = None

    for y in all_list:
        print(f"{y.get('orgName')} 에서 백신을 {y.get('leftCounts')}개 발견했습니다.")
        vaccine_found_code = get_available_vaccine(y, vaccine_type, cookie)
        if vaccine_found_code:
            organization_code = y.get('orgCode')
            try_reservation(organization_code, vaccine_found_code, cookie)

    return True  # no_vaccine = True

def get_available_vaccine(data, vaccine_type, cookie):
    check_organization_url = f'https://vaccine.kakao.com/api/v3/org/org_code/{data.get("orgCode")}'
    check_organization_response = requests.get(check_organization_url, headers=headers_vaccine, cookies=cookie, verify=False)
    check_organization_data = json.loads(check_organization_response.text).get("lefts")
    for x in vaccine_type:
        find = list(filter(lambda v: v.get('vaccineCode') == x and v.get('leftCount') != 0, check_organization_data))
        if len(find):
            print(f"{find[0].get('vaccineName')} {find[0].get('leftCount')}개가 있습니다.")
            return find[0].get('vaccineName')
    print(f"{vaccine_type} 백신은 없습니다.")
    return None


def try_reservation(organization_code, vaccine_type, jar):
    reservation_url = 'https://vaccine.kakao.com/api/v2/reservation'
    data = {"from": "List", "vaccineCode": vaccine_type,
            "orgCode": organization_code, "distance": None}
    response = requests.post(reservation_url, data=json.dumps(data), headers=headers_vaccine, cookies=jar, verify=False)
    response_json = json.loads(response.text)
    for key in response_json:
        value = response_json[key]
        if key != 'code':
            continue
        if key == 'code' and value == "NO_VACANCY":
            print("잔여백신 접종 신청이 선착순 마감되었습니다.")
        elif key == 'code' and value == "TIMEOUT":
            print("TIMEOUT, 예약을 재시도합니다.")
            retry_reservation(organization_code, vaccine_type, jar)
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


def retry_reservation(organization_code, vaccine_type, jar):
    reservation_url = 'https://vaccine.kakao.com/api/v2/reservation/retry'

    data = {"from": "List", "vaccineCode": vaccine_type,
            "orgCode": organization_code, "distance": None}
    response = requests.post(reservation_url, data=json.dumps(data), headers=headers_vaccine, cookies=jar, verify=False)
    response_json = json.loads(response.text)
    for key in response_json:
        value = response_json[key]
        if key != 'code':
            continue
        if key == 'code' and value == "NO_VACANCY":
            print("잔여백신 접종 신청이 선착순 마감되었습니다.")
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
