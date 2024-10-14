# creater: chuanwen.peng
# time: 2022/7/12 12:30
import datetime
import logging
import multiprocessing
import os
import re
import subprocess
import time
import allure
import pytest

from common.base_page import BasePage
from common.utils import Util
from Smoke.element.element_router import ElementRouter
from Smoke import root_dir
from moviepy.editor import *


def get_screen_shot(device):
    if not os.path.exists(os.path.join(os.getcwd(), "report")):
        os.mkdir(os.path.join(os.getcwd(), "report"))
    file_path = device.screenshot(os.path.join(os.getcwd(), "report", device.serial + "_" + time.strftime('%Y%m%d%H%M',
                                                                                                          time.localtime(
                                                                                                              time.time())) + ".png"))
    logging.info("截图保存位置为：%s" % file_path)


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
    os.system("adb -s %s shell input keyevent 4" % glass.serial)
    while not glass(resourceId="com.upuphone.star.launcher:id/iv_icon").exists:
        logging.info("未进入到dock页面，再次单击返回")
        if not glass.info.get("screenOn"):
            # 点击power进入待机页面
            glass.press("power")
            time.sleep(1)
        glass.press("4")
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


def set_address(phone, a_type):
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


def get_current_value(glass, key):
    ret = [glass(resourceId="com.upuphone.star.launcher:id/sub_content")[i].get_text() for i in
           range(glass(resourceId="com.upuphone.star.launcher:id/sub_content").count) if
           key in glass(resourceId="com.upuphone.star.launcher:id/sub_content")[i].sibling()[1].get_text()]
    return ret[0]


