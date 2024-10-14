#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import shutil
import sys
import time
import pytest
import platform
import argparse

import requests
import uiautomator2

from common import project_dir
from common.config_parser import ReadConfig
from common.utils import Util


def local_run(app_name):
    env = ReadConfig().get_env
    # args = [app_name[0] + "/case/", app_name[1] + "/case/", app_name[2] + "/case/", app_name[3] + "/case/",
    #         app_name[4] + "/case/", app_name[5] + "/case/", "-m S", "--alluredir", project_dir + "/report/raw_data/"]
    args = [app_name[0] + "/case/test_smoke_star_new.py", "-m M",
            "--alluredir", project_dir + "/report/raw_data/"]
    pytest.main(args)


def generate_report():
    report_path = os.path.join(project_dir, "report",
                               "html_report_" + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time())))
    os.system("allure generate " + project_dir + "/report/raw_data/ -o " + report_path)
    return report_path


def open_report(report_path):
    # windows TODO 判断平台在linux会出错
    os.system("allure open %s -p 2022" % report_path)
    # os.system("nohup allure open %s -p 2022 &" % report_path)


def break_app(serial):
    phone = uiautomator2.connect(serial)
    if not phone.info['screenOn']:
        phone.press("power")
        time.sleep(1)
        phone.swipe(0.5, 0.9, 0.5, 0.5)
        # TODO 源码无以下这行，原因是手机滑动之后会有延迟，需增加超时机制
        time.sleep(1)  # 解锁
    os.system(
        "adb -s %s shell am start -n com.upuphone.star.launcher/com.upuphone.xr.sapp.superconnect.ui.SplashActivity --ez force_login false" % serial)
    time.sleep(4)
    with phone.watch_context(builtin=True) as ctx:
        ctx.when("跳过%").click()
        ctx.when("暂不升级").click()
        ctx.when("允许").click()
        ctx.when("仅在使用时允许").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("同意").click()
        ctx.when("继续").click()
        ctx.when("每次开启").click()
        ctx.when("刷新一下").click()
        # ctx.when("去开启").click()
        ctx.when("创建").when("取消").click()
        ctx.when("恢复").when("取消").click()
        ctx.wait_stable(seconds=1.5)
        before_time = time.time()
        time.sleep(8)
        while not phone(resourceId="com.upuphone.star.launcher:id/confirm", text="去开启").exists:
            if time.time() - before_time >= 120:
                logging.error('--------无去开启弹窗---------')
                os.system("kill -9 %s" % args.p)
                sys.exit()
            time.sleep(3)
        time.sleep(3)
        if not phone(resourceId="com.upuphone.star.launcher:id/confirm", text="去开启").exists:
            logging.error('--------无去开启弹窗---------')
            os.system("kill -9 %s" % args.p)
            sys.exit()
        phone(resourceId="com.upuphone.star.launcher:id/confirm", text="去开启").click()
        time.sleep(3)
        check_status = phone(resourceId="android:id/title", text="星纪AR").exists
        before_time = time.time()
        while not check_status:
            if time.time() - before_time >= 30:
                logging.error('--------无星纪AR选项---------')
                os.system("kill -9 %s" % args.p)
                sys.exit()
            time.sleep(5)
            check_status = phone(resourceId="android:id/title", text="星纪AR").exists
        if not phone(resourceId="android:id/title", text="星纪AR").exists:
            logging.error('--------无星纪AR选项---------')
            os.system("kill -9 %s" % args.p)
            sys.exit()
        phone(resourceId="android:id/title", text="星纪AR").click()
        time.sleep(2)
        while not phone(resourceId="com.android.settings:id/preference_text_layout").exists:
            if phone(resourceId="android:id/title", text="星纪AR").exists:
                phone(resourceId="android:id/title", text="星纪AR").click()
                time.sleep(3)
            else:
                logging.error('--------选择星纪AR后无授权选项---------')
                os.system("kill -9 %s" % args.p)
                sys.exit()
        phone(resourceId="com.android.settings:id/preference_text_layout").click()
        time.sleep(5)
        if phone(resourceId="android:id/switch_widget", text="开启").exists:
            phone.press("back")
            phone.press("back")
        if phone(text="勿扰模式").exists:
            phone(text="勿扰模式").click()
        time.sleep(3)
        phone.app_stop("com.upuphone.star.launcher")


def phone_connect_wifi(serial):
    # 检查手机是否连接wifi
    wifi_status = Util().wifi_connect_status(serial)
    if not wifi_status:
        os.system("adb -s %s shell svc wifi enable" % serial)
        time.sleep(3)
    if not Util().get_network_state(serial):
        Util().connect_wifi(serial)
    time.sleep(3)
    logging.info("=======手机已连接wifi==========")


def alter(file):
    new_data = []
    with open(file, 'r+', encoding='utf-8') as f:
        filedata = f.readlines()
        for line in filedata:
            if "wifi_verbose_logging_enabled" in line:
                line = line.replace('false', 'true')
            new_data.append(line)
    with open(file, 'w', encoding='utf-8') as f:
        for line in new_data:
            f.write(line)


