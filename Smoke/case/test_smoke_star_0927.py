#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author   : chuanwen.peng
# @Time     : 2022/11/14 14:48
# @File     : test_smoke.py
# @Project  : glass_ui
"""
import datetime
import logging
import multiprocessing
import os
import random
import re
import string
import subprocess
import time

import allure
import pytest
import inspect

import uiautomator2

from Smoke.flow.smoke_flow import SmokeFlow
from Smoke import root_dir
from common.config_parser import ReadConfig
from common.base_page import BasePage

from common.utils import Util
from moviepy.editor import *

devices_dic = ReadConfig().get_package_name(root_dir.split('\\')[-1])
devices = [i for i in list(devices_dic.keys())]
data_list = []
for num in range(len(devices)):
    locals()['test_data' + str(num)] = [
        {
            "app_name": root_dir.split('\\')[-1],
            "devices": devices[num]
        }]
    data_list.append(locals()['test_data' + str(num)])


# logging.getLogger("urllib3").setLevel(logging.ERROR)
# logging.getLogger("filelock").setLevel(logging.ERROR)
# logging.getLogger("uiautomator2").setLevel(logging.ERROR)
# logging.getLogger("Util").setLevel(logging.ERROR)
# logging.getLogger("ReadConfig").setLevel(logging.ERROR)
# logging.getLogger("AdbTools").setLevel(logging.ERROR)
# logging.getLogger("logging").setLevel(logging.ERROR)


def set_setting_video(phone):
    before_time = time.time()
    my_inco = phone(resourceId="tv.danmaku.bili:id/tab_text", text="我的").exists
    while not my_inco:
        if time.time() - before_time >= 180:
            logging.error("-----------ui等待”我的“超时（double check）---------")
            pytest.assume(False)
        time.sleep(2)
    logging.info("-------------------点击我的------------------------")
    if not phone(resourceId="tv.danmaku.bili:id/tab_text", text="我的").exists:
        logging.error("-----------ui无”我的“元素（double check）---------")
        pytest.assume(False)
    phone(resourceId="tv.danmaku.bili:id/tab_text", text="我的").click()
    time.sleep(3)

    # before_time = time.time()
    # in_my = phone(resourceId="tv.danmaku.bili:id/title", text="青少年守护").exists
    # while not in_my:
    #     if time.time() - before_time >= 180:
    #         logging.error("-----------ui等待”青少年守护“超时（double check）---------")
    #         pytest.assume(False)
    #     time.sleep(2)
    logging.info("-------------------已进入我的------------------------")
    phone.swipe(0.5, 0.8, 0.5, 0.3)
    time.sleep(3)

    before_time = time.time()
    setting_inco = phone(resourceId="tv.danmaku.bili:id/title", text="设置").exists
    while not setting_inco:
        if time.time() - before_time >= 180:
            logging.error("-----------ui等待”设置“超时（double check）---------")
            pytest.assume(False)
        time.sleep(2)
    logging.info("-------------------点击设置------------------------")
    if not phone(resourceId="tv.danmaku.bili:id/title", text="设置").exists:
        logging.error("-----------ui无”我的“元素（double check）---------")
        pytest.assume(False)
    phone(resourceId="tv.danmaku.bili:id/title", text="设置").click()
    time.sleep(3)

    before_time = time.time()
    tuijian_inco = phone(text="首页推荐设置").exists
    while not tuijian_inco:
        if time.time() - before_time >= 180:
            logging.error("-----------ui等待”首页推荐设置“超时（double check）---------")
            pytest.assume(False)
        time.sleep(2)
    logging.info("-------------------点击首页推荐设置------------------------")
    if not phone(text="首页推荐设置").exists:
        logging.error("-----------ui无”首页推荐设置“元素（double check）---------")
        pytest.assume(False)
    phone(text="首页推荐设置").click()
    time.sleep(3)

    before_time = time.time()
    choose_inco = phone(resourceId="tv.danmaku.bili:id/rb_1").exists
    while not choose_inco:
        if time.time() - before_time >= 180:
            logging.error("-----------ui等待tv.danmaku.bili:id/rb_1元素超时（double check）---------")
            pytest.assume(False)
        time.sleep(2)
    logging.info("-------------------点击竖屏模式------------------------")
    if not phone(resourceId="tv.danmaku.bili:id/rb_1").exists:
        logging.error("-----------ui无”首页推荐设置“元素（double check）---------")
        pytest.assume(False)
    if not phone(resourceId="tv.danmaku.bili:id/rb_1").exists:
        logging.error("-----------ui无tv.danmaku.bili:id/rb_1元素（double check）---------")
        pytest.assume(False)
    phone(resourceId="tv.danmaku.bili:id/rb_1").click()
    time.sleep(3)
    phone.app_stop("tv.danmaku.bili")
    time.sleep(3)
    phone.app_start("tv.danmaku.bili", wait=True)
    time.sleep(4)


def get_screen_shot(device):
    file_path = device.screenshot(os.path.join(os.getcwd(), "report", device.serial + "_" + time.strftime('%Y%m%d%H%M',
                                                                                                          time.localtime(
                                                                                                              time.time())) + ".png"))
    logging.info("截图保存位置为：%s" % file_path)


def generate_random_str(randomlength=5):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    # 使用string库中的字母、数字和标点符号组成一个基础字符序列
    base_str = string.ascii_letters + string.digits + string.punctuation
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def play_music(play_time, path="person.wav"):
    logging.info("开始电脑播放音频")
    audio = AudioFileClip(os.path.join(os.getcwd(), "Smoke", path))
    audio.fx(afx.audio_loop, duration=play_time).preview()


def set_fanyi_src(phone, t_type="all"):
    start_app_reconnect(phone)
    time.sleep(3)
    phone.swipe_ext("up")
    time.sleep(4)
    if phone(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").exists:
        logging.info("点击翻译官")
        phone(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").click()
    else:
        logging.error("手机未找到翻译官图标")
        get_screen_shot(phone)
        pytest.assume(False)
    time.sleep(4)
    if phone(resourceId="com.upuphone.star.launcher:id/tv_title", text="同传翻译").exists:
        logging.info("手机已经进入翻译官首页，点击设置")
        time.sleep(3)
        phone(resourceId="com.upuphone.star.launcher:id/btnSetting").click()
        time.sleep(2)
    else:
        logging.error("手机未进入翻译官首页")
        get_screen_shot(phone)
        pytest.assume(False)
    if phone(resourceId="com.upuphone.star.launcher:id/tv_sub_other").exists:
        logging.info("已经进入翻译设置")
        time.sleep(2)
    else:
        logging.error("未进入翻译设置")
        get_screen_shot(phone)
        pytest.assume(False)
    # 检测当前字幕内容
    if phone(resourceId="com.upuphone.star.launcher:id/cv_sub_other_trans").child().child()[2].info.get("selected"):
        logging.info("当前字幕内容是只显示译文")
        if t_type == "all":
            logging.info("需求为修改为显示译文＋全文")
            phone(resourceId="com.upuphone.star.launcher:id/tv_card_desc", text="显示原文和译文").click()
            time.sleep(2)
            if phone(resourceId="com.upuphone.star.launcher:id/cv_sub_other_all").child().child()[3].info.get(
                    "selected"):
                logging.info("设置显示译文＋全文手机端成功")
            else:
                logging.error("设置显示译文＋全文手机端成功")
                get_screen_shot(phone)
                pytest.assume(False)
        else:
            logging.info("需求为只显示译文, 无需修改")
    else:
        logging.info("当前字幕内容是显示译文＋原文")
        if t_type != "all":
            logging.info("需求为修改为显示译文")
            phone(resourceId="com.upuphone.star.launcher:id/tv_card_desc", text="显示译文").click()
            time.sleep(2)
            if phone(resourceId="com.upuphone.star.launcher:id/cv_sub_other_trans").child().child()[2].info.get(
                    "selected"):
                logging.info("设置显示译文手机端成功")
            else:
                logging.error("设置显示译文手机端成功")
                get_screen_shot(phone)
                pytest.assume(False)
        else:
            logging.info("需求为显示译文＋原文, 无需修改")


def glass_to_app(glass, app, resource, flag=True):
    # 眼镜端从待机页面点击qq音乐
    os.system("adb -s %s shell input keyevent 4" % glass.serial)
    time.sleep(3)
    if not glass.info.get("screenOn"):
        # 点击power进入待机页面
        glass.press("power")
        time.sleep(1)
        while not glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            # 未进入到待机页面，再次单击power
            logging.info("未进入到待机页面，再次单击power")
            glass.press("power")
            time.sleep(1)
    logging.info("眼镜端进入到待机页面")
    # 点击返回进入到dock栏
    glass.keyevent("4")
    while not glass(resourceId="com.upuphone.star.launcher:id/iv_icon").exists:
        logging.info("未进入到dock页面，再次单击返回")
        if not glass.info.get("screenOn"):
            # 点击power进入待机页面
            glass.press("power")
            time.sleep(1)
        os.system("adb -s %s shell input keyevent 4" % devices[0])
        time.sleep(1)
    logging.info("眼镜端进入到dock页面")
    glass.keyevent("22")
    while not glass(resourceId="com.upuphone.star.launcher:id/tv_title", text=app).exists:
        logging.info("未出现%s上焦，再次单击右滑" % app)
        glass.keyevent("22")
        time.sleep(1)
    logging.info("已出现%s上焦，单击进入应用" % app)
    glass.keyevent("23")
    time.sleep(1)
    if flag:
        if glass(resourceId=resource).exists:
            logging.info("进入%s成功" % app)
    else:
        if not glass(resourceId=resource).exists:
            logging.info("进入%s成功" % app)


def start_app_reconnect(device):
    device.app_stop("com.upuphone.star.launcher")
    time.sleep(3)
    Util().device_unlock(device)
    # todo 手机启动超级app
    os.system(
        "adb -s %s shell am start -n com.upuphone.star.launcher/com.upuphone.xr.sapp.superconnect.ui.SplashActivity --ez force_login false" % device.serial)
    start_time = time.time()
    time.sleep(6)
    while time.time() - start_time <= 20:
        if device(resourceId="com.upuphone.star.launcher:id/card_device_info").exists and device(
                resourceId="com.upuphone.star.launcher:id/tv_device_battery").exists:
            logging.info("=======手机启动超级app成功==========")
            break
    else:
        logging.error("启动超级APP后互联回连成功失败")
        get_screen_shot(device)
        pytest.assume(False)


def connect_glass_wifi(phone):
    start_app_reconnect(phone)
    logging.info("超级app点击眼镜设置切换系统语言")
    phone(resourceId="com.upuphone.star.launcher:id/model_name", text="眼镜设置").click()
    time.sleep(2)
    if phone(resourceId="com.upuphone.star.launcher:id/card_title", text="系统语言").exists:
        logging.info("点击眼镜设置后进入成功")
        time.sleep(1)
    else:
        logging.error("点击眼镜设置后进入未成功")
        get_screen_shot(phone)
        pytest.assume(False)
    phone(text="网络配置").click()
    time.sleep(8)
    # 点击手机网络图标
    phone(resourceId="com.upuphone.star.launcher:id/wifi_phone_connect").click()
    time.sleep(10)
    if phone(resourceId="com.upuphone.star.launcher:id/wifi_connect_ed").exists:
        logging.info("手机点击配网显示成功")
    else:
        logging.error("手机点击配网后15s未显示配网成")
        get_screen_shot(phone)
        pytest.assume(False)
    # 检查眼镜端网络情况
    cmd = "adb -s %s shell dumpsys wifi | findstr Wi-Fi" % devices[0]
    connect_wifi = os.popen(cmd).read().strip()
    wifi_glass = re.findall(r'.*?SSID: (.*?), BSSID.*?', connect_wifi, re.S)[0].strip('"')
    if wifi_glass == "XJSD-GUEST":
        logging.info("=======眼镜端连接的wifi网络和手机一致==========")
        time.sleep(4)
    else:
        logging.error("=======眼镜端连接的wifi网络和手机不一致: %s==========" % wifi_glass)
        pytest.assume(False)


def get_bluetooth_devices():
    """检查电池状态"""
    cmd = "adb -s %s shell dumpsys bluetooth_manager" % devices[1]
    ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    res = [i for i in ret.stdout.readlines() if
           "name=AvrcpControllerStateMachine state=Connected" in i.decode("utf-8")]
    device_name = re.findall(r".*?\((.*)\)", res[0].decode(), re.S)
    return device_name


def get_current_value(glass, key):
    ret = [glass(resourceId="com.upuphone.star.launcher:id/sub_content")[i].get_text() for i in
           range(glass(resourceId="com.upuphone.star.launcher:id/sub_content").count) if
           key in glass(resourceId="com.upuphone.star.launcher:id/sub_content")[i].sibling()[1].get_text()]
    return ret[0]


@allure.epic("Smoke")
class TestSmoke:

    def set_address(self, phone, a_type):
        start_app_reconnect(phone)
        phone.swipe_ext("up", 0.8)
        time.sleep(1)
        logging.info("点击AR导航")
        phone(resourceId="com.upuphone.star.launcher:id/card_title", text="导航").click()
        time.sleep(1)
        if phone(resourceId="com.upuphone.star.launcher:id/name", text="回家").exists:
            logging.info("已设置家庭地址")
            phone.press("back")
            time.sleep(1)
        else:
            logging.info("未设置地址，点击添加家庭地址")
            phone(resourceId="com.upuphone.star.launcher:id/name", text=a_type).click()
            time.sleep(2)
            logging.info("输入天府广场")
            phone(resourceId="com.upuphone.star.launcher:id/keyWord").set_text("天府广场")
            time.sleep(1)
            logging.info("点击搜索结果第一个天府广场")
            phone(resourceId="com.upuphone.star.launcher:id/name", textContains="天府广场")[0].click()
            time.sleep(4)
            logging.info("检查是否添加成功家庭地址")
            if "天府广场" in phone(resourceId="com.upuphone.star.launcher:id/home_address").get_text():
                logging.info("%s添加成功，去导航" % a_type)
                phone.press("back")
                time.sleep(2)
            else:
                logging.error("%s添加失败" % a_type)
                get_screen_shot(phone)
                pytest.assume(False)

    def delete_address(self, phone, a_type):
        start_app_reconnect(phone)
        phone.swipe_ext("up", 0.8)
        time.sleep(1)
        logging.info("点击AR导航")
        phone(resourceId="com.upuphone.star.launcher:id/card_title", text="导航").click()
        time.sleep(1)
        if phone(resourceId="com.upuphone.star.launcher:id/name", text="回家").exists:
            logging.info("点击设置")
            phone(resourceId="com.upuphone.star.launcher:id/right_icon").click()
            time.sleep(2)
            logging.info("点击常用地址")
            phone(resourceId="com.upuphone.star.launcher:id/common_address").click()
            time.sleep(2)
            logging.info("点击删除地址")
            phone(resourceId=a_type).click()
            time.sleep(2)
            phone(resourceId="com.upuphone.star.launcher:id/menu_delete").click()
            time.sleep(2)
        else:
            logging.info("未设置家庭地址，无需删除")
            phone.press("back")
            time.sleep(1)

    @allure.feature("T211461")
    @allure.title("超级APP启动-同传翻译-翻译停止开始-手机退出（交替字幕显示）")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_phone_start_phone_stop_translate_with_src(self, driver, driver1):
        """超级APP启动-同传翻译-翻译停止开始-手机退出（交替字幕显示）"""
        # glass = driver
        # phone = driver1
        # t_type = "all"
        # logging.info("设置翻译字幕内容为显示原文+译文")
        # set_fanyi_src(phone, t_type=t_type)
        # start_app_reconnect(phone)
        # logging.info("--------------超级APP启动-同传翻译-翻译停止开始-手机退出（交替字幕显示）--------------")
        # time.sleep(3)
        # phone.swipe_ext("up")
        # time.sleep(4)
        # if phone(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").exists:
        #     logging.info("点击翻译官")
        #     phone(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").click()
        # else:
        #     logging.error("手机未找到翻译官图标")
        #     get_screen_shot(phone)
        #     pytest.assume(False)
        # time.sleep(4)
        # if phone(resourceId="com.upuphone.star.launcher:id/tv_title", text="同传翻译").exists:
        #     logging.info("手机已经进入翻译官首页，选择翻译类型")
        #     time.sleep(3)
        #     phone(resourceId="com.upuphone.star.launcher:id/tv_title", text="同传翻译").click()
        #     time.sleep(2)
        # else:
        #     logging.error("手机未进入翻译官首页")
        #     get_screen_shot(phone)
        #     pytest.assume(False)
        # if phone(resourceId="com.upuphone.star.launcher:id/cl_trans_btn").exists:
        #     logging.info("手机端点击翻译类型后进入到翻译设置页面，交换翻译语言")
        #     get_src = phone(resourceId="com.upuphone.star.launcher:id/tv_trans_src").get_text()
        #     get_dst = phone(resourceId="com.upuphone.star.launcher:id/tv_trans_dst").get_text()
        #     phone(resourceId="com.upuphone.star.launcher:id/lottie_trans_chang").click()
        #     time.sleep(2)
        #     get_src_after = phone(resourceId="com.upuphone.star.launcher:id/tv_trans_src").get_text()
        #     get_dst_after = phone(resourceId="com.upuphone.star.launcher:id/tv_trans_dst").get_text()
        #     if get_dst_after == get_src and get_src_after == get_dst:
        #         logging.info("点击交换翻译语言成功")
        #     else:
        #         logging.error("点击交换翻译语言失败")
        #         get_screen_shot(phone)
        #         pytest.assume(False)
        #     thread = multiprocessing.Process(target=play_music, args=(60,))
        #     # thread.setDaemon(True)
        #     thread.start()
        #     phone(resourceId="com.upuphone.star.launcher:id/tv_trans_btn", text="开始翻译").click()
        #     logging.info("点击开始翻译， 翻译8s")
        #     time.sleep(3)
        #     if phone(resourceId="com.upuphone.star.launcher:id/tv_trans_btn", text="停止翻译").exists and glass(
        #             resourceId="com.upuphone.star.launcher:id/tips", textContains="长按触控板停止").exists:
        #         logging.info("点击开始翻译后，眼镜端正常开始翻译")
        #         time.sleep(5)
        #         # 检测翻译字幕内容
        #         if t_type == "all":
        #             if glass(resourceId="com.upuphone.star.launcher:id/tv_dst").exists and glass(
        #                     resourceId="com.upuphone.star.launcher:id/tv_src").exists:
        #                 logging.info("眼镜翻译界面显示原文+译文")
        #             else:
        #                 logging.error("眼镜翻译界面字幕有误")
        #                 get_screen_shot(glass)
        #                 pytest.assume(False)
        #         else:
        #             if not glass(resourceId="com.upuphone.star.launcher:id/tv_src").exists:
        #                 logging.info("眼镜翻译界面只显示译文")
        #             else:
        #                 logging.error("眼镜翻译界面字幕有误")
        #                 get_screen_shot(glass)
        #                 pytest.assume(False)
        #         time.sleep(5)
        #     else:
        #         logging.error("点击开始翻译后，眼镜端未正常开始翻译")
        #         get_screen_shot(phone)
        #         pytest.assume(False)
        #     phone(resourceId="com.upuphone.star.launcher:id/tv_trans_btn", text="停止翻译").click()
        #     logging.info("翻译5s后手机端停止翻译")
        #     time.sleep(2)
        #     if phone(resourceId="com.upuphone.star.launcher:id/tv_trans_btn", text="开始翻译").exists and not glass(
        #             resourceId="com.upuphone.star.launcher:id/tips", textContains="长按触控板停止").exists:
        #         logging.info("手机停止翻译成功，眼镜端退出翻译页面")
        #     else:
        #         logging.error("手机停止翻译成功，眼镜端未退出翻译页面")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     logging.info("翻译首页长按tp回到待机页面")
        #     glass.keyevent("4")
        #     time.sleep(3)
        #     if glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #         logging.info("翻译首页长按tp回到待机页面成功")
        #         time.sleep(2)
        #     else:
        #         logging.error("翻译首页长按tp回到待机页面未成功")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        # else:
        #     logging.error("手机端点击翻译类型后未进入翻译设置页面")
        #     get_screen_shot(phone)
        #     pytest.assume(False)
        # thread.terminate()
        driver_list = [driver, driver1]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_start_translater_phone_end()

    @allure.feature("T211461")
    @allure.title("超级APP启动-语音转写-翻译停止开始-手机退出")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_phone_start_phone_stop_voice(self, driver, driver1):
        """超级APP启动-语音转写-翻译停止开始-手机退出"""
        # glass = driver
        # phone = driver1
        # start_app_reconnect(phone)
        # logging.info("-------------------超级APP启动-语音转写-翻译停止开始-手机退出------------------------")
        # time.sleep(3)
        # phone.swipe_ext("up")
        # time.sleep(4)
        # if phone(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").exists:
        #     logging.info("点击翻译官")
        #     phone(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").click()
        # else:
        #     logging.error("手机未找到翻译官图标")
        #     get_screen_shot(phone)
        #     pytest.assume(False)
        # time.sleep(4)
        # if phone(resourceId="com.upuphone.star.launcher:id/tv_title", text="语音转写").exists:
        #     logging.info("手机已经进入翻译官首页，选择翻译类型")
        #     time.sleep(3)
        #     phone(resourceId="com.upuphone.star.launcher:id/tv_title", text="语音转写").click()
        #     time.sleep(2)
        #     if phone(resourceId="com.upuphone.star.launcher:id/cl_transcribe_btn").exists:
        #         logging.info("手机端点击翻译类型后进入到语音转写页面")
        #         thread = multiprocessing.Process(target=play_music, args=(60,))
        #         # thread.setDaemon(True)
        #         thread.start()
        #         phone(resourceId="com.upuphone.star.launcher:id/cl_transcribe_btn").click()
        #         logging.info("点击开始转写， 转写8s")
        #         time.sleep(3)
        #         if phone(resourceId="com.upuphone.star.launcher:id/tv_transcribe_btn",
        #                  text="停止转写").exists and glass(
        #             resourceId="com.upuphone.star.launcher:id/tips", textContains="长按触控板停止").exists:
        #             logging.info("点击开始转写后，眼镜端正常开始转写，出现拾音条")
        #             time.sleep(5)
        #             if glass(resourceId="com.upuphone.star.launcher:id/rv_result").exists:
        #                 logging.info("眼镜端正常开始语音转写，出现字幕")
        #             else:
        #                 logging.error("眼镜端未正常开始语音转写")
        #                 get_screen_shot(glass)
        #                 pytest.assume(False)
        #         else:
        #             logging.error("点击开始转写后，眼镜端未正常开始转写")
        #             get_screen_shot(phone)
        #             pytest.assume(False)
        #         phone(resourceId="com.upuphone.star.launcher:id/tv_transcribe_btn", text="停止转写").click()
        #         logging.info("翻译5s后手机端停止转写")
        #         time.sleep(2)
        #         if phone(resourceId="com.upuphone.star.launcher:id/cl_transcribe_btn").exists and not glass(
        #                 resourceId="com.upuphone.star.launcher:id/tips", textContains="长按触控板停止").exists:
        #             logging.info("手机停止转写成功，眼镜端退出转写页面")
        #         else:
        #             logging.error("手机停止转写成功，眼镜端未退出转写页面")
        #             get_screen_shot(glass)
        #             pytest.assume(False)
        #         logging.info("翻译首页长按tp回到待机页面")
        #         glass.keyevent("4")
        #         time.sleep(3)
        #         if glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #             logging.info("翻译首页长按tp回到待机页面成功")
        #             time.sleep(2)
        #         else:
        #             logging.error("翻译首页长按tp回到待机页面未成功")
        #             get_screen_shot(glass)
        #             pytest.assume(False)
        #     else:
        #         logging.error("手机端点击翻译类型后未进入语音转写页面")
        #         get_screen_shot(phone)
        #         pytest.assume(False)
        # else:
        #     logging.error("手机未进入翻译官首页")
        #     get_screen_shot(phone)
        #     pytest.assume(False)
        # thread.terminate()
        driver_list = [driver, driver1]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_start_voice_phone_end()

    @allure.feature("T211461")
    @allure.title("dock启动-同传翻译-翻译停止开始-tp退出（交替字幕显示）")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_glass_start_glass_stop_translate(self, driver, driver1):
        """dock启动-同传翻译-翻译停止开始-tp退出（交替字幕显示）"""
        # glass = driver
        # phone = driver1
        # t_type = "trans"
        # logging.info("设置翻译字幕内容为只显示译文")
        # set_fanyi_src(phone, t_type=t_type)
        # start_app_reconnect(phone)
        # logging.info("------------------dock启动-同传翻译-翻译停止开始-tp退出（交替字幕显示）------------------------")
        # glass_to_app(glass, "翻译官", "com.upuphone.star.launcher:id/iv_icon", flag=False)
        # time.sleep(3)
        # thread = multiprocessing.Process(target=play_music, args=(60,))
        # # thread.setDaemon(True)
        # thread.start()
        # glass.keyevent("22")
        # time.sleep(1)
        # glass.keyevent("23")
        # time.sleep(5)
        # if glass(resourceId="com.upuphone.star.launcher:id/lottieWave").exists:
        #     logging.info("眼镜端点击同传翻译后进入同传翻译成功， 翻译5s")
        #     time.sleep(5)
        #     if t_type == "all":
        #         if glass(resourceId="com.upuphone.star.launcher:id/tv_dst").exists and glass(
        #                 resourceId="com.upuphone.star.launcher:id/tv_src").exists:
        #             logging.info("眼镜翻译界面显示原文+译文")
        #         else:
        #             logging.error("眼镜翻译界面字幕有误")
        #             get_screen_shot(glass)
        #             pytest.assume(False)
        #     else:
        #         if not glass(resourceId="com.upuphone.star.launcher:id/tv_src").exists:
        #             logging.info("眼镜翻译界面只显示译文")
        #         else:
        #             logging.error("眼镜翻译界面字幕有误")
        #             get_screen_shot(glass)
        #             pytest.assume(False)
        #     time.sleep(5)
        # else:
        #     logging.error("眼镜端点击同传翻译后进入同传翻译未成功")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("翻译中长按tp回到翻译官首页")
        # glass.keyevent("4")
        # time.sleep(3)
        # if not glass(resourceId="com.upuphone.star.launcher:id/lottieWave").exists:
        #     logging.info("翻译中长按tp回到翻译官首页成功")
        #     time.sleep(2)
        # else:
        #     logging.error("翻译中长按tp回到翻译官首页未成功")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("翻译首页长按tp回到待机页面")
        # glass.keyevent("4")
        # time.sleep(3)
        # if glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #     logging.info("翻译首页长按tp回到待机页面成功")
        #     time.sleep(2)
        # else:
        #     logging.error("翻译首页长按tp回到待机页面未成功")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # thread.terminate()
        driver_list = [driver, driver1]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_glass_start_voice_phone_end()

    @allure.feature("T211461")
    @allure.title("dock启动-语音转写-翻译停止开始-tp退出")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_glass_start_glass_stop_voice(self, driver, driver1):
        """dock启动-语音转写-翻译停止开始-tp退出"""
        # glass = driver
        # phone = driver1
        # start_app_reconnect(phone)
        # logging.info("-------------------dock启动-语音转写-翻译停止开始-tp退出------------------------")
        # glass_to_app(glass, "翻译官", "com.upuphone.star.launcher:id/iv_icon", flag=False)
        # time.sleep(3)
        # thread = multiprocessing.Process(target=play_music, args=(60,))
        # # thread.setDaemon(True)
        # thread.start()
        # glass.keyevent("22")
        # time.sleep(1)
        # glass.keyevent("22")
        # time.sleep(1)
        # glass.keyevent("23")
        # time.sleep(3)
        # if glass(resourceId="com.upuphone.star.launcher:id/lottieWave").exists:
        #     logging.info("眼镜端点击同传翻译后进入语音转写成功， 转写5s，出现拾音条")
        #     time.sleep(5)
        #     if glass(resourceId="com.upuphone.star.launcher:id/rv_result").exists:
        #         logging.info("眼镜端正常开始语音转写，出现字幕")
        #     else:
        #         logging.error("眼镜端未正常开始语音转写")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        # else:
        #     logging.error("眼镜端点击同传翻译后进入语音转写未成功")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("翻译中长按tp回到翻译官首页")
        # glass.keyevent("4")
        # time.sleep(3)
        # if not glass(resourceId="com.upuphone.star.launcher:id/lottieWave").exists:
        #     logging.info("翻译中长按tp回到翻译官首页成功")
        #     time.sleep(2)
        # else:
        #     logging.error("翻译中长按tp回到翻译官首页未成功")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("翻译首页长按tp回到待机页面")
        # glass.keyevent("4")
        # time.sleep(3)
        # if glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #     logging.info("翻译首页长按tp回到待机页面成功")
        #     time.sleep(2)
        # else:
        #     logging.error("翻译首页长按tp回到待机页面未成功")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # thread.terminate()
        driver_list = [driver, driver1]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_glass_start_voice_phone_end()

    @allure.title("dock发起抖音-TP前后滑动-tp小窗-tp进入应用-TP双击退出")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_douyin_glass_double_quit(self, driver, driver1):
        """dock发起抖音-TP前后滑动-tp小窗-tp进入应用-TP双击退出"""
        # glass = driver
        # phone = driver1
        # logging.info("dock发起抖音-TP前后滑动-tp小窗-tp进入应用-TP双击退出")
        # phone.app_stop('com.ss.android.ugc.aweme')
        # time.sleep(2)
        # glass_to_app(glass, "抖音", "com.upuphone.star.launcher:id/iv_icon", flag=False)
        # time.sleep(15)
        # status = 'com.ss.android.ugc.aweme' in phone.app_list_running()
        # if status and not glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #     line = datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
        #     logging.info("-----------抖音投屏成功，TP下滑, 发送时间：%s------------" % line)
        #     os.system("adb -s %s shell input keyevent 22" % glass.serial)
        #     time.sleep(4)
        #     line = datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
        #     logging.info("-----------抖音投屏成功，TP上滑, 发送时间：%s------------" % line)
        #     os.system("adb -s %s shell input keyevent 21" % glass.serial)
        #     time.sleep(4)
        #     logging.info("-----------抖音投屏成功，TP双击进入小窗------------")
        #     os.system("adb -s %s shell input keyevent 314" % glass.serial)
        #     time.sleep(3)
        #     if glass(resourceId="com.upuphone.star.launcher:id/picture_view_container").exists:
        #         logging.info("眼镜端双击进入待机小窗成功")
        #         time.sleep(3)
        #     else:
        #         logging.error("眼镜端双击进入待机小窗未成功")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     logging.info("单击TP从小窗进入应用")
        #     os.system("adb -s %s shell input keyevent 23" % glass.serial)
        #     time.sleep(4)
        #     if not glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #         logging.info("单击TP从小窗进入应用成功")
        #         time.sleep(3)
        #     else:
        #         logging.error("单击TP从小窗进入应用未成功")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     logging.info("tp长按退出抖音")
        #     os.system(
        #         "adb -s %s shell input keyevent 4&&adb -s %s shell input keyevent 4" % (glass.serial, glass.serial))
        #     # os.system("adb -s %s shell input keyevent 4" % glass.serial)
        #     time.sleep(4)
        #     if glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #         logging.info("TP退出抖音成功")
        #     else:
        #         logging.error("TP退出抖音失败")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        # else:
        #     logging.error("眼镜端未投屏抖音成功,眼镜端显示在待机页面")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # phone.app_stop('com.ss.android.ugc.aweme')
        # time.sleep(2)
        driver_list = [driver, driver1]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_glass_start_tiktok_end()

    @allure.title("dock发起快手-TP前后滑动-tp双击小窗-tp单击进入应用-TP长按退出")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_kuaishou_glass_double_quit(self, driver, driver1):
        """dock发起快手-TP前后滑动-tp双击小窗-tp单击进入应用-TP长按退出"""
        # glass = driver
        # phone = driver1
        # logging.info("dock发起快手-TP前后滑动-tp双击小窗-tp单击进入应用-TP长按退出")
        # phone.app_stop('com.smile.gifmaker')
        # time.sleep(2)
        # start_app_reconnect(phone)
        # glass_to_app(glass, "快手", "com.upuphone.star.launcher:id/iv_icon", flag=False)
        # time.sleep(15)
        # status = 'com.smile.gifmaker' in phone.app_list_running()
        # if status and not glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #     line = datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
        #     logging.info("-----------快手投屏成功，TP下滑, 发送时间：%s------------" % line)
        #     os.system("adb -s %s shell input keyevent 22" % glass.serial)
        #     time.sleep(4)
        #     line = datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
        #     logging.info("-----------快手投屏成功，TP上滑, 发送时间：%s------------" % line)
        #     os.system("adb -s %s shell input keyevent 21" % glass.serial)
        #     time.sleep(4)
        #     logging.info("-----------快手投屏成功，TP双击进入小窗------------")
        #     os.system("adb -s %s shell input keyevent 314" % glass.serial)
        #     time.sleep(3)
        #     if glass(resourceId="com.upuphone.star.launcher:id/picture_view_container").exists:
        #         logging.info("眼镜端双击进入待机小窗成功")
        #         time.sleep(3)
        #     else:
        #         logging.error("眼镜端双击进入待机小窗未成功")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     logging.info("单击TP从小窗进入应用")
        #     os.system("adb -s %s shell input keyevent 23" % glass.serial)
        #     time.sleep(4)
        #     if not glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #         logging.info("单击TP从小窗进入应用成功")
        #         time.sleep(3)
        #     else:
        #         logging.error("单击TP从小窗进入应用未成功")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     logging.info("tp长按退出快手")
        #     os.system(
        #         "adb -s %s shell input keyevent 4&&adb -s %s shell input keyevent 4" % (glass.serial, glass.serial))
        #     time.sleep(4)
        #     if glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #         logging.info("TP退出快手成功")
        #     else:
        #         logging.error("TP退出快手失败")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        # else:
        #     logging.error("眼镜端未投屏快手成功，眼镜端显示在待机页面")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # phone.app_stop('com.smile.gifmaker')
        # time.sleep(2)
        #
        driver_list = [driver, driver1]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_glass_start_kuaishou_end()

    @allure.feature("T192122")
    @allure.title("眼镜启动-常用地址-眼镜退出压测")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_glass_start_glass_quit(self, driver, driver1):
        """手机启动-设置常用地址-切换出行方式-手机退出压测"""
        # glass = driver
        # phone = driver1
        # # self.delete_address(phone, "com.upuphone.star.launcher:id/home_more")
        # self.set_address(phone, "添加家")
        # logging.info("-------------------眼镜启动-常用地址-眼镜退出------------------------")
        # glass_to_app(glass, "导航", "com.upuphone.star.launcher:id/address_bg_view")
        # time.sleep(3)
        # # # 呼出语音助理
        # # os.system("adb -s %s shell %s" % (glass.serial, config_r.order_dict.get("power_press")))
        # # time.sleep(15)
        # if glass(resourceId="com.upuphone.star.launcher:id/address_item", text="回家").exists:
        #     logging.info("眼镜端添加家庭地址成功")
        #     time.sleep(1)
        # else:
        #     logging.error("眼镜端添加家庭地址失败")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # glass.keyevent("22")
        # # glass(resourceId="com.upuphone.star.launcher:id/address_item", text="回家").click()
        # time.sleep(1)
        # glass.keyevent("23")
        # # glass(resourceId="com.upuphone.star.launcher:id/address_item", text="回家").click()
        # time.sleep(10)
        # if not glass(resourceId="com.upuphone.star.launcher:id/info_layout").exists:
        #     logging.error("开始导航后10s眼镜仍未有导航画面")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # else:
        #     logging.info("眼镜端导航成功")
        #     # 超级app端关闭导航路线
        #     time.sleep(8)
        #     logging.info("双击tp进入小窗模式")
        #     glass.keyevent("314")
        #     time.sleep(3)
        #     if glass(resourceId="com.upuphone.star.launcher:id/navi_content_layout").exists:
        #         logging.info("TP双击进入小窗成功")
        #     else:
        #         logging.error("TP双击进入小窗成功")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     logging.info("单击TP从小窗进入应用")
        #     os.system("adb -s %s shell input keyevent 23" % glass.serial)
        #     time.sleep(4)
        #     if not glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #         logging.info("单击TP从小窗进入应用成功")
        #         time.sleep(3)
        #     else:
        #         logging.error("单击TP从小窗进入应用未成功")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     logging.info("眼镜端长按退出导航")
        #     os.system("adb -s %s shell input keyevent 4" % glass.serial)
        #     time.sleep(4)
        #     if glass(resourceId="com.upuphone.star.launcher:id/info_layout").exists:
        #         logging.error("手机退出导航后眼镜仍未有导航画面")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     else:
        #         logging.info("眼镜退出导航成功！")
        driver_list = [driver, driver1]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_glass_start_navi_end()

    @allure.feature("T192122")
    @allure.title("手机启动-输入地址-切换出行方式-眼镜退出")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_input_address_phone_quit(self, driver, driver1):
        """手机启动-输入地址-切换出行方式-眼镜退出"""
        # glass = driver
        # phone = driver1
        # Util().device_unlock(phone)
        # logging.info("-------------------手机启动-输入地址-切换出行方式-眼镜退出------------------------")
        # start_app_reconnect(phone)
        # phone.swipe_ext("up", 0.8)
        # time.sleep(0.8)
        # logging.info("点击发起导航")
        # phone(resourceId="com.upuphone.star.launcher:id/card_title", text="导航").click()
        # time.sleep(1)
        # phone(resourceId="com.upuphone.star.launcher:id/bottom_edit").click()
        # time.sleep(1)
        # logging.info("输入天府广场")
        # phone(resourceId="com.upuphone.star.launcher:id/keyWord").set_text("天府广场")
        # time.sleep(3)
        # logging.info("点击搜索结果第一个天府广场")
        # phone(resourceId="com.upuphone.star.launcher:id/name", textContains="天府广场")[0].click()
        # time.sleep(4)
        # logging.info("点击路线")
        # phone(resourceId="com.upuphone.star.launcher:id/navi_route").click()
        # time.sleep(4)
        # # logging.info("获取默认驾车导航第一个路线的时间")
        # # drive_time = phone(resourceId="com.upuphone.star.launcher:id/time")[0].get_text()
        # # time.sleep(1)
        # # logging.info("点击骑行")
        # # bike_time = phone(resourceId="com.upuphone.star.launcher:id/navi_bike").click()
        # # if bike_time != drive_time:
        # #     logging.info("切换导航方式成功")
        # # else:
        # #     logging.error("切换导航方式失败")
        # #     result_dic["failed_count"] += 1
        # #     pytest.assume(False)
        # logging.info("点击开始导航")
        # phone(resourceId="com.upuphone.star.launcher:id/navi").click()
        # time.sleep(10)
        # if not glass(resourceId="com.upuphone.star.launcher:id/info_layout").exists:
        #     logging.error("手机开始导航后10s眼镜仍未有导航画面")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # else:
        #     logging.info("眼镜端导航成功")
        #     time.sleep(8)
        #     logging.info("双击tp进入小窗模式")
        #     glass.keyevent("314")
        #     time.sleep(3)
        #     if glass(resourceId="com.upuphone.star.launcher:id/navi_content_layout").exists:
        #         logging.info("TP双击进入小窗成功")
        #     else:
        #         logging.error("TP双击进入小窗成功")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     logging.info("单击TP从小窗进入应用")
        #     os.system("adb -s %s shell input keyevent 23" % glass.serial)
        #     time.sleep(4)
        #     if not glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #         logging.info("单击TP从小窗进入应用成功")
        #         time.sleep(3)
        #     else:
        #         logging.error("单击TP从小窗进入应用未成功")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        #     # 超级app端关闭导航路线
        #     time.sleep(5)
        #     logging.info("眼镜端长按退出导航")
        #     os.system("adb -s %s shell input keyevent 4" % glass.serial)
        #     time.sleep(4)
        #     if glass(resourceId="com.upuphone.star.launcher:id/info_layout").exists:
        #         logging.error("手机退出导航后眼镜仍未有导航画面")
        #         get_screen_shot(glass)
        #         assert False
        #     else:
        #         logging.info("眼镜退出导航成功！")
        driver_list = [driver, driver1]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_phone_start_navi_end()

    @allure.feature("T192047")
    @allure.title("眼镜端设置调节音量")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    def test_glass_setting_vol(self, driver):
        """眼镜端设置调节音量"""
        # glass = driver
        # logging.info("-------------------眼镜端设置调节音量------------------------")
        # before_vol = int(os.popen(
        #     "adb -s %s shell settings get system volume_music_speaker" % glass.serial).readlines()[
        #                      0].strip())
        # glass_to_app(glass, "设置", "com.upuphone.star.launcher:id/setting_page_title")
        # time.sleep(3)
        # glass.keyevent("23")
        # time.sleep(1.5)
        # if glass(resourceId="com.upuphone.star.launcher:id/volume_view").exists:
        #     logging.info("眼镜端设置页面点击音量出现音量条，前滑上焦")
        # else:
        #     logging.error("眼镜端设置页面点击音量未出现音量条")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("调节音量前音量为：%s" % before_vol)
        # logging.info("TP前滑调节音量")
        # # os.system("adb -s %s shell input keyevent 22" % glass.serial)
        # glass.keyevent("21")
        # time.sleep(0.5)
        # glass.keyevent("22")
        # # time.sleep(3)
        # after_vol = int(os.popen(
        #     "adb -s %s shell  settings get system volume_music_speaker" % glass.serial).readlines()[
        #                     0].strip())
        # logging.info("TP前滑调节音量后音量为：%s" % after_vol)
        # if after_vol > before_vol:
        #     logging.info("TP前滑后音量调整成功！调节前：%s，调节后：%s" % (before_vol, after_vol))
        # else:
        #     logging.error("TP前滑后音量调整失败！调节前：%s，调节后：%s" % (before_vol, after_vol))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("TP长按回退到设置主页面")
        # glass.keyevent("4")
        # time.sleep(2)
        # if glass(resourceId="com.upuphone.star.launcher:id/setting_page_title", text="设置").exists:
        #     logging.info("TP长按回退到设置主页面成功")
        # else:
        #     logging.error("TP长按回退到设置主页面失败")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # time.sleep(1)
        # # TODO 还有对比调节后得值做百分比比较
        # if int(get_current_value(glass, "音量").split("%")[0]) == int(float(
        #         str(after_vol / 15).split(".")[0] + "." + str(after_vol / 15).split(".")[1][:2]) * 100):
        #     logging.info("音量显示百分比成功，百分比为：%s" % get_current_value(glass, "音量"))
        # else:
        #     logging.info("音量显示百分比失败，设置显示为：%s，调节到：%s" % (get_current_value(glass, "音量"), int(float(
        #         str(after_vol / 15).split(".")[0] + "." + str(after_vol / 15).split(".")[1][:2]) * 100)))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # time.sleep(1)
        # glass.keyevent("23")
        # time.sleep(2)
        # logging.info("TP后滑调节音量")
        # glass.keyevent("22")
        # time.sleep(0.5)
        # glass.keyevent("21")
        # # time.sleep(3)
        # after_vol_1 = int(os.popen(
        #     "adb -s %s shell settings get system volume_music_speaker" % glass.serial).readlines()[
        #                       0].strip())
        # logging.info("TP后滑调节音量后音量为：%s" % after_vol_1)
        # if after_vol_1 < after_vol:
        #     logging.info("TP后滑后音量调整成功！调节前：%s，调节后：%s" % (after_vol, after_vol_1))
        # else:
        #     logging.error("TP后滑后音量调整失败！调节前：%s，调节后：%s" % (after_vol, after_vol_1))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("TP长按回退到设置主页面")
        # glass.keyevent("4")
        # time.sleep(2)
        # if glass(resourceId="com.upuphone.star.launcher:id/setting_page_title", text="设置").exists:
        #     logging.info("TP长按回退到设置主页面成功")
        # else:
        #     logging.error("TP长按回退到设置主页面失败")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # time.sleep(1)
        # # TODO 还有对比调节后得值做百分比比较
        # if int(get_current_value(glass, "音量").split("%")[0]) == int(
        #         float(str(after_vol_1 / 15).split(".")[0] + "." + str(after_vol_1 / 15).split(".")[1][:2]) * 100):
        #     logging.info("音量显示百分比成功，百分比为：%s" % get_current_value(glass, "音量"))
        # else:
        #     logging.info(
        #         "音量显示百分比失败，设置显示为：%s，调节到：%s" % (get_current_value(glass, "音量"), int(float(
        #             str(after_vol_1 / 15).split(".")[0] + "." + str(after_vol_1 / 15).split(".")[1][:2]) * 100)))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # time.sleep(1)
        # logging.info("TP长按回退到待机页面")
        # glass.keyevent("4")
        # time.sleep(2)
        # if glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #     logging.info("TP长按后，眼镜回到待机页面")
        # else:
        #     logging.error("TP长按后，眼镜未回到待机页面")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        driver_list = [driver]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_glass_set_vol()

    @allure.feature("T192047")
    @allure.title("眼镜端设置调节亮度")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    def test_glass_setting_bri(self, driver):
        """眼镜端设置调节亮度"""
        # glass = driver
        # bri_dict = {"10": 0, "25": 10, "51": 20, "64": 30, "102": 40, "128": 50, "153": 60, "179": 70, "204": 80,
        #             "230": 90, "255": 100}
        # logging.info("-------------------眼镜端设置调节亮度------------------------")
        # before_bri = int(os.popen(
        #     "adb -s %s shell settings get system screen_brightness" % glass.serial).readlines()[
        #                      0].strip())
        # glass_to_app(glass, "设置", "com.upuphone.star.launcher:id/setting_page_title")
        # time.sleep(2)
        # glass.keyevent("22")
        # time.sleep(0.5)
        # glass.keyevent("22")
        # # glass(resourceId="com.upuphone.star.launcher:id/name", text="亮度").click()
        # time.sleep(1)
        # glass.keyevent("23")
        # time.sleep(2)
        # if glass(resourceId="com.upuphone.star.launcher:id/brightness_view").exists:
        #     logging.info("眼镜端设置页面点击亮度出现亮度条")
        # else:
        #     logging.error("眼镜端设置页面点击亮度未出现亮度条")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("调节亮度前亮度为：%s" % before_bri)
        # logging.info("TP前滑调节亮度")
        # os.system("adb -s %s shell input keyevent 22" % glass.serial)
        # time.sleep(3)
        # after_bri = int(os.popen(
        #     "adb -s %s shell settings get system screen_brightness" % glass.serial).readlines()[
        #                     0].strip())
        # logging.info("TP前滑调节亮度后亮度为：%s" % after_bri)
        # if after_bri > before_bri:
        #     logging.info("TP前滑后亮度调整成功！调节前：%s，调节后：%s" % (before_bri, after_bri))
        # else:
        #     logging.error("TP前滑后亮度调整失败！调节前：%s，调节后：%s" % (before_bri, after_bri))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("TP长按回退到设置主页面")
        # glass.keyevent("4")
        # time.sleep(2)
        # if glass(resourceId="com.upuphone.star.launcher:id/setting_page_title", text="设置").exists:
        #     logging.info("TP长按回退到设置主页面成功")
        # else:
        #     logging.error("TP长按回退到设置主页面失败")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # time.sleep(1)
        # # TODO 还有对比调节后得值做百分比比较
        # if int(get_current_value(glass, "亮度").split("%")[0]) == bri_dict[str(after_bri)]:
        #     logging.info("亮度显示百分比成功，百分比为：%s" % get_current_value(glass, "亮度"))
        # else:
        #     logging.info("亮度显示百分比失败，百分比为：%s" % get_current_value(glass, "亮度"))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # time.sleep(1)
        # glass.keyevent("23")
        # time.sleep(2)
        # logging.info("TP后滑调节亮度")
        # glass.keyevent("21")
        # time.sleep(3)
        # after_bri_1 = int(os.popen(
        #     "adb -s %s shell settings get system screen_brightness" % glass.serial).readlines()[
        #                       0].strip())
        # logging.info("TP后滑调节亮度后亮度为：%s" % after_bri_1)
        # if after_bri_1 < after_bri:
        #     logging.info("TP后滑后亮度调整成功！调节前：%s，调节后：%s" % (after_bri, after_bri_1))
        # else:
        #     logging.error("TP后滑后亮度调整失败！调节前：%s，调节后：%s" % (after_bri, after_bri_1))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("TP长按回退到设置主页面")
        # glass.keyevent("4")
        # time.sleep(2)
        # if glass(resourceId="com.upuphone.star.launcher:id/setting_page_title", text="设置").exists:
        #     logging.info("TP长按回退到设置主页面成功")
        # else:
        #     logging.error("TP长按回退到设置主页面失败")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # time.sleep(1)
        # # TODO 还有对比调节后得值做百分比比较
        # if int(get_current_value(glass, "亮度").split("%")[0]) == bri_dict[str(after_bri_1)]:
        #     logging.info("亮度显示百分比成功，百分比为：%s" % get_current_value(glass, "亮度"))
        # else:
        #     logging.info("亮度显示百分比失败，百分比为：%s" % get_current_value(glass, "亮度"))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # time.sleep(1)
        # logging.info("TP长按回退到待机页面")
        # glass.keyevent("4")
        # time.sleep(2)
        # if glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
        #     logging.info("TP长按后，眼镜回到待机页面")
        # else:
        #     logging.error("TP长按后，眼镜未回到待机页面")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        driver_list = [driver]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_glass_set_bri()

    @allure.feature("T192047")
    @allure.title("呼出关机页面，并取消")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    def test_glass_power_page_cancel(self, driver):
        """呼出关机页面，并取消"""
        # glass = driver
        # logging.info("-------------------呼出关机页面，并取消------------------------")
        # power_press = "sendevent /dev/input/event0 1 116 1;sendevent /dev/input/event0 0 0 0;sleep 5;sendevent /dev/input/event0 1 116 0;sendevent /dev/input/event0 0 0 0"
        # os.system("adb -s %s shell %s" % (glass.serial, power_press))
        # time.sleep(1)
        # if glass(resourceId="com.upuphone.star.launcher:id/system_shutdown_btn").exists:
        #     logging.info("长按5s电源键呼出关机页面成功")
        # else:
        #     logging.error("长按5s电源键呼出关机页面失败")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # time.sleep(2)
        # logging.info("TP长按退出关机页面")
        # glass.keyevent("4")
        # time.sleep(2)
        # if not glass(resourceId="com.upuphone.star.launcher:id/system_shutdown_btn").exists:
        #     logging.info("TP长按后，TP长按退出关机页面成功")
        # else:
        #     logging.error("TP长按后，TP长按退出关机页面失败")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        driver_list = [driver]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_glass_power_page()

    @allure.feature("T211461")
    @allure.title("眼镜dock启动-TP单击播放-TP前后滑动-TP单击暂停退出")
    @pytest.mark.M
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_glass_start_music_click_quit(self, driver, driver1):
        """眼镜dock启动-TP单击播放-TP前后滑动-TP单击暂停退出"""
        # glass = driver
        # phone = driver1
        # start_app_reconnect(phone)
        # logging.info("-------------------眼镜dock启动-TP单击播放-TP前后滑动-TP单击暂停退出------------------------")
        # glass_to_app(glass, "QQ音乐", "com.upuphone.star.launcher:id/cl_song_info_layout")
        # time.sleep(5)
        # if not glass(resourceId="com.upuphone.star.launcher:id/ll_progress_value").exists:
        #     logging.info("眼镜端未同步歌曲信息，先去授权手机")
        #     phone.app_start("com.tencent.qqmusic", wait=True)
        #     time.sleep(5)
        #     start_time = time.time()
        #     while not phone(text="猜你喜欢").exists or time.time() - start_time > 15:
        #         logging.info("手机打开qq音乐后未进入qq音乐界面")
        #         time.sleep(2)
        #         phone.press("back")
        #     phone(text="猜你喜欢").click()
        #     time.sleep(3)
        # else:
        #     logging.info("眼镜端同步显示歌曲进度条")
        # # 开始写播放控制
        # # 单击上焦，默认在播放/暂停按钮
        # glass.keyevent("22")
        # # time.sleep(0.5)
        # # if glass(resourceId="com.upuphone.star.launcher:id/iv_play").info.get("selected"):
        # #     # 已上焦到播放/暂停按钮，点击播放
        # glass.keyevent("23")
        # time.sleep(3)
        # if glass(resourceId="com.upuphone.star.launcher:id/iv_pause").exists:
        #     logging.info("单击TP之后开始播放歌曲， 播放8s")
        #     time.sleep(8)
        # else:
        #     logging.error("播放按钮上焦后单击TP未播放音乐")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # # 切换歌曲
        # get_current_music = glass(resourceId="com.upuphone.star.launcher:id/tv_artist").get_text()
        # logging.info("当前播放歌曲为：%s" % get_current_music)
        # glass.keyevent("22")
        # time.sleep(0.5)
        # glass.keyevent("22")
        # time.sleep(0.5)
        # glass.keyevent("23")
        # time.sleep(1)
        # logging.info("切换下一首，播放音乐8s")
        # time.sleep(8)
        # get_current_music_before = glass(resourceId="com.upuphone.star.launcher:id/tv_artist").get_text()
        # if get_current_music_before != get_current_music:
        #     logging.info("眼镜端切换下一首成功；切换后：%s，切换前：%s" % (get_current_music_before, get_current_music))
        # else:
        #     logging.error("眼镜端tp切换下一首失败；切换后：%s， 切换前: %s" % (get_current_music_before, get_current_music))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # logging.info("切换上一首，播放音乐8s")
        # time.sleep(8)
        # glass.keyevent("22")
        # time.sleep(0.5)
        # glass.keyevent("21")
        # time.sleep(1)
        # glass.keyevent("23")
        # time.sleep(1)
        # get_current_music_after = glass(resourceId="com.upuphone.star.launcher:id/tv_artist").get_text()
        # if get_current_music_after != get_current_music_before and get_current_music_after == get_current_music:
        #     logging.info("眼镜端tp切换上一首成功；切换后：%s， 切换前: %s" % (get_current_music_after, get_current_music_before))
        # else:
        #     logging.error("眼镜端tp切换上一首失败；切换后：%s， 切换前: %s" % (get_current_music_after, get_current_music_before))
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        # # TODO 剩余退出音乐操作，先写单击暂停
        # glass.keyevent("23")
        # time.sleep(1)
        # if glass(resourceId="com.upuphone.star.launcher:id/iv_pause").info.get("selected"):
        #     # 已上焦到播放/暂停按钮，点击播放
        #     glass.keyevent("23")
        #     time.sleep(1)
        #     if glass(resourceId="com.upuphone.star.launcher:id/iv_play").exists:
        #         logging.info("单击TP之后暂停成功")
        #     else:
        #         logging.error("单击TP之后暂停失败")
        #         get_screen_shot(glass)
        #         pytest.assume(False)
        # # else:
        # #     logging.error("QQ音乐页面单击TP未上焦到播放/暂停按钮")
        # #     get_screen_shot(glass)
        # #     pytest.assume(False)
        # logging.info("TP长按tp回到待机页面，显示播控中心")
        # glass.keyevent("4")
        # time.sleep(3)
        # if glass(resourceId="com.upuphone.star.launcher:id/song_artist").exists:
        #     logging.info("TP长按tp回到待机页面成功显示播控中心")
        #     time.sleep(2)
        # else:
        #     logging.error("TP长按tp回到待机页面未成功显示播控中心")
        #     get_screen_shot(glass)
        #     pytest.assume(False)
        driver_list = [driver]
        smoke_flow = SmokeFlow(driver_list)
        smoke_flow.smoke_glass_qq_music()

    @allure.title("手机发起投屏压测，眼镜TP双击小窗-眼镜tp单击进入全屏-眼镜tp长按退出投屏压测")
    @pytest.mark.S
    @pytest.mark.parametrize('driver', data_list[0], indirect=True)
    @pytest.mark.parametrize('driver1', data_list[1], indirect=True)
    def test_dlna_glass(self, driver, driver1):
        """手机发起投屏压测，眼镜TP双击小窗-眼镜tp单击进入全屏-眼镜tp长按退出投屏压测"""
        glass = driver
        phone = driver1
        phone.watcher.when("登录注册解锁更多精彩内容").press("back")
        phone.watcher.when("开启推送通知，及时获取消息提醒").press("back")
        phone.watcher.start()
        Util().device_unlock(phone)
        start_app_reconnect(phone)
        if not Util().get_network_state(glass.serial):
            connect_glass_wifi(phone)
        dlna_name = get_bluetooth_devices()
        init_time = "2023-09-20 10:11:12"
        logging.info("清除哔哩哔哩缓存")
        phone.app_clear("tv.danmaku.bili")
        time.sleep(3)
        glass.keyevent("4")
        phone.app_start("tv.danmaku.bili", wait=True)
        time.sleep(8)
        logging.info("=======手机启动bilibili成功==========")
        logging.info("-------------------手机发起投屏压测，眼镜TP双击小窗-眼镜tp单击进入全屏-眼镜tp长按退出投屏压测------------------------")
        logging.info("-------------------点击视频------------------------")
        if "竖屏" not in phone(resourceId="tv.danmaku.bili:id/desc")[0].get_text():
            phone(resourceId="tv.danmaku.bili:id/title_layout")[0].click()
        else:
            phone(resourceId="tv.danmaku.bili:id/title_layout")[1].click()
        time.sleep(3)
        phone.click(0.905, 0.204)
        time.sleep(0.5)
        if phone(resourceId="tv.danmaku.bili:id/projection_screen_icon").exists:
            logging.info("单击视频出现投屏按钮，点击投屏")
            while "com.github.uiautomator" in phone.current_app().get("package"):
                phone.press("back")
            phone(resourceId="tv.danmaku.bili:id/projection_screen_icon").click()
            time.sleep(8)
        else:
            logging.error("单击视频未出现投屏按钮")
            get_screen_shot(phone)
            pytest.assume(False)
        if phone(text=dlna_name[0]).exists:
            logging.info("-------------------找到互联设备点击投屏------------------------")
            phone(text=dlna_name[0]).click()
            time.sleep(0.5)
        else:
            logging.error("--------------未检测到互联的蓝牙设备，请检测互联状态及star设备是否联网---------------")
            pytest.assume(False)
        if phone(resourceId="tv.danmaku.bili:id/device_switch_text_view", text="换设备").exists and glass(
                resourceId="com.upuphone.star.launcher:id/video_seekBar").exists:
            logging.info("点击投屏后，手机端出现投屏操作按钮，眼镜端显示进度条，投屏10s")
            time.sleep(10)
        else:
            logging.error("点击投屏后，手机端未出现投屏操作按钮")
            get_screen_shot(phone)
            get_screen_shot(glass)
            pytest.assume(False)
        before_time = phone(textContains="/").get_text()
        before_time_tmp_0 = init_time.replace("11", before_time.split("/")[0].split(':')[0])
        before_time_tmp_1 = before_time_tmp_0.replace("12", before_time.split("/")[0].split(':')[1])
        before_time_end = datetime.datetime.strptime(before_time_tmp_1, "%Y-%m-%d %H:%M:%S")
        logging.info("眼镜TP前滑快进")
        glass.keyevent("22")
        time.sleep(0.5)
        if glass(resourceId="com.upuphone.star.launcher:id/video_seekBar").exists:
            logging.info("TP前滑眼镜端出现进度条")
        else:
            logging.error("TP前滑眼镜端未出现进度条")
            get_screen_shot(glass)
            pytest.assume(False)
        time.sleep(2)
        after_time = phone(textContains="/").get_text()
        after_time_tmp_0 = init_time.replace("11", after_time.split("/")[0].split(':')[0])
        after_time_tmp_1 = after_time_tmp_0.replace("12", after_time.split("/")[0].split(':')[1])
        after_time_end = datetime.datetime.strptime(after_time_tmp_1, "%Y-%m-%d %H:%M:%S")
        if (after_time_end - before_time_end).seconds >= 8:
            logging.info("TP前滑快进成功")
        else:
            logging.error("TP前滑快进失败")
            get_screen_shot(phone)
            get_screen_shot(glass)
            pytest.assume(False)
        time.sleep(2)
        logging.info("TP后滑快退")
        before_time = phone(textContains="/").get_text()
        before_time_tmp_0 = init_time.replace("11", before_time.split("/")[0].split(':')[0])
        before_time_tmp_1 = before_time_tmp_0.replace("12", before_time.split("/")[0].split(':')[1])
        before_time_end = datetime.datetime.strptime(before_time_tmp_1, "%Y-%m-%d %H:%M:%S")
        glass.keyevent("21")
        time.sleep(0.5)
        if glass(resourceId="com.upuphone.star.launcher:id/video_seekBar").exists:
            logging.info("TP前滑眼镜端出现进度条")
        else:
            logging.error("TP前滑眼镜端未出现进度条")
            get_screen_shot(glass)
            pytest.assume(False)
        time.sleep(2)
        after_time = phone(textContains="/").get_text()
        after_time_tmp_0 = init_time.replace("11", after_time.split("/")[0].split(':')[0])
        after_time_tmp_1 = after_time_tmp_0.replace("12", after_time.split("/")[0].split(':')[1])
        after_time_end = datetime.datetime.strptime(after_time_tmp_1, "%Y-%m-%d %H:%M:%S")
        if (before_time_end - after_time_end).seconds >= 8:
            logging.info("TP前滑快退成功")
        else:
            logging.error("TP前滑快退失败")
            get_screen_shot(phone)
            get_screen_shot(glass)
            pytest.assume(False)
        time.sleep(2)
        before_time = phone(textContains="/").get_text()
        before_time_tmp_0 = init_time.replace("11", before_time.split("/")[0].split(':')[0])
        before_time_tmp_1 = before_time_tmp_0.replace("12", before_time.split("/")[0].split(':')[1])
        before_time_end = datetime.datetime.strptime(before_time_tmp_1, "%Y-%m-%d %H:%M:%S")
        logging.info("眼镜TP前滑快进")
        glass.keyevent("22")
        time.sleep(0.5)
        if glass(resourceId="com.upuphone.star.launcher:id/video_seekBar").exists:
            logging.info("TP前滑眼镜端出现进度条")
        else:
            logging.error("TP前滑眼镜端未出现进度条")
            get_screen_shot(glass)
            pytest.assume(False)
        time.sleep(2)
        after_time = phone(textContains="/").get_text()
        after_time_tmp_0 = init_time.replace("11", after_time.split("/")[0].split(':')[0])
        after_time_tmp_1 = after_time_tmp_0.replace("12", after_time.split("/")[0].split(':')[1])
        after_time_end = datetime.datetime.strptime(after_time_tmp_1, "%Y-%m-%d %H:%M:%S")
        if (after_time_end - before_time_end).seconds >= 8:
            logging.info("TP前滑快进成功")
        else:
            logging.error("TP前滑快进失败")
            get_screen_shot(phone)
            get_screen_shot(glass)
            pytest.assume(False)
        time.sleep(2)
        logging.info("TP后滑快退")
        before_time = phone(textContains="/").get_text()
        before_time_tmp_0 = init_time.replace("11", before_time.split("/")[0].split(':')[0])
        before_time_tmp_1 = before_time_tmp_0.replace("12", before_time.split("/")[0].split(':')[1])
        before_time_end = datetime.datetime.strptime(before_time_tmp_1, "%Y-%m-%d %H:%M:%S")
        glass.keyevent("21")
        time.sleep(0.5)
        if glass(resourceId="com.upuphone.star.launcher:id/video_seekBar").exists:
            logging.info("TP前滑眼镜端出现进度条")
        else:
            logging.error("TP前滑眼镜端未出现进度条")
            get_screen_shot(glass)
            pytest.assume(False)
        time.sleep(2)
        after_time = phone(textContains="/").get_text()
        after_time_tmp_0 = init_time.replace("11", after_time.split("/")[0].split(':')[0])
        after_time_tmp_1 = after_time_tmp_0.replace("12", after_time.split("/")[0].split(':')[1])
        after_time_end = datetime.datetime.strptime(after_time_tmp_1, "%Y-%m-%d %H:%M:%S")
        if (before_time_end - after_time_end).seconds >= 8:
            logging.info("TP前滑快退成功")
        else:
            logging.error("TP前滑快退失败")
            get_screen_shot(phone)
            get_screen_shot(glass)
            pytest.assume(False)
        time.sleep(2)
        # 眼镜双击小窗
        logging.info("-----------投屏成功，TP双击进入小窗------------")
        os.system("adb -s %s shell input keyevent 314" % glass.serial)
        time.sleep(3)
        if glass(resourceId="com.upuphone.star.launcher:id/picture_view_container").exists:
            logging.info("眼镜端双击进入待机小窗成功")
            time.sleep(3)
        else:
            logging.error("眼镜端双击进入待机小窗未成功")
            get_screen_shot(glass)
            pytest.assume(False)
        logging.info("单击TP从小窗进入应用")
        os.system("adb -s %s shell input keyevent 23" % glass.serial)
        time.sleep(4)
        if not glass(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            logging.info("单击TP从小窗进入应用成功")
            time.sleep(3)
        else:
            logging.error("单击TP从小窗进入应用未成功")
            get_screen_shot(glass)
            pytest.assume(False)
        logging.info("tp长按退出")
        os.system("adb -s %s shell input keyevent 4" % glass.serial)
        time.sleep(4)
        if glass(resourceId="com.upuphone.star.launcher:id/time_view").exists and phone(text="00:00/00:00").exists:
            logging.info("TP退出成功")
        else:
            logging.error("TP退出失败")
            get_screen_shot(glass)
            get_screen_shot(phone)
            pytest.assume(False)