class SmokePagePhone(BasePage):
    def __init__(self, driver):
        self.platform = root_dir.split('\\')[-1]
        super(SmokePagePhone, self).__init__(driver)
        self.element = ElementRouter.select(self.__class__.__name__, "element")
        self.data = Data(self.driver).data

    @allure.step("设置翻译字幕内容")
    def click_set_fanyi_src(self):
        self.find_element_and_click(**self.element["start_navi"])
        time.sleep(5)
        logging.info("设置翻译字幕内容为显示原文+译文")
        set_fanyi_src(self.driver, t_type="all")

    @allure.step("发起同传翻译")
    def click_start_translater(self):
        start_app_reconnect(self.driver)
        logging.info("--------------超级APP启动-同传翻译-翻译停止开始-手机退出（交替字幕显示）--------------")
        time.sleep(3)
        self.driver.swipe_ext("up")
        time.sleep(4)
        if self.driver(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").exists:
            logging.info("点击翻译官")
            self.driver(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").click()
        else:
            logging.error("手机未找到翻译官图标")
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(4)
        if self.driver(resourceId="com.upuphone.star.launcher:id/tv_title", text="同传翻译").exists:
            logging.info("手机已经进入翻译官首页，选择翻译类型")
            time.sleep(3)
            self.driver(resourceId="com.upuphone.star.launcher:id/tv_title", text="同传翻译").click()
            time.sleep(2)
        else:
            logging.error("手机未进入翻译官首页")
            get_screen_shot(self.driver)
            pytest.assume(False)
        if self.driver(resourceId="com.upuphone.star.launcher:id/cl_trans_btn").exists:
            logging.info("手机端点击翻译类型后进入到翻译设置页面，开始翻译")
            global thread
            thread = multiprocessing.Process(target=play_music, args=(60,))
            # thread.setDaemon(True)
            thread.start()
            self.driver(resourceId="com.upuphone.star.launcher:id/tv_trans_btn", text="开始翻译").click()
            logging.info("点击开始翻译， 翻译8s")
            time.sleep(3)

    @allure.step("手机端点击停止翻译")
    def phone_stop_translater(self):
        self.driver(resourceId="com.upuphone.star.launcher:id/tv_trans_btn", text="停止翻译").click()
        logging.info("翻译5s后手机端停止翻译")
        time.sleep(2)

    @allure.step("发起语音转写")
    def click_start_voice(self):
        start_app_reconnect(self.driver)
        logging.info("-------------------超级APP启动-语音转写-翻译停止开始-手机退出------------------------")
        time.sleep(3)
        self.driver.swipe_ext("up")
        time.sleep(4)
        if self.driver(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").exists:
            logging.info("点击翻译官")
            self.driver(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").click()
        else:
            logging.error("手机未找到翻译官图标")
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(4)
        if self.driver(resourceId="com.upuphone.star.launcher:id/tv_title", text="语音转写").exists:
            logging.info("手机已经进入翻译官首页，选择翻译类型")
            time.sleep(3)
            self.driver(resourceId="com.upuphone.star.launcher:id/tv_title", text="语音转写").click()
            time.sleep(2)
            if self.driver(resourceId="com.upuphone.star.launcher:id/cl_transcribe_btn").exists:
                logging.info("手机端点击翻译类型后进入到语音转写页面")
                global thread_voice
                thread_voice = multiprocessing.Process(target=play_music, args=(60,))
                # thread.setDaemon(True)
                thread_voice.start()
                self.driver(resourceId="com.upuphone.star.launcher:id/cl_transcribe_btn").click()
                logging.info("点击开始转写， 转写8s")
                time.sleep(8)
        else:
            logging.error("手机未进入翻译官首页")
            get_screen_shot(self.driver)
            pytest.assume(False)

    @allure.step("手机端点击停止转写")
    def phone_stop_voice(self):
        self.driver(resourceId="com.upuphone.star.launcher:id/tv_transcribe_btn", text="停止转写").click()
        logging.info("翻译5s后手机端停止转写")
        time.sleep(2)

    @allure.step("手机关闭抖音")
    def phone_stop_tiktok(self):
        self.driver.app_stop('com.ss.android.ugc.aweme')
        time.sleep(2)

    @allure.step("手机关闭快手")
    def phone_stop_kuaishou(self):
        self.driver.app_stop('com.smile.gifmaker')
        time.sleep(2)

    @allure.step("设置家庭地址")
    def phone_set_home(self):
        set_address(self.driver, "添加家")

    @allure.step("手机开始导航")
    def phone_start_navi(self):
        start_app_reconnect(self.driver)
        self.driver.swipe_ext("up", 0.8)
        time.sleep(0.8)
        logging.info("点击发起导航")
        self.driver(resourceId="com.upuphone.star.launcher:id/card_title", text="导航").click()
        time.sleep(1)
        self.driver(resourceId="com.upuphone.star.launcher:id/bottom_edit").click()
        time.sleep(1)
        logging.info("输入天府广场")
        self.driver(resourceId="com.upuphone.star.launcher:id/keyWord").set_text("天府广场")
        time.sleep(3)
        logging.info("点击搜索结果第一个天府广场")
        self.driver(resourceId="com.upuphone.star.launcher:id/name", textContains="天府广场")[0].click()
        time.sleep(4)
        logging.info("点击路线")
        time.sleep(5)
        logging.info("点击开始导航")
        self.driver(resourceId="com.upuphone.star.launcher:id/navi").click()
        time.sleep(10)


class SmokePageGlass(BasePage):
    def __init__(self, driver):
        self.platform = root_dir.split('\\')[-1]
        super(SmokePageGlass, self).__init__(driver)
        self.element = ElementRouter.select(self.__class__.__name__, "element")
        self.data = Data(self.driver).data

    @allure.step("检查眼镜端是否开始翻译")
    def glass_check_translater(self):
        if self.driver(resourceId="com.upuphone.star.launcher:id/tips", textContains="长按触控板停止").exists:
            logging.info("点击开始翻译后，眼镜端正常开始翻译")
            time.sleep(5)
            # 检测翻译字幕内容
            if self.driver(resourceId="com.upuphone.star.launcher:id/tv_dst").exists and self.driver(
                    resourceId="com.upuphone.star.launcher:id/tv_src").exists:
                logging.info("眼镜翻译界面显示原文+译文")
            else:
                logging.error("眼镜翻译界面字幕有误")
                get_screen_shot(self.driver)
                pytest.assume(False)
            time.sleep(5)
            thread.terminate()
        else:
            logging.error("点击开始翻译后，眼镜端未正常开始翻译")
            get_screen_shot(self.driver)
            pytest.assume(False)

    @allure.step("检查眼镜端是否停止翻译，并退出")
    def glass_check_translater_stop(self):
        if self.driver(resourceId="com.upuphone.star.launcher:id/tips", textContains="长按触控板停止").exists:
            logging.info("手机停止翻译成功，眼镜端退出翻译页面")
        else:
            logging.error("手机停止翻译成功，眼镜端未退出翻译页面")
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("翻译首页长按tp回到待机页面")
        self.driver.keyevent("4")
        time.sleep(3)
        if self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            logging.info("翻译首页长按tp回到待机页面成功")
            time.sleep(2)
        else:
            logging.error("翻译首页长按tp回到待机页面未成功")
            get_screen_shot(self.driver)
            pytest.assume(False)

    @allure.step("检查眼镜端是否开始转写")
    def glass_check_voice(self):
        if self.driver(resourceId="com.upuphone.star.launcher:id/tips", textContains="长按触控板停止").exists:
            logging.info("点击开始转写后，眼镜端正常开始转写，出现拾音条")
            time.sleep(5)
            if self.driver(resourceId="com.upuphone.star.launcher:id/rv_result").exists:
                logging.info("眼镜端正常开始语音转写，出现字幕")
            else:
                logging.error("眼镜端未正常开始语音转写")
                get_screen_shot(self.driver)
                pytest.assume(False)
        else:
            logging.error("点击开始转写后，眼镜端未正常开始转写")
            get_screen_shot(self.driver)
            pytest.assume(False)

    @allure.step("检查眼镜端是否停止转写，并退出")
    def glass_check_voice_stop(self):
        if self.driver(resourceId="com.upuphone.star.launcher:id/tips", textContains="长按触控板停止").exists:
            logging.info("手机停止转写成功，眼镜端退出转写页面")
        else:
            logging.error("手机停止转写成功，眼镜端未退出转写页面")
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("翻译首页长按tp回到待机页面")
        self.driver.keyevent("4")
        time.sleep(3)
        if self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            logging.info("翻译首页长按tp回到待机页面成功")
            time.sleep(2)
        else:
            logging.error("翻译首页长按tp回到待机页面未成功")
            get_screen_shot(self.driver)
            pytest.assume(False)
        thread_voice.terminate()

    @allure.step("dock启动同传翻译")
    def click_start_translater(self):
        glass_to_app(self.driver, "翻译官", "com.upuphone.star.launcher:id/iv_icon", flag=False)
        time.sleep(3)
        thread_glass = multiprocessing.Process(target=play_music, args=(60,))
        # thread.setDaemon(True)
        thread_glass.start()
        self.driver.keyevent("22")
        time.sleep(1)
        self.driver.keyevent("23")
        time.sleep(5)
        if self.driver(resourceId="com.upuphone.star.launcher:id/lottieWave").exists:
            logging.info("眼镜端点击同传翻译后进入同传翻译成功， 翻译5s")
            time.sleep(5)
            if self.driver(resourceId="com.upuphone.star.launcher:id/tv_dst").exists and self.driver(
                    resourceId="com.upuphone.star.launcher:id/tv_src").exists:
                logging.info("眼镜翻译界面显示原文+译文")
            else:
                logging.error("眼镜翻译界面字幕有误")
                get_screen_shot(self.driver)
                pytest.assume(False)
            time.sleep(5)
        else:
            logging.error("眼镜端点击同传翻译后进入同传翻译未成功")
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("翻译中长按tp回到翻译官首页")
        self.driver.keyevent("4")
        time.sleep(3)
        if not self.driver(resourceId="com.upuphone.star.launcher:id/lottieWave").exists:
            logging.info("翻译中长按tp回到翻译官首页成功")
            time.sleep(2)
        else:
            logging.error("翻译中长按tp回到翻译官首页未成功")
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("翻译首页长按tp回到待机页面")
        self.driver.keyevent("4")
        time.sleep(3)
        if self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            logging.info("翻译首页长按tp回到待机页面成功")
            time.sleep(2)
        else:
            logging.error("翻译首页长按tp回到待机页面未成功")
            get_screen_shot(self.driver)
            pytest.assume(False)
        thread_glass.terminate()

    @allure.step("dock启动语音转写")
    def click_start_voice(self):
        glass_to_app(self.driver, "翻译官", "com.upuphone.star.launcher:id/iv_icon", flag=False)
        time.sleep(3)
        thread = multiprocessing.Process(target=play_music, args=(60,))
        # thread.setDaemon(True)
        thread.start()
        self.driver.keyevent("22")
        time.sleep(1)
        self.driver.keyevent("22")
        time.sleep(1)
        self.driver.keyevent("23")
        time.sleep(3)
        if self.driver(resourceId="com.upuphone.star.launcher:id/lottieWave").exists:
            logging.info("眼镜端点击同传翻译后进入语音转写成功， 转写5s，出现拾音条")
            time.sleep(5)
            if self.driver(resourceId="com.upuphone.star.launcher:id/rv_result").exists:
                logging.info("眼镜端正常开始语音转写，出现字幕")
            else:
                logging.error("眼镜端未正常开始语音转写")
                get_screen_shot(self.driver)
                pytest.assume(False)
        else:
            logging.error("眼镜端点击同传翻译后进入语音转写未成功")
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("翻译中长按tp回到翻译官首页")
        self.driver.keyevent("4")
        time.sleep(3)
        if not self.driver(resourceId="com.upuphone.star.launcher:id/lottieWave").exists:
            logging.info("翻译中长按tp回到翻译官首页成功")
            time.sleep(2)
        else:
            logging.error("翻译中长按tp回到翻译官首页未成功")
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("翻译首页长按tp回到待机页面")
        self.driver.keyevent("4")
        time.sleep(3)
        if self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            logging.info("翻译首页长按tp回到待机页面成功")
            time.sleep(2)
        else:
            logging.error("翻译首页长按tp回到待机页面未成功")
            get_screen_shot(self.driver)
            pytest.assume(False)
        thread.terminate()

    @allure.step("dock启动抖音")
    def click_start_tiktok(self):
        glass_to_app(self.driver, "抖音", "com.upuphone.star.launcher:id/iv_icon", flag=False)
        time.sleep(15)
        if not self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            line = datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
            logging.info("-----------抖音投屏成功，TP下滑, 发送时间：%s------------" % line)
            os.system("adb -s %s shell input keyevent 22" % self.driver.serial)
            time.sleep(4)
            line = datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
            logging.info("-----------抖音投屏成功，TP上滑, 发送时间：%s------------" % line)
            os.system("adb -s %s shell input keyevent 21" % self.driver.serial)
            time.sleep(4)
            logging.info("-----------抖音投屏成功，TP双击进入小窗------------")
            os.system("adb -s %s shell input keyevent 314" % self.driver.serial)
            time.sleep(3)
            if self.driver(resourceId="com.upuphone.star.launcher:id/picture_view_container").exists:
                logging.info("眼镜端双击进入待机小窗成功")
                time.sleep(3)
            else:
                logging.error("眼镜端双击进入待机小窗未成功")
                get_screen_shot(self.driver)
                pytest.assume(False)
            logging.info("单击TP从小窗进入应用")
            os.system("adb -s %s shell input keyevent 23" % self.driver.serial)
            time.sleep(4)
            if not self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
                logging.info("单击TP从小窗进入应用成功")
                time.sleep(3)
            else:
                logging.error("单击TP从小窗进入应用未成功")
                get_screen_shot(self.driver)
                pytest.assume(False)
            logging.info("tp长按退出抖音")
            os.system(
                "adb -s %s shell input keyevent 4&&adb -s %s shell input keyevent 4" % (
                    self.driver.serial, self.driver.serial))
            # os.system("adb -s %s shell input keyevent 4" % glass.serial)
            time.sleep(4)
            if self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
                logging.info("TP退出抖音成功")
            else:
                logging.error("TP退出抖音失败")
                get_screen_shot(self.driver)
                pytest.assume(False)
        else:
            logging.error("眼镜端未投屏抖音成功,眼镜端显示在待机页面")
            get_screen_shot(self.driver)
            pytest.assume(False)

    @allure.step("dock启动快手")
    def click_start_kuaishou(self):
        glass_to_app(self.driver, "快手", "com.upuphone.star.launcher:id/iv_icon", flag=False)
        time.sleep(15)
        if not self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            line = datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
            logging.info("-----------快手投屏成功，TP下滑, 发送时间：%s------------" % line)
            os.system("adb -s %s shell input keyevent 22" % self.driver.serial)
            time.sleep(4)
            line = datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3]
            logging.info("-----------快手投屏成功，TP上滑, 发送时间：%s------------" % line)
            os.system("adb -s %s shell input keyevent 21" % self.driver.serial)
            time.sleep(4)
            logging.info("-----------快手投屏成功，TP双击进入小窗------------")
            os.system("adb -s %s shell input keyevent 314" % self.driver.serial)
            time.sleep(3)
            if self.driver(resourceId="com.upuphone.star.launcher:id/picture_view_container").exists:
                logging.info("眼镜端双击进入待机小窗成功")
                time.sleep(3)
            else:
                logging.error("眼镜端双击进入待机小窗未成功")
                get_screen_shot(self.driver)
                pytest.assume(False)
            logging.info("单击TP从小窗进入应用")
            os.system("adb -s %s shell input keyevent 23" % self.driver.serial)
            time.sleep(4)
            if not self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
                logging.info("单击TP从小窗进入应用成功")
                time.sleep(3)
            else:
                logging.error("单击TP从小窗进入应用未成功")
                get_screen_shot(self.driver)
                pytest.assume(False)
            logging.info("tp长按退出快手")
            os.system(
                "adb -s %s shell input keyevent 4&&adb -s %s shell input keyevent 4" % (
                    self.driver.serial, self.driver.serial))
            time.sleep(4)
            if self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
                logging.info("TP退出快手成功")
            else:
                logging.error("TP退出快手失败")
                get_screen_shot(self.driver)
                pytest.assume(False)
        else:
            logging.error("眼镜端未投屏快手成功，眼镜端显示在待机页面")
            get_screen_shot(self.driver)
            pytest.assume(False)

    @allure.step("dock启动导航")
    def click_start_navi(self):
        glass_to_app(self.driver, "导航", "com.upuphone.star.launcher:id/address_bg_view")
        time.sleep(3)
        # # 呼出语音助理
        # os.system("adb -s %s shell %s" % (self.driver.serial, config_r.order_dict.get("power_press")))
        # time.sleep(15)
        if self.driver(resourceId="com.upuphone.star.launcher:id/address_item", text="回家").exists:
            logging.info("眼镜端添加家庭地址成功")
            time.sleep(1)
        else:
            logging.error("眼镜端添加家庭地址失败")
            get_screen_shot(self.driver)
            pytest.assume(False)
        self.driver.keyevent("22")
        # self.driver(resourceId="com.upuphone.star.launcher:id/address_item", text="回家").click()
        time.sleep(1)
        self.driver.keyevent("23")
        # self.driver(resourceId="com.upuphone.star.launcher:id/address_item", text="回家").click()
        time.sleep(10)
        if not self.driver(resourceId="com.upuphone.star.launcher:id/info_layout").exists:
            logging.error("开始导航后10s眼镜仍未有导航画面")
            get_screen_shot(self.driver)
            pytest.assume(False)
        else:
            logging.info("眼镜端导航成功")
            # 超级app端关闭导航路线
            time.sleep(8)
            logging.info("双击tp进入小窗模式")
            self.driver.keyevent("314")
            time.sleep(3)
            if self.driver(resourceId="com.upuphone.star.launcher:id/navi_content_layout").exists:
                logging.info("TP双击进入小窗成功")
            else:
                logging.error("TP双击进入小窗成功")
                get_screen_shot(self.driver)
                pytest.assume(False)
            logging.info("单击TP从小窗进入应用")
            os.system("adb -s %s shell input keyevent 23" % self.driver.serial)
            time.sleep(4)
            if not self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
                logging.info("单击TP从小窗进入应用成功")
                time.sleep(3)
            else:
                logging.error("单击TP从小窗进入应用未成功")
                get_screen_shot(self.driver)
                pytest.assume(False)
            logging.info("眼镜端长按退出导航")
            os.system("adb -s %s shell input keyevent 4" % self.driver.serial)
            time.sleep(4)
            if self.driver(resourceId="com.upuphone.star.launcher:id/info_layout").exists:
                logging.error("手机退出导航后眼镜仍未有导航画面")
                get_screen_shot(self.driver)
                pytest.assume(False)
            else:
                logging.info("眼镜退出导航成功！")

    @allure.step("眼镜检查导航")
    def check_navi_glass(self):
        if not self.driver(resourceId="com.upuphone.star.launcher:id/info_layout").exists:
            logging.error("手机开始导航后10s眼镜仍未有导航画面")
            get_screen_shot(self.driver)
            pytest.assume(False)
        else:
            logging.info("眼镜端导航成功")
            time.sleep(8)
            logging.info("双击tp进入小窗模式")
            self.driver.keyevent("314")
            time.sleep(3)
            if self.driver(resourceId="com.upuphone.star.launcher:id/navi_content_layout").exists:
                logging.info("TP双击进入小窗成功")
            else:
                logging.error("TP双击进入小窗成功")
                get_screen_shot(self.driver)
                pytest.assume(False)
            logging.info("单击TP从小窗进入应用")
            os.system("adb -s %s shell input keyevent 23" % self.driver.serial)
            time.sleep(4)
            if not self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
                logging.info("单击TP从小窗进入应用成功")
                time.sleep(3)
            else:
                logging.error("单击TP从小窗进入应用未成功")
                get_screen_shot(self.driver)
                pytest.assume(False)
            # 超级app端关闭导航路线
            time.sleep(5)
            logging.info("眼镜端长按退出导航")
            os.system("adb -s %s shell input keyevent 4" % self.driver.serial)
            time.sleep(4)
            if self.driver(resourceId="com.upuphone.star.launcher:id/info_layout").exists:
                logging.error("手机退出导航后眼镜仍未有导航画面")
                get_screen_shot(self.driver)
                assert False
            else:
                logging.info("眼镜退出导航成功！")

    @allure.step("眼镜设置音量")
    def glass_set_vol(self):
        before_vol = int(os.popen(
            "adb -s %s shell settings get system volume_music_speaker" % self.driver.serial).readlines()[
                             0].strip())
        glass_to_app(self.driver, "设置", "com.upuphone.star.launcher:id/setting_page_title")
        time.sleep(3)
        self.driver.keyevent("23")
        time.sleep(1.5)
        if self.driver(resourceId="com.upuphone.star.launcher:id/volume_view").exists:
            logging.info("眼镜端设置页面点击音量出现音量条，前滑上焦")
        else:
            logging.error("眼镜端设置页面点击音量未出现音量条")
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("调节音量前音量为：%s" % before_vol)
        logging.info("TP前滑调节音量")
        # os.system("adb -s %s shell input keyevent 22" % self.driver.serial)
        self.driver.keyevent("21")
        time.sleep(0.5)
        self.driver.keyevent("22")
        # time.sleep(3)
        after_vol = int(os.popen(
            "adb -s %s shell  settings get system volume_music_speaker" % self.driver.serial).readlines()[
                            0].strip())
        logging.info("TP前滑调节音量后音量为：%s" % after_vol)
        if after_vol > before_vol:
            logging.info("TP前滑后音量调整成功！调节前：%s，调节后：%s" % (before_vol, after_vol))
        else:
            logging.error("TP前滑后音量调整失败！调节前：%s，调节后：%s" % (before_vol, after_vol))
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("TP长按回退到设置主页面")
        self.driver.keyevent("4")
        time.sleep(2)
        if self.driver(resourceId="com.upuphone.star.launcher:id/setting_page_title", text="设置").exists:
            logging.info("TP长按回退到设置主页面成功")
        else:
            logging.error("TP长按回退到设置主页面失败")
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(1)
        # TODO 还有对比调节后得值做百分比比较
        if int(get_current_value(self.driver, "音量").split("%")[0]) == int(float(
                str(after_vol / 15).split(".")[0] + "." + str(after_vol / 15).split(".")[1][:2]) * 100):
            logging.info("音量显示百分比成功，百分比为：%s" % get_current_value(self.driver, "音量"))
        else:
            logging.info("音量显示百分比失败，设置显示为：%s，调节到：%s" % (get_current_value(self.driver, "音量"), int(float(
                str(after_vol / 15).split(".")[0] + "." + str(after_vol / 15).split(".")[1][:2]) * 100)))
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(1)
        self.driver.keyevent("23")
        time.sleep(2)
        logging.info("TP后滑调节音量")
        self.driver.keyevent("22")
        time.sleep(0.5)
        self.driver.keyevent("21")
        # time.sleep(3)
        after_vol_1 = int(os.popen(
            "adb -s %s shell settings get system volume_music_speaker" % self.driver.serial).readlines()[
                              0].strip())
        logging.info("TP后滑调节音量后音量为：%s" % after_vol_1)
        if after_vol_1 < after_vol:
            logging.info("TP后滑后音量调整成功！调节前：%s，调节后：%s" % (after_vol, after_vol_1))
        else:
            logging.error("TP后滑后音量调整失败！调节前：%s，调节后：%s" % (after_vol, after_vol_1))
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("TP长按回退到设置主页面")
        self.driver.keyevent("4")
        time.sleep(2)
        if self.driver(resourceId="com.upuphone.star.launcher:id/setting_page_title", text="设置").exists:
            logging.info("TP长按回退到设置主页面成功")
        else:
            logging.error("TP长按回退到设置主页面失败")
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(1)
        # TODO 还有对比调节后得值做百分比比较
        if int(get_current_value(self.driver, "音量").split("%")[0]) == int(
                float(str(after_vol_1 / 15).split(".")[0] + "." + str(after_vol_1 / 15).split(".")[1][:2]) * 100):
            logging.info("音量显示百分比成功，百分比为：%s" % get_current_value(self.driver, "音量"))
        else:
            logging.info(
                "音量显示百分比失败，设置显示为：%s，调节到：%s" % (get_current_value(self.driver, "音量"), int(float(
                    str(after_vol_1 / 15).split(".")[0] + "." + str(after_vol_1 / 15).split(".")[1][:2]) * 100)))
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(1)
        logging.info("TP长按回退到待机页面")
        self.driver.keyevent("4")
        time.sleep(2)
        if self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            logging.info("TP长按后，眼镜回到待机页面")
        else:
            logging.error("TP长按后，眼镜未回到待机页面")
            get_screen_shot(self.driver)
            pytest.assume(False)

    @allure.step("眼镜设置亮度")
    def glass_set_bri(self):
        bri_dict = {"10": 0, "25": 10, "51": 20, "64": 30, "102": 40, "128": 50, "153": 60, "179": 70, "204": 80,
                    "230": 90, "255": 100}
        logging.info("-------------------眼镜端设置调节亮度------------------------")
        before_bri = int(os.popen(
            "adb -s %s shell settings get system screen_brightness" % self.driver.serial).readlines()[
                             0].strip())
        glass_to_app(self.driver, "设置", "com.upuphone.star.launcher:id/setting_page_title")
        time.sleep(2)
        self.driver.keyevent("22")
        time.sleep(0.5)
        self.driver.keyevent("22")
        # glass(resourceId="com.upuphone.star.launcher:id/name", text="亮度").click()
        time.sleep(1)
        self.driver.keyevent("23")
        time.sleep(2)
        if self.driver(resourceId="com.upuphone.star.launcher:id/brightness_view").exists:
            logging.info("眼镜端设置页面点击亮度出现亮度条")
        else:
            logging.error("眼镜端设置页面点击亮度未出现亮度条")
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("调节亮度前亮度为：%s" % before_bri)
        logging.info("TP前滑调节亮度")
        os.system("adb -s %s shell input keyevent 22" % self.driver.serial)
        time.sleep(3)
        after_bri = int(os.popen(
            "adb -s %s shell settings get system screen_brightness" % self.driver.serial).readlines()[
                            0].strip())
        logging.info("TP前滑调节亮度后亮度为：%s" % after_bri)
        if after_bri > before_bri:
            logging.info("TP前滑后亮度调整成功！调节前：%s，调节后：%s" % (before_bri, after_bri))
        else:
            logging.error("TP前滑后亮度调整失败！调节前：%s，调节后：%s" % (before_bri, after_bri))
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("TP长按回退到设置主页面")
        self.driver.keyevent("4")
        time.sleep(2)
        if self.driver(resourceId="com.upuphone.star.launcher:id/setting_page_title", text="设置").exists:
            logging.info("TP长按回退到设置主页面成功")
        else:
            logging.error("TP长按回退到设置主页面失败")
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(1)
        # TODO 还有对比调节后得值做百分比比较
        if int(get_current_value(self.driver, "亮度").split("%")[0]) == bri_dict[str(after_bri)]:
            logging.info("亮度显示百分比成功，百分比为：%s" % get_current_value(self.driver, "亮度"))
        else:
            logging.info("亮度显示百分比失败，百分比为：%s" % get_current_value(self.driver, "亮度"))
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(1)
        self.driver.keyevent("23")
        time.sleep(2)
        logging.info("TP后滑调节亮度")
        self.driver.keyevent("21")
        time.sleep(3)
        after_bri_1 = int(os.popen(
            "adb -s %s shell settings get system screen_brightness" % self.driver.serial).readlines()[
                              0].strip())
        logging.info("TP后滑调节亮度后亮度为：%s" % after_bri_1)
        if after_bri_1 < after_bri:
            logging.info("TP后滑后亮度调整成功！调节前：%s，调节后：%s" % (after_bri, after_bri_1))
        else:
            logging.error("TP后滑后亮度调整失败！调节前：%s，调节后：%s" % (after_bri, after_bri_1))
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("TP长按回退到设置主页面")
        self.driver.keyevent("4")
        time.sleep(2)
        if self.driver(resourceId="com.upuphone.star.launcher:id/setting_page_title", text="设置").exists:
            logging.info("TP长按回退到设置主页面成功")
        else:
            logging.error("TP长按回退到设置主页面失败")
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(1)
        # TODO 还有对比调节后得值做百分比比较
        if int(get_current_value(self.driver, "亮度").split("%")[0]) == bri_dict[str(after_bri_1)]:
            logging.info("亮度显示百分比成功，百分比为：%s" % get_current_value(self.driver, "亮度"))
        else:
            logging.info("亮度显示百分比失败，百分比为：%s" % get_current_value(self.driver, "亮度"))
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(1)
        logging.info("TP长按回退到待机页面")
        self.driver.keyevent("4")
        time.sleep(2)
        if self.driver(resourceId="com.upuphone.star.launcher:id/time_view").exists:
            logging.info("TP长按后，眼镜回到待机页面")
        else:
            logging.error("TP长按后，眼镜未回到待机页面")
            get_screen_shot(self.driver)
            pytest.assume(False)

    @allure.step("眼镜端呼出关机页面")
    def glass_power_page(self):
        power_press = "sendevent /dev/input/event0 1 116 1;sendevent /dev/input/event0 0 0 0;sleep 5;sendevent /dev/input/event0 1 116 0;sendevent /dev/input/event0 0 0 0"
        os.system("adb -s %s shell %s" % (self.driver.serial, power_press))
        time.sleep(1)
        if self.driver(resourceId="com.upuphone.star.launcher:id/system_shutdown_btn").exists:
            logging.info("长按5s电源键呼出关机页面成功")
        else:
            logging.error("长按5s电源键呼出关机页面失败")
            get_screen_shot(self.driver)
            pytest.assume(False)
        time.sleep(2)
        logging.info("TP长按退出关机页面")
        self.driver.keyevent("4")
        time.sleep(2)
        if not self.driver(resourceId="com.upuphone.star.launcher:id/system_shutdown_btn").exists:
            logging.info("TP长按后，TP长按退出关机页面成功")
        else:
            logging.error("TP长按后，TP长按退出关机页面失败")
            get_screen_shot(self.driver)
            pytest.assume(False)

    @allure.step("眼镜端启动音乐")
    def glass_start_music(self):
        glass_to_app(self.driver, "QQ音乐", "com.upuphone.star.launcher:id/cl_song_info_layout")
        time.sleep(5)
        self.driver.keyevent("22")
        # time.sleep(0.5)
        # if self.driver(resourceId="com.upuphone.star.launcher:id/iv_play").info.get("selected"):
        #     # 已上焦到播放/暂停按钮，点击播放
        self.driver.keyevent("23")
        time.sleep(3)
        if self.driver(resourceId="com.upuphone.star.launcher:id/iv_pause").exists:
            logging.info("单击TP之后开始播放歌曲， 播放8s")
            time.sleep(8)
        else:
            logging.error("播放按钮上焦后单击TP未播放音乐")
            get_screen_shot(self.driver)
            pytest.assume(False)
        # 切换歌曲
        get_current_music = self.driver(resourceId="com.upuphone.star.launcher:id/tv_artist").get_text()
        logging.info("当前播放歌曲为：%s" % get_current_music)
        self.driver.keyevent("22")
        time.sleep(0.5)
        self.driver.keyevent("22")
        time.sleep(0.5)
        self.driver.keyevent("23")
        time.sleep(1)
        logging.info("切换下一首，播放音乐8s")
        time.sleep(8)
        get_current_music_before = self.driver(resourceId="com.upuphone.star.launcher:id/tv_artist").get_text()
        if get_current_music_before != get_current_music:
            logging.info("眼镜端切换下一首成功；切换后：%s，切换前：%s" % (get_current_music_before, get_current_music))
        else:
            logging.error("眼镜端tp切换下一首失败；切换后：%s， 切换前: %s" % (get_current_music_before, get_current_music))
            get_screen_shot(self.driver)
            pytest.assume(False)
        logging.info("切换上一首，播放音乐8s")
        time.sleep(8)
        self.driver.keyevent("22")
        time.sleep(0.5)
        self.driver.keyevent("21")
        time.sleep(1)
        self.driver.keyevent("23")
        time.sleep(1)
        get_current_music_after = self.driver(resourceId="com.upuphone.star.launcher:id/tv_artist").get_text()
        if get_current_music_after != get_current_music_before and get_current_music_after == get_current_music:
            logging.info("眼镜端tp切换上一首成功；切换后：%s， 切换前: %s" % (get_current_music_after, get_current_music_before))
        else:
            logging.error("眼镜端tp切换上一首失败；切换后：%s， 切换前: %s" % (get_current_music_after, get_current_music_before))
            get_screen_shot(self.driver)
            pytest.assume(False)
        # TODO 剩余退出音乐操作，先写单击暂停
        self.driver.keyevent("23")
        time.sleep(1)
        if self.driver(resourceId="com.upuphone.star.launcher:id/iv_pause").info.get("selected"):
            # 已上焦到播放/暂停按钮，点击播放
            self.driver.keyevent("23")
            time.sleep(1)
            if self.driver(resourceId="com.upuphone.star.launcher:id/iv_play").exists:
                logging.info("单击TP之后暂停成功")
            else:
                logging.error("单击TP之后暂停失败")
                get_screen_shot(self.driver)
                pytest.assume(False)
        # else:
        #     logging.error("QQ音乐页面单击TP未上焦到播放/暂停按钮")
        #     get_screen_shot(self.driver)
        #     pytest.assume(False)
        logging.info("TP长按tp回到待机页面，显示播控中心")
        self.driver.keyevent("4")
        time.sleep(3)
        if self.driver(resourceId="com.upuphone.star.launcher:id/song_artist").exists:
            logging.info("TP长按tp回到待机页面成功显示播控中心")
            time.sleep(2)
        else:
            logging.error("TP长按tp回到待机页面未成功显示播控中心")
            get_screen_shot(self.driver)
            pytest.assume(False)


class Data(BasePage):
    def __init__(self, driver):
        self.platform = root_dir.split('\\')[-1]
        super(Data, self).__init__(driver)
        self.data = ElementRouter.select(self.__class__.__name__, "data")