def get_wlan_log(serial):
    Util().dev_root(serial)
    wifi_path = os.path.join(module_name, "WifiConfigStore.xml")
    if os.path.exists(wifi_path):
        os.remove(wifi_path)
    # TODO 获取build文件
    logging.error("开始获取wifi配置文件")
    os.system(
        "adb -s %s shell cat data/misc/apexdata/com.android.wifi/WifiConfigStore.xml > WifiConfigStore.xml" % serial)
    logging.error("复制WIFI文件命令发送成功")
    while not os.path.exists(wifi_path):
        time.sleep(3)
        logging.error("重试获取wifi配置文件")
        os.system(
            "adb -s %s shell cat data/misc/apexdata/com.android.wifi/WifiConfigStore.xml > WifiConfigStore.xml" % serial)
    logging.error("完成获取wifi配置文件")
    file_name = os.path.join(module_name, wifi_path)
    # TODO 判断当前服务状态
    with open(wifi_path, 'r+', encoding='utf-8') as f:
        filedata = f.readlines()
        for line in filedata:
            if 'name="wifi_verbose_logging_enabled"' in line:
                alter(file=file_name)
                status = 1 if "error" in os.popen(
                    "adb -s %s push %s data/misc/apexdata/com.android.wifi/WifiConfigStore.xml" % (
                        serial, file_name)).read() else 0
                while status:
                    logging.error("重试文件传输")
                    os.system("adb -s %s push %s data/misc/apexdata/com.android.wifi/WifiConfigStore.xml" % (
                        serial, file_name))
                    time.sleep(5)
                    status = 1 if "error" in os.popen(
                        "adb -s %s push %s system/WifiConfigStore.xml" % (serial, file_name)).read() else 0
                logging.error("文件传输成功")
                Util().dev_reboot(serial)
                Util().dev_root(serial)
                logging.info("已经打开wlan详细日志")
    if os.path.exists(wifi_path):
        os.remove(wifi_path)


def get_hci_log(serial):
    Util().dev_root(serial)
    os.system("adb -s %s shell setprop persist.bluetooth.btsnooplogmode full" % serial)
    time.sleep(3)
    os.system("adb -s %s shell svc bluetooth  disable" % serial)
    time.sleep(3)
    os.system("adb -s %s shell svc bluetooth enable" % serial)
    time.sleep(20)
    logging.info("已经打开hci详细日志")


def check_hci(serial):
    if "full" not in os.popen("adb -s %s shell getprop persist.bluetooth.btsnooplogmode" % serial).readlines()[0]:
        logging.info("正在打开%s设备的hci详细日志" % device)
        get_hci_log(device)
        logging.info("正在打开%s设备的wlan详细日志" % device)
        get_wlan_log(device)
    else:
        logging.error("已经打开HCI日志！！！删除以前的日志")
        logging.info("已经打开HCI日志！！！删除以前的日志")
        os.system("adb -s %s root" % serial)
        time.sleep(2)
        # todo 删除手机
        model_name = "mars" if "meizu" in os.popen("adb -s %s shell getprop ro.product.model" % serial).readlines()[
            0].lower() else "star"
        if "mars" in model_name:
            logging.info("删除手机sdcard/Android/log/下文件")
            os.system("adb -s %s shell rm -rf sdcard/Android/log/*" % serial)
            time.sleep(2)
        else:
            logging.info("删除眼镜/data/vendor/wifi/wlan_logs/下文件")
            os.system("adb -s %s shell rm -rf sdcard/Android/log/*" % serial)
            time.sleep(2)
            os.system("adb -s %s shell rm -rf /data/misc/bluetooth/logs/*" % serial)
            time.sleep(2)


def get_super_app(serial):
    current_day = time.strftime('%Y%m%d')
    logging.info("开始下载超级APP： %s..." % current_day)
    # 构建一个post请求
    url = 'https://package.upuphone.com/daily/app/superapp-daily/feature-sw5100-1.0-base/' + current_day + '0159/release/phoneMars/daily_superapp_PhoneMars_release_prd.apk'  # 接口地址
    res = requests.get(url)
    with open("super.apk", "wb") as f:
        f.write(res.content)
    logging.info("超级APP下载完成, 开始安装...")
    apk_path = os.path.join(os.getcwd(), "super.apk")
    # apk_path = os.path.join(os.getcwd(), super_apk_name)
    install_status = Util().install(serial, apk_path)
    time.sleep(2)
    if not install_status:
        assert False
    time.sleep(2)


if __name__ == "__main__":
    # module_name = '/home/chuanwenpeng/workspace/smoketest_glass/glass_ui/'
    module_name = os.getcwd()
    # super_apk = [i for i in os.listdir(os.getcwd()) if ".apk" in i]
    # if super_apk:
    #     super_apk_name = super_apk[0]
    try:
        if os.path.exists("report"):
            shutil.rmtree("report")
    except Exception as e:
        logging.error(e)
    # if os.path.exists(super_apk_name):
    #     os.remove(super_apk_name)
    app_list = ReadConfig().pkg_config_path
    report_list = []
    devices_dic = ReadConfig().get_package_name(app_list[0])
    devices = [i for i in list(devices_dic.keys())]
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=str)
    args = parser.parse_args()
    if len(devices) >= 2:
        logging.info('--------正在执行刷机互联流程---------')
        # connect_main(args.p)
    else:
        logging.error('--------当前连接设备不足两台---------')
        os.system("kill -9 %s" % args.p)
        sys.exit()
    # get_super_app(devices[-1])
    # break_app(devices[-1])
    # phone_connect_wifi(devices[-1])
    # logging.error("正在打开设备的hci&wifi详细日志")
    # for device in devices:
    #     logging.info("正在打开%s设备的hci&wifi详细日志" % device)
    #     logging.info("正在打开%s设备的hci&wifi详细日志" % device)
    #     check_hci(device)
    local_run(app_list)
    report_path = generate_report()
    logging.error("report location: %s" % report_path)
    report_list.append(report_path)
    [open_report(i) for i in report_list]
