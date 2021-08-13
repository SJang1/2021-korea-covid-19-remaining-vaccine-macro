import json

import requests

from kakao.common import close
from kakao.cookie import load_cookie_from_chrome
from kakao.request import headers_vaccine


# 쿠키를 통해 사용자의 정보를 불러오는 함수
def check_user_info_loaded(jar):
    user_info_api = 'https://vaccine.kakao.com/api/v1/user'
    user_info_response = requests.get(user_info_api, headers=headers_vaccine, cookies=jar, verify=False)
    user_info_json = json.loads(user_info_response.text)
    if user_info_json.get('error'):
        # cookie.ini 에 있는 쿠키가 유통기한 지났을 수 있다
        chrome_cookie = load_cookie_from_chrome()

        # 크롬 브라우저에서 새로운 쿠키를 찾았으면 다시 체크 시작 한다
        if jar != chrome_cookie:
            #  print('new cookie value from chrome detected')
            check_user_info_loaded(chrome_cookie)
            return

        print("사용자 정보를 불러오는데 실패하였습니다.")
        print("Chrome 브라우저에서 카카오에 제대로 로그인되어있는지 확인해주세요.")
        print("로그인이 되어 있는데도 안된다면, 카카오톡에 들어가서 잔여백신 알림 신청을 한번 해보세요. 정보제공 동의가 나온다면 동의 후 다시 시도해주세요.")
        close()
    else:
        user_info = user_info_json.get("user")
        if user_info['status'] == "NORMAL":
            print(f"{user_info['name']}님 안녕하세요.")
        elif user_info['status'] == "UNKNOWN":
            print("상태를 알 수 없는 사용자입니다. 1339 또는 보건소에 문의해주세요.")
            close(success=None)
        elif user_info['status'] == "REFUSED":
            print(f"{user_info['name']}님은 백신을 예약하고 방문하지 않은 사용자로 파악됩니다. 잔여백신 예약이 불가합니다.")
            close(success=None)
        elif user_info['status'] == "ALREADY_RESERVED" or user_info['status'] == "ALREADY_VACCINATED":
            print(f"{user_info['name']}님은 이미 예약 또는 접종이 완료된 사용자입니다.")
            close(success=None)
        else:
            print(f"알려지지 않은 상태 코드입니다. 상태코드:{user_info['status']}")
            print("상태 코드 정보와 함께 Issues 생성 부탁드립니다.")
            close()
