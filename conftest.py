#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import os
import re
import subprocess
import time
import uuid

import allure
import pytest
import uiautomator2 as u2
import wda

from common import project_dir
from common.config_parser import ReadConfig
from common.utils import get_installed_package_name
from common.adb_tool import AdbTools


@pytest.fixture(scope="package")
def driver(request):
    global platform, package_name, app_name, devices, error_logs
    app_name = request.param.get("app_name")
    platform = ReadConfig().get_platform(app_name)
    error_logs = ReadConfig().error_log
    package_name = get_installed_package_name(app_name)
    if isinstance(package_name, dict):
        package_name = package_name[request.param.get("devices")]
    else:
        package_name = package_name
    if platform == "android":
        devices = request.param.get("devices")
        os.system('adb -s %s root' % devices)
        driver = u2.connect(devices)  # 连接设备(usb只能插入单个设备)
        # driver.service("uiautomator").start()
        # driver.set_fastinput_ime(True)  # 启用自动化定制的输入法
        driver.settings["operation_delay"] = (0.2, 0.2)  # 操作后的延迟，(0, 0)表示操作前等待0s，操作后等待0s
        driver.settings['operation_delay_methods'] = ['click', 'swipe', 'drag', 'press']
        driver.implicitly_wait(ReadConfig().get_implicitly_wait(app_name))  # 设置隐式等待时间，默认20s
        # driver.unlock()  # 解锁
        if not driver.info['screenOn']:
            driver.press("power")
            driver.swipe(0.5, 0.9, 0.9, 0.1)
            # TODO 源码无以下这行，原因是手机滑动之后会有延迟，需增加超时机制
            time.sleep(1)  # 解锁

        screen_off_timeout = os.popen('adb -s %s shell settings get system screen_off_timeout' % devices).read().strip()
        if screen_off_timeout != '1800000':
            os.system('adb -s %s shell settings put system screen_off_timeout 1800000' % devices)
        with driver.watch_context(builtin=True) as ctx:
            ctx.when("^(下载|更新)").when("取消").click()  # 当同时出现（下载 或 更新）和 取消 按钮时，点击取消
            ctx.when("跳过%").click()
            # ctx.when("%允许%").click()
            # ctx.when("允许").click()
            ctx.when("继续").click()
            ctx.when("每次开启").click()
            ctx.when("创建").when("取消").click()
            ctx.when("恢复").when("取消").click()
            for element in ReadConfig().get_popup_elements(app_name):
                ctx.when(element).click()
            ctx.wait_stable(seconds=1.5)  # 开启弹窗监控，并等待界面稳定（两个弹窗检查周期内没有弹窗代表稳定）
            yield driver
            driver.set_fastinput_ime(False)  # 关闭自动化定制的输入法
            # driver.app_stop_all()  # 停止所有应
            driver.press("home")
            os.system('adb -s %s shell settings put system screen_off_timeout %s' % (devices, screen_off_timeout))
            driver.screen_off()  # 息屏
            # driver.service("uiautomator").stop()
    elif platform == "ios":
        driver = wda.USBClient().session(alert_action=wda.AlertAction.ACCEPT)
        driver.wait_ready()
        driver.implicitly_wait(ReadConfig().get_implicitly_wait)
        # driver.unlock()  # 解锁
        if not driver.info['screenOn']:
            driver.press("power")
            driver.swipe(0.5, 0.9, 0.9, 0.1)
            # TODO 源码无以下这行，原因是手机滑动之后会有延迟，需增加超时机制
            time.sleep(1)
        with driver.alert.watch_and_click():
            for element in ReadConfig().get_popup_elements(app_name):
                ele = driver(labelContains=element).get(timeout=2.5, raise_error=False)
                if ele is None:
                    continue
                else:
                    ele.tap()
            yield driver
            driver.close()
            driver.lock()  # 息屏


