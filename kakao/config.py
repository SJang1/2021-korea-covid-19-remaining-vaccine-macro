import configparser
import os

from kakao.common import fill_str_with_space


def is_in_range(coord_type, coord, user_min_x=-180.0, user_max_y=90.0):
    korea_coordinate = {  # Republic of Korea coordinate
        "min_x": 124.5,
        "max_x": 132.0,
        "min_y": 33.0,
        "max_y": 38.9
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


# pylint: disable=too-many-branches
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

                if len(vaccine_type) != 8 or not vaccine_type.startswith("VEN") or not vaccine_type[3:].isdigit():
                    print("입력하신 코드가 현재 알려진 백신 코드 형식이랑 맞지 않습니다.")
                    proceed = str.lower(input("진행하시겠습니까? Y/N : "))
                    if proceed == "y":
                        pass
                    elif proceed == "n":
                        continue
                    else:
                        print("Y 또는 N을 입력해 주세요.")
                        continue

            if next((x for x in vaccine_candidates if x["code"] == vaccine_type), {"name": ""})["name"] == "(미사용)":
                print("현재 프로그램 버전에서 백신 이름이 등록되지 않은, 추후를 위해 미리 넣어둔 백신 코드입니다.\n" +
                      "입력하신 코드가 정상적으로 작동하는 백신 코드인지 필히 확인해주세요.\n" +
                      f"현재 코드: '{vaccine_type}'\n")

            break
        else:
            print("백신 코드를 확인해주세요.")

    print("사각형 모양으로 백신범위를 지정한 뒤, 해당 범위 안에 있는 백신을 조회해서 남은 백신이 있으면 해당 병원에 예약을 시도합니다.")
    print("경위도는 구글 맵에서 원하는 위치를 우클릭하여 복사할 수 있습니다.")
    top_x = None
    top_y = None
    while top_x is None or top_y is None:
        top_y, top_x = input("사각형의 왼쪽 위 경위도를 넣어주세요. 37.28631662121671, 126.81741443463375: ").strip().split(",")
        if not is_in_range(coord_type="x", coord=top_x) or not is_in_range(coord_type="y", coord=top_y):
            print(f"올바른 좌표 값이 아닙니다. 입력 값 : {top_y}, {top_x}")
            top_x = None
            top_y = None
        else:
            top_x = top_x.strip()
            top_y = top_y.strip()

    bottom_x = None
    bottom_y = None
    while bottom_x is None or bottom_y is None:
        bottom_y, bottom_x = input("사각형의 오른쪽 아래 경위도를 넣어주세요. 37.28631662121671, 126.81741443463375: ").strip().split(",")
        if not is_in_range(coord_type="x", coord=bottom_x) or not is_in_range(coord_type="y", coord=bottom_y):
            print(f"올바른 좌표 값이 아닙니다. 입력 값 : {bottom_y}, {bottom_x}")
            bottom_x = None
            bottom_y = None
        else:
            bottom_x = bottom_x.strip()
            bottom_y = bottom_y.strip()

    only_left = None
    while only_left is None:
        only_left = str.lower(input("남은 잔여백신이 있는 병원만 조회하시겠습니까? Y/N : "))
        if only_left == "y":
            only_left = True
        elif only_left == "n":
            only_left = False
        else:
            print("Y 또는 N을 입력해 주세요.")
            only_left = None

    dump_config(vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left)
    return vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left


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
                try:
                    # 설정 파일이 있으면 최근 로그인 정보 로딩
                    configuration = config_parser['config']
                    previous_used_type = configuration["VAC"]
                    previous_top_x = configuration["topX"]
                    previous_top_y = configuration["topY"]
                    previous_bottom_x = configuration["botX"]
                    previous_bottom_y = configuration["botY"]
                    previous_only_left = configuration["onlyLeft"] == "True"
                    return previous_used_type, previous_top_x, previous_top_y, previous_bottom_x, previous_bottom_y, previous_only_left
                except KeyError:
                    print('기존에 입력한 정보가 없습니다.')
            else:
                return None, None, None, None, None, None
        except ValueError:
            return None, None, None, None, None, None
    return None, None, None, None, None, None


# pylint: disable=too-many-arguments
def dump_config(vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left, search_time=0.2):
    config_parser = configparser.ConfigParser()
    config_parser['config'] = {}
    conf = config_parser['config']
    conf['VAC'] = vaccine_type
    conf["topX"] = top_x
    conf["topY"] = top_y
    conf["botX"] = bottom_x
    conf["botY"] = bottom_y
    conf["search_time"] = str(search_time)
    conf["onlyLeft"] = "True" if only_left else "False"

    with open("config.ini", "w") as config_file:
        config_parser.write(config_file)


def load_search_time():
    config_parser = configparser.ConfigParser()
    search_time = 0.2
    if os.path.exists('config.ini'):
        config_parser.read('config.ini')
        input_time = config_parser.getfloat('config', 'search_time', fallback=0.2)

        if input_time < 0.1:
            confirm_input = None
            while confirm_input is None:
                confirm_input = str.lower(input("과도하게 딜레이를 줄이면 계정 정지의 위험이 있습니다. 계속하시겠습니까? Y/N : "))
                if confirm_input == "y":
                    search_time = input_time
                elif confirm_input == "n":
                    print("검색 주기가 기본값 0.2로 설정되었습니다.")
                else:
                    print("Y 또는 N을 입력해 주세요.")
                    confirm_input = None
        else:
            search_time = input_time
    return search_time
