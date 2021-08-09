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

banlist = {}

# pylint: disable=too-many-locals,too-many-statements,too-many-branches,too-many-arguments
def find_vaccine(cookie, search_time, vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left):
    global banlist
    url = 'https://vaccine-map.kakao.com/api/v3/vaccine/left_count_by_coords'
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "onlyLeft": only_left, "order": "count",
            "topLeft": {"x": top_x, "y": top_y}}
    done = False
    found = None
    all_list = []

    while not done:
        try:
            time.sleep(search_time)
            response = requests.post(url, data=json.dumps(data), headers=header_map, verify=False, timeout=5)

            try:
                json_data = json.loads(response.text)

                for x in json_data.get("organizations"):
                    orgName = x.get('orgName')
                    if orgName in banlist.keys() and banlist[orgName] == x.get('leftCounts'):
                        # it is banned.
                        continue
                    if x.get('status') == "AVAILABLE" or x.get('leftCounts') != 0:
                        found = x
                        all_list.append(x)
                        done = True

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

    if found is None:
        return True  # no_vaccine = True

    # 실제 백신 남은수량 확인
    vaccine_found_code = None

    if vaccine_type == "ANY":  # ANY 백신 선택
        print(f"{found.get('orgName')} 에서 백신을 {found.get('leftCounts')}개 발견했습니다.")
        print(f"주소는 : {found.get('address')} 입니다.")
        organization_code = found.get('orgCode')
        check_organization_url = f'https://vaccine.kakao.com/api/v3/org/org_code/{organization_code}'
        check_organization_response = requests.get(check_organization_url, headers=headers_vaccine, cookies=cookie, verify=False)
        check_organization_data = json.loads(check_organization_response.text).get("lefts")
        for x in check_organization_data:
            if x.get('leftCount') != 0:
                print(f"{x.get('vaccineName')} 백신을 {x.get('leftCount')}개 발견했습니다.")
                vaccine_found_code = x.get('vaccineCode')
                break
            else:
                print(f"{x.get('vaccineName')} 백신이 없습니다.")

    else:
        for y in all_list:
            print(f"{y.get('orgName')} 에서 백신을 {y.get('leftCounts')}개 발견했습니다.")
            print(f"주소는 : {y.get('address')} 입니다.")
            organization_code = y.get('orgCode')
            check_organization_url = f'https://vaccine.kakao.com/api/v3/org/org_code/{organization_code}'
            check_organization_response = requests.get(check_organization_url, headers=headers_vaccine, cookies=cookie, verify=False)
            check_organization_data = json.loads(check_organization_response.text).get("lefts")
            is_vac = False
            for x in check_organization_data:
                if x.get('vaccineCode') == vaccine_type and x.get('leftCount') != 0:
                    is_vac = True
                    print(f"{x.get('vaccineName')} 백신을 {x.get('leftCount')}개 발견했습니다.")
                    vaccine_found_code = vaccine_type
                    print(f"{vaccine_found_code} 으로 예약을 시도합니다.")        
                    try_reservation(organization_code, vaccine_found_code, cookie)
            if not is_vac:
                banlist[y.get('orgName')] = y.get('leftCounts')
                print(f"{vaccine_type} 백신은 없습니다.")
                

    if vaccine_found_code:
        try_reservation(organization_code, vaccine_found_code, cookie)

    return True  # no_vaccine = True


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