@pytest.fixture(scope="function")
def start_stop_app(driver):
    record_file = None
    if platform == "android":
        screenrecord_path = os.path.join(project_dir, "report", "screenrecord")
        if not os.path.exists(screenrecord_path):
            os.makedirs(screenrecord_path)
        record_file = os.path.join(screenrecord_path, time.strftime("%m%d_%H%M%S") + ".mp4")
        try:
            driver.screenrecord(record_file)  # 开始录制视频
            logging.info("start screen recording: %s", str(record_file))
        except Exception as e:
            logging.info(e)
    logcat_path = os.path.join(project_dir, "report", "logcat")
    if not os.path.exists(logcat_path):
        os.makedirs(logcat_path)
    logcat_filename = os.path.join(logcat_path,
                                   platform + "-" + time.strftime("%m%d_%H%M%S",
                                                                  time.localtime(time.time())) + ".txt")
    logcat_file = open(logcat_filename, "w")
    # driver.unlock()  # 解锁
    if not driver.info['screenOn']:
        driver.press("power")
        driver.swipe(0.5, 0.9, 0.9, 0.1)
        # TODO 源码无以下这行，原因是手机滑动之后会有延迟，需增加超时机制
        time.sleep(1)  # 解锁设备  # 解锁设备
    driver.app_stop(package_name)  # 确保待测app已终止
    # driver.app_stop_all()  # 确保待测app已终止
    poplog = None
    if platform == "android":
        os.system("adb -s %s logcat -c" % driver._serial)
        poplog = subprocess.Popen(["adb", "-s", driver._serial, "logcat", "-v", "threadtime"],
                                  stdout=logcat_file,
                                  stderr=subprocess.PIPE)  # 启动logcat捕获日志
        logging.info("start capturing log: %s", str(logcat_file))
        driver.app_start(package_name, wait=True)  # 启动app
        while driver.current_app()["package"] != "com.android.settings":
            time.sleep(0.5)
            # TODO star  打开通知权限
        if driver(textContains="星纪AR").exists:
            # TODO 点击授权
            driver(textContains="星纪AR").click()
            # TODO 点击打开
            driver(resourceId="android:id/switch_widget", text="关闭").click()
            # TODO 点击允许字样
            driver(textContains="允许").click()
            time.sleep(0.5)
            driver.press("back")
            time.sleep(0.5)
            driver.press("back")
        else:
            # TODO 先找到再授权
            driver(scrollable=True).scroll.to(text="星纪AR")
        while not driver(textContains="开始体验").exists:
            time.sleep(1)
        driver(textContains="开始体验").click()
        time.sleep(1)
        pop_info = driver(resourceId="com.upuphone.star.launcher:id/card_title", text="翻译官").exists
        while not pop_info:
            time.sleep(2)
    elif platform == "ios":
        poplog = subprocess.Popen(["idevicesyslog"], stdout=logcat_file,
                                  stderr=subprocess.PIPE)  # 启动idevicesyslog捕获日志
        logging.info("start capturing log: %s", str(logcat_file))
        driver.app_activate(package_name)  # 启动app
    logging.info("start app: %s", str(package_name))
    yield
    if platform == "android":
        driver.screenrecord.stop()  # 停止录制视频
        logging.info("stop screen recording")
        try:
            allure.attach.file(record_file, "执行视频 " + str(record_file), allure.attachment_type.MP4)  # 添加视频到报告中
        except Exception as e:
            logging.info(e)
    logcat_file.close()
    poplog.terminate()  # 停止日志捕获
    # todo sc_log抓取
    file_path = os.path.join(os.path.abspath(project_dir), "report", driver.serial + "_" + app_name, "sc_log")
    file_name = time.strftime('%Y_%m_%d_%H_%M', time.localtime(time.time())) + "_" + app_name
    cmd = "%s\\scLogTools\\get_log.bat %s %s" % (
        os.path.abspath(os.path.dirname(project_dir)), driver.serial, os.path.join(file_path, file_name))
    os.system(cmd)
    time.sleep(2)
    logging.info("已抓取sclog日志")
    with open(logcat_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            for error in list(error_logs.keys()):
                if re.findall(error, line):
                    logging.error("存在%s错误: %s" % (error, line))
    logging.info("stop capturing log")
    allure.attach.file(logcat_filename, "logcat日志 " + str(logcat_filename),
                       allure.attachment_type.TEXT)  # 添加logcat日志到报告中
    driver.app_stop(package_name)  # 停止app
    logging.info("stop app: %s", str(package_name))


@pytest.fixture(scope="function")
def clear_cache(driver):
    yield
    logging.info("clear app cache")
    driver.app_clear(package_name)


def _add_screenshot(driver):
    """ 添加截图 """
    screenshot_path = os.path.join(project_dir, "report", "screenshot")
    if not os.path.exists(screenshot_path):
        os.makedirs(screenshot_path)
    filename = os.path.join(screenshot_path, str(uuid.uuid1()) + ".png")
    driver.screenshot(filename)  # 截图
    logging.info("take screenshot: %s", str(filename))
    allure.attach.file(filename, "失败截图 " + time.strftime("%m-%d %H:%M:%S", time.localtime()) + " " + str(filename),
                       allure.attachment_type.PNG)  # 添加截图到报告中


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        for i in item.funcargs:
            if isinstance(item.funcargs[i], u2.Device) or isinstance(item.funcargs[i], wda.Client):
                _add_screenshot(item.funcargs[i])


def pytest_collection_modifyitems(session, items):
    print("收集到的测试用例:%s" % items)
    # all_items = [os.listdir(os.path.join(i, "case")) for i in ReadConfig().pkg_config_path]
    # new_items = [i for j in all_items for i in j if i.startswith("test")]
    # # 期望用例顺序按照.py文件执行
    # appoint_classes = {}
    #
    # for i in new_items:
    #     appoint_classes[i] = []
    #
    # for item in items:
    #     for cls_name in appoint_classes:
    #         if item.parent.parent.name == cls_name:
    #             appoint_classes[cls_name].append(item)
    # items.clear()
    # for cases in appoint_classes.values():
    #     items.extend(cases)
    # print("整理后的测试用例:%s" % items)
