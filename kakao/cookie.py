import configparser
import os


# cookie.ini 안의 [chrome][cookie_file] 에서 경로를 로드함.
import platform
import browser_cookie3
from kakao.common import close


def load_cookie_config():
    config_parser = configparser.ConfigParser(interpolation=None)
    if os.path.exists('cookie.ini'):
        config_parser.read('cookie.ini')
        try:
            cookie_file = config_parser.get(
                'chrome', 'cookie_file', fallback=None)
            if cookie_file is None:
                return None

            indicator = cookie_file[0]
            if indicator == '~':
                cookie_path = os.path.expanduser(cookie_file)
            elif indicator in ('%', '$'):
                cookie_path = os.path.expandvars(cookie_file)
            else:
                cookie_path = cookie_file

            cookie_path = os.path.abspath(cookie_path)

            if os.path.exists(cookie_path):
                return cookie_path
            else:
                print("지정된 경로에 쿠키 파일이 존재하지 않습니다. 기본값으로 시도합니다.")
                return None
        finally:
            pass
    return None


# 저장된 쿠키 로드
def load_saved_cookie() -> (bool, dict):
    #  print('saved cookie loading')
    config_parser = configparser.ConfigParser(interpolation=None)
    if os.path.exists('cookie.ini'):
        try:
            config_parser.read('cookie.ini')
            cookie = config_parser['cookie_values']['_kawlt'].strip()

            if cookie is None or cookie == '':
                return False

            jar = {'_kawlt': cookie}
            return True, jar
        finally:
            pass
    return False, None


# 쿠키의 경로를 저장
def dump_cookie(value):
    config_parser = configparser.ConfigParser()
    config_parser.read('cookie.ini')

    with open('cookie.ini', 'w') as cookie_file:
        config_parser['cookie_values'] = {
            '_kawlt': value
        }
        config_parser.write(cookie_file)


# cookie 경로가 입력되지 않았을시, 쿠키 파일이 Default 경로에 있는지 확인함
# 경로가 입력되었거나, Default 경로의 쿠키가 존재해야 global jar 함수에 cookie를 로드함.
def load_cookie_from_chrome():
    cookie_file = load_cookie_config()
    if cookie_file is False:
        return None

    if cookie_file is None:
        cookie_path = None
        os_type = platform.system()
        if os_type == "Linux":
            # browser_cookie3 also checks beta version of google chrome's cookie file.
            cookie_path = os.path.expanduser("~/.config/google-chrome/Default/Cookies")
            if os.path.exists(cookie_path) is False:
                cookie_path = os.path.expanduser("~/.config/google-chrome-beta/Default/Cookies")
        elif os_type == "Darwin":
            cookie_path = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies")
        elif os_type == "Windows":
            cookie_path = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Cookies")
        else:  # Jython?
            print("지원하지 않는 환경입니다.")
            close()

        if os.path.exists(cookie_path) is False:
            print("기본 쿠키 파일 경로에 파일이 존재하지 않습니다. 아래 링크를 참조하여 쿠키 파일 경로를 지정해주세요.\n" +
                  "https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/discussions/403")
            close()

    jar = browser_cookie3.chrome(cookie_file=cookie_file, domain_name=".kakao.com")

    cookie_dict = {}

    # 쿠키를 cookie.ini 에 저장한다
    for cookie in jar:
        if cookie.name == '_kawlt':
            cookie_dict['_kawlt'] = cookie.value
            dump_cookie(cookie.value)
            break

    return cookie_dict
