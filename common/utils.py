#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# @Author   : chuanwen.peng
# @Time     : 2022/4/15 14:21
# @File     : utils.py
# @Project  : Glass_UI
"""

import logging
import os
import re
import subprocess
import time

import uiautomator2 as u2
from git import Repo

from common import project_dir
from common.config_parser import ReadConfig

platform = ReadConfig().get_platform


def get_android_version() -> int:
    android_version = os.popen("adb shell getprop ro.build.version.release").read().split(".")[0]
    logging.info("current android version is: {}".format(android_version))
    return int(android_version)


def get_installed_package_name(app_name) -> str:
    pkg_dict = ReadConfig().get_package_name(app_name)
    if isinstance(pkg_dict, dict):
        package_name = {}
        for package in pkg_dict:
            package_info = os.popen(
                "adb -s %s shell \"pm list packages |grep -ie %s\"" % (package, pkg_dict[package])).read()
            if package_info is not None:
                package_name[package] = pkg_dict[package]
                continue
        if package_name is None:
            raise RuntimeError("can not find package: {}".format(package_name))
        return package_name
    else:
        package_name = None
        for package in pkg_dict:
            package_info = os.popen("adb shell \"pm list packages |grep " + package + "\"").read()
            if package_info is not None:
                package_name = package_info
                continue
        if package_name is None:
            raise RuntimeError("can not find package: {}".format(package_name))
        return package_name


def install_app(file_path):
    logging.info("install app path: {}".format(file_path))
    try:
        if platform == "android":
            os.popen("adb install -d -r " + file_path)
            d = u2.connect()
            d.unlock()
            if get_android_version() >= 10:
                logging.info("install app finished")
                return
            element = d(text="重新安装")
            if element.wait(timeout=10.0):
                element.click()
            d.click(0.75, 0.95)  # 点击安装(比例定位)
            element = d(textContains="安装完成")
            if element.wait(timeout=20.0):
                d.click(0.25, 0.95)  # 点击完成(比例定位)
        elif platform == "ios":
            pass
        logging.info("install app finished")
    except Exception as e:
        logging.error("install app failed： {}".format(e))
        raise


def git_pull():
    repo = Repo(project_dir)
    repo.remote().pull()


class Util:
    def __init__(self):
        pass

    def get_bluetooth_devices(self, serial):
        """检查电池状态"""
        cmd = "adb -s %s shell dumpsys bluetooth_manager" % serial
        ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        res = [i for i in ret.stdout.readlines() if
               "name=AvrcpControllerStateMachine state=Connected" in i.decode("utf-8")]
        device_name = re.findall(r".*?\((.*)\)", res[0].decode(), re.S)
        return device_name

    def install(self, devices, path):
        """
        安装apk文件
        :return:
        """
        # adb install 安装错误常见列表
        errors = {'INSTALL_FAILED_ALREADY_EXISTS': '程序已经存在',
                  'INSTALL_DEVICES_NOT_FOUND': '找不到设备',
                  'INSTALL_FAILED_DEVICE_OFFLINE': '设备离线',
                  'INSTALL_FAILED_INVALID_APK': '无效的APK',
                  'INSTALL_FAILED_INVALID_URI': '无效的链接',
                  'INSTALL_FAILED_INSUFFICIENT_STORAGE': '没有足够的存储空间',
                  'INSTALL_FAILED_DUPLICATE_PACKAGE': '已存在同名程序',
                  'INSTALL_FAILED_NO_SHARED_USER': '要求的共享用户不存在',
                  'INSTALL_FAILED_UPDATE_INCOMPATIBLE': '版本不能共存',
                  'INSTALL_FAILED_SHARED_USER_INCOMPATIBLE': '需求的共享用户签名错误',
                  'INSTALL_FAILED_MISSING_SHARED_LIBRARY': '需求的共享库已丢失',
                  'INSTALL_FAILED_REPLACE_COULDNT_DELETE': '需求的共享库无效',
                  'INSTALL_FAILED_DEXOPT': 'dex优化验证失败',
                  'INSTALL_FAILED_DEVICE_NOSPACE': '手机存储空间不足导致apk拷贝失败',
                  'INSTALL_FAILED_DEVICE_COPY_FAILED': '文件拷贝失败',
                  'INSTALL_FAILED_OLDER_SDK': '系统版本过旧',
                  'INSTALL_FAILED_CONFLICTING_PROVIDER': '存在同名的内容提供者',
                  'INSTALL_FAILED_NEWER_SDK': '系统版本过新',
                  'INSTALL_FAILED_TEST_ONLY': '调用者不被允许测试的测试程序',
                  'INSTALL_FAILED_CPU_ABI_INCOMPATIBLE': '包含的本机代码不兼容',
                  'CPU_ABIINSTALL_FAILED_MISSING_FEATURE': '使用了一个无效的特性',
                  'INSTALL_FAILED_CONTAINER_ERROR': 'SD卡访问失败',
                  'INSTALL_FAILED_INVALID_INSTALL_LOCATION': '无效的安装路径',
                  'INSTALL_FAILED_MEDIA_UNAVAILABLE': 'SD卡不存在',
                  'INSTALL_FAILED_INTERNAL_ERROR': '系统问题导致安装失败',
                  'INSTALL_PARSE_FAILED_NO_CERTIFICATES': '文件未通过认证 >> 设置开启未知来源',
                  'INSTALL_PARSE_FAILED_INCONSISTENT_CERTIFICATES': '文件认证不一致 >> 先卸载原来的再安装',
                  'INSTALL_FAILED_INVALID_ZIP_FILE': '非法的zip文件 >> 先卸载原来的再安装',
                  'INSTALL_CANCELED_BY_USER': '需要用户确认才可进行安装',
                  'INSTALL_FAILED_VERIFICATION_FAILURE': '验证失败 >> 尝试重启手机',
                  'DEFAULT': '未知错误'
                  }
        print('Installing...')
        l = os.popen("adb -s %s install -r %s" % (devices, path)).read()
        if 'Success' in l:
            print('Install Success')
        if 'Failure' in l:
            reg = re.compile('\\[(.+?)\\]')
            key = re.findall(reg, l)[0]
            try:
                print('Install Failure >> %s' % errors[key])
            except KeyError:
                print('Install Failure >> %s' % key)
        return 1 if [i for i in l.split() if "Success" in i] else 0

    def get_network_state(self, devices):
        """
        设备是否连上互联网
        :return:
        """
        return 0 if subprocess.Popen('adb -s %s shell ping -w 1 www.baidu.com' % devices, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, shell=True).stderr.readlines() else 1

    def close_wear_detect(self, glass_serial):
        print("关闭佩戴检测服务")
        self.dev_root(glass_serial)
        os.system('adb -s %s shell "setprop persist.hw.wear.bp_support false"' % glass_serial)
        self.dev_reboot(glass_serial)

    def device_unlock(self, serial):
        while serial.info.get("currentPackageName") == 'com.android.systemui':
            # serial.unlock()
            serial.screen_on()
            serial.swipe(0.5, 0.9, 0.5, 0.1)
            time.sleep(0.5)
        # if serial.info.get('screenOn'):
        #     serial.screen_off()
        # time.sleep(0.5)  # 防止屏幕打开动作失效
        # serial.screen_on()
        # serial.swipe(0.5, 0.9, 0.5, 0.1)
        # time.sleep(0.5)

    def dev_lock_time(self, device):
        os.system('adb -s %s shell settings put system screen_off_timeout 1800000' % device)

    def dev_unlock(self, device):
        self.dev_root(device.serial)
        if not device.info['screenOn']:
            device.press("power")
            device.swipe(0.3, 0.9, 0.9, 0.1)
            # TODO 源码无以下这行，原因是手机滑动之后会有延迟，需增加超时机制
            time.sleep(1)

    def connect_wifi(self, device, path="common/adb-join-wifi.apk"):
        self.dev_root(device)
        install_status = self.install(device, path)
        if install_status:
            os.system(
                "adb -s %s shell am start -n com.steinwurf.adbjoinwifi/.MainActivity --esn connect -e ssid XR@Ruijie-5G -e password_type WPA -e password xjsd@123456" % device)
            time.sleep(2)
            # if not self.wifi_connect_status(device):
            u2.connect(device).app_stop("com.steinwurf.adbjoinwifi")

    def wifi_connect_status(self, device):
        logging.info("---------------------获取wifi连接状态： %s------------------------" % device)
        p = os.popen('adb -s %s shell settings get global wifi_on' % device)

        status = 1 if "1" in p.readline()[0] else 0
        if status:
            logging.info("---------------------获取wifi接状态： 开------------------------")
        else:
            logging.info("---------------------获取wifi接状态： 关------------------------")
        return status

    def bt_connect_status(self, device):
        p = os.popen('adb -s %s shell settings get global bluetooth_on' % device)

        status = 1 if "1" in p.readline()[0] else 0
        if status:
            logging.info("---------------------获取bluetooth接状态： 开------------------------")
        else:
            logging.info("---------------------获取bluetooth接状态： 关------------------------")
        return status

    def dev_root(self, serial):
        root_status = "adbd is already running as root" in [i.strip() for i in
                                                            os.popen("adb -s %s root" % serial).readlines()]
        if not root_status:
            time.sleep(3)
            root_status = "adbd is already running as root" in [i.strip() for i in
                                                                os.popen("adb -s %s root" % serial).readlines()]
        logging.info("---------------------root设备： %s成功------------------------" % serial)
        return root_status

    def dev_reboot(self, serial):
        os.system("adb -s %s reboot" % serial)
        time.sleep(40)
        root_status = 1 if serial in os.popen("adb devices").read() else 0
        while not root_status:
            time.sleep(5)
            root_status = 1 if serial in os.popen("adb devices").read() else 0
        logging.info("---------------------reboot设备： %s成功------------------------" % serial)
        return root_status

    def device_status(self, serial):
        """设备是否在线"""
        root_status = 1 if [i for i in os.popen("adb devices").readlines() if serial in i and "device" in i] else 0
        if not root_status:
            time.sleep(5)
            root_status = 1 if [i for i in os.popen("adb devices").readlines() if serial in i and "device" in i] else 0
        logging.info("---------------------device设备： %s成功------------------------" % serial)
        return root_status

    def simulate_wear(self, glass_serial):
        """模拟佩戴"""
        self.dev_root(glass_serial)
        os.system('adb -s %s shell "am broadcast -a com.upup.debug.WEAR_STATE_CHANGED --ei state 1"' % glass_serial)
        time.sleep(0.5)
