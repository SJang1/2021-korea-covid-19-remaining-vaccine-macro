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


# pylint: disable=too-many-locals,too-many-statements,too-many-branches,too-many-arguments
def find_vaccine(cookie, search_time, vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left):
    url = 'https://vaccine-map.kakao.com/api/v3/vaccine/left_count_by_coords'
    data = {"bottomRight": {"x": bottom_x, "y": bottom_y}, "onlyLeft": only_left, "order": "count",
            "topLeft": {"x": top_x, "y": top_y}}
    done = False
    found = None
    prevSearch = None

    while not done:
        try:
            time.sleep(search_time)
            response = requests.post(url, data=json.dumps(data), headers=header_map, verify=False, timeout=5)

            try:
                json_data = json.loads(response.text)
                for x in list(reversed(json_data.get("organizations"))):
                    if x.get('status') == "AVAILABLE" or x.get('leftCounts') != 0:
                        if prevSearch:
                            prev = list(filter(lambda org: org.get('orgCode') == x.get('orgCode'), prevSearch))
                            if len(prev) and prev[0].get('leftCounts') == x.get('leftCounts'):
                                continue

                        print(f"{x.get('orgName')} ?????? ????????? {x.get('leftCounts')}??? ??????????????????.")
                        found, target = check_vaccine_availablity(x, vaccine_type, cookie)
                        if found:
                            print(f"?????????: {x.get('address')} ?????????.")
                            done = True
                            break
                        else:
                            print("????????? ?????? ????????? ????????????.")

                if not done:
                    prevSearch = json_data.get("organizations")
                    pretty_print(json_data)
                    print(datetime.now())

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

    vaccine_found_code = None

    if found is None:
        find_vaccine(cookie, search_time, vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left)
        return None
    else:
        vaccine_found_code = found.get('vaccineCode')
        organization_code = target

    if vaccine_found_code and try_reservation(organization_code, vaccine_found_code, cookie):
        return None
    else:
        find_vaccine(cookie, search_time, vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left)
        return None


def check_vaccine_availablity(data, vaccine_type, cookie):
    check_organization_url = f'https://vaccine.kakao.com/api/v3/org/org_code/{data.get("orgCode")}'
    check_organization_response = requests.get(check_organization_url, headers=headers_vaccine, cookies=cookie, verify=False)
    check_organization_data = json.loads(check_organization_response.text).get("lefts")
    for x in vaccine_type:
        find = list(filter(lambda v: v.get('vaccineCode') == x and v.get('leftCount') != 0, check_organization_data))
        if len(find):
            print(f"{find[0].get('vaccineName')} {find[0].get('leftCount')}?????? ????????????.")
            return [find[0], data.get("orgCode")]
    return [False, False]


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
            print("???????????? ?????? ????????? ????????? ?????????????????????.")
            retry_reservation(organization_code, vaccine_type, jar)

        elif key == 'code' and value == "TIMEOUT":
            print("TIMEOUT, ????????? ??????????????????.")
            retry_reservation(organization_code, vaccine_type, jar)
        elif key == 'code' and value == "SUCCESS":
            print("?????????????????? ??????!!!")
            organization_code_success = response_json.get("organization")
            print(
                f"????????????: {organization_code_success.get('orgName')}\t" +
                f"????????????: {organization_code_success.get('phoneNumber')}\t" +
                f"??????: {organization_code_success.get('address')}")
            close(success=True)
        else:
            print("ERROR. ?????? ???????????? ??????, ????????? ????????? ?????? ?????? 1339??? ????????? ???????????? ??????????????????.")
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
            print("???????????? ?????? ????????? ????????? ?????????????????????.")
        elif key == 'code' and value == "SUCCESS":
            print("?????????????????? ??????!!!")
            organization_code_success = response_json.get("organization")
            print(
                f"????????????: {organization_code_success.get('orgName')}\t" +
                f"????????????: {organization_code_success.get('phoneNumber')}\t" +
                f"??????: {organization_code_success.get('address')}")
            close(success=True)
        else:
            print("ERROR. ?????? ???????????? ??????, ????????? ????????? ?????? ?????? 1339??? ????????? ???????????? ??????????????????.")
            print(response.text)
            close()
