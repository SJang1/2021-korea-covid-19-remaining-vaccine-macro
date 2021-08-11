import os
import sys
import configparser
import unicodedata

import telepot
from playsound import playsound, PlaysoundException


def close(success=False):
    if success is True:
        send_msg("잔여백신 예약 성공!! \n 카카오톡지갑을 확인하세요.")
        play_tada()
    elif success is False:
        send_msg("오류와 함께 잔여백신 예약 프로그램이 종료되었습니다.")
        play_xylophon()
    else:
        pass
    input("Press Enter to close...")
    sys.exit()


def clear():
    if 'win' in sys.platform.lower():
        os.system('cls')
    else:
        os.system('clear')


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def play_tada():
    try:
        playsound(resource_path('sound/tada.mp3'))
    except PlaysoundException:
        print("ERROR: sound/tada.mp3를 재생하지 못했습니다.")


def play_xylophon():
    try:
        playsound(resource_path('sound/xylophon.mp3'))
    except PlaysoundException:
        print("ERROR: sound/xylophon.mp3를 재생하지 못했습니다.")


def send_msg(msg):
    config_parser = configparser.ConfigParser()
    if os.path.exists('telegram.txt'):
        try:
            config_parser.read('telegram.txt')
            print("Telegram 으로 결과를 전송합니다.")
            telegram_token = config_parser["telegram"]["token"]
            telegram_id = config_parser["telegram"]["chatid"]
            bot = telepot.Bot(telegram_token)
            bot.sendMessage(telegram_id, msg)
            return
        except Exception as e:
            print("Telegram Error : ", e)
            return


def pretty_print(json_object):
    available_organization_count = 0
    
    for org in json_object["organizations"]:
        if org.get('status') == "CLOSED" or org.get('status') == "EXHAUSTED" or org.get('status') == "UNAVAILABLE":
            continue
        print(f"잔여갯수: {org.get('leftCounts')}\t상태: {org.get('status')}\t기관명: {org.get('orgName')}\t주소: {org.get('address')}")
        available_organization_count += 1
        
    if len(json_object["organizations"]) == 0:
        print("범위 내에 검색이 되는 병원이 없습니다. 좌표값을 다시 확인해주세요.")
    elif available_organization_count == 0:
        print("범위 내 영업중인 병원이 없습니다. 좌표를 다시 설정해주시거나, 병원 영업시간 내 이용해주세요.")


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
