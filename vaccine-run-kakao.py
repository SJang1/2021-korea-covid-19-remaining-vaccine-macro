#!/usr/bin/env python3.9 -m nuitka
# -*- coding: utf-8 -*-
from kakao.common import close
from kakao.config import load_search_time, load_config, input_config
from kakao.cookie import load_saved_cookie, load_cookie_from_chrome
from kakao.request import find_vaccine
from kakao.user import check_user_info_loaded


def main_function():
    got_cookie, cookie = load_saved_cookie()
    if not got_cookie:
        cookie = load_cookie_from_chrome()

    search_time = load_search_time()
    check_user_info_loaded(cookie)
    previous_used_type, previous_top_x, previous_top_y, previous_bottom_x, previous_bottom_y, only_left = load_config()
    if previous_used_type is None:
        vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left = input_config()
    else:
        vaccine_type, top_x, top_y, bottom_x, bottom_y = previous_used_type, previous_top_x, previous_top_y, previous_bottom_x, previous_bottom_y
    no_vaccine = True
    while no_vaccine:
        no_vaccine = find_vaccine(cookie, search_time, vaccine_type, top_x, top_y, bottom_x, bottom_y, only_left)
    close()


# ===================================== run ===================================== #
if __name__ == '__main__':
    main_function()
