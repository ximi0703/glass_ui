# creater: chuanwen.peng
# time: 2022/7/12 12:30
import time

import allure

from Smoke.page.smoke_page import SmokePagePhone, SmokePageGlass


class SmokeFlow(object):
    def __init__(self, driver_list):
        if len(driver_list) == 1:
            self.route_page_glass = SmokePageGlass(driver_list[0])
        else:
            self.route_page_glass = SmokePageGlass(driver_list[0])
            self.route_page_phone = SmokePagePhone(driver_list[1])

    @allure.story("超级APP启动-同传翻译-翻译停止开始-手机退出")
    def smoke_start_translater_phone_end(self):
        self.route_page_phone.click_set_fanyi_src()
        self.route_page_phone.click_start_translater()
        self.route_page_glass.glass_check_translater()
        self.route_page_phone.phone_stop_translater()
        self.route_page_glass.glass_check_translater_stop()

    @allure.story("超级APP启动-语音转写-翻译停止开始-手机退出")
    def smoke_start_voice_phone_end(self):
        self.route_page_phone.click_start_voice()
        self.route_page_glass.glass_check_voice()
        self.route_page_phone.phone_stop_voice()
        self.route_page_glass.glass_check_voice_stop()

    @allure.story("dock启动-同传翻译-翻译停止开始-tp退出")
    def smoke_glass_start_voice_phone_end(self):
        self.route_page_phone.click_set_fanyi_src()
        self.route_page_glass.click_start_translater()

    @allure.story("dock启动-语音转写-翻译停止开始-tp退出")
    def smoke_glass_start_voice_phone_end(self):
        self.route_page_glass.click_start_voice()

    @allure.story("dock发起抖音-TP前后滑动-tp小窗-tp进入应用-TP双击退出")
    def smoke_glass_start_tiktok_end(self):
        self.route_page_phone.phone_stop_tiktok()
        self.route_page_glass.click_start_tiktok()

    @allure.story("dock发起抖音-TP前后滑动-tp小窗-tp进入应用-TP双击退出")
    def smoke_glass_start_kuaishou_end(self):
        self.route_page_phone.phone_stop_kuaishou()
        self.route_page_glass.click_start_kuaishou()

    @allure.story("眼镜启动导航-常用地址-眼镜退出压测")
    def smoke_glass_start_navi_end(self):
        self.route_page_phone.phone_set_home()
        self.route_page_glass.click_start_navi()

    @allure.story("手机启动导航-输入地址-切换出行方式-眼镜退出")
    def smoke_phone_start_navi_end(self):
        self.route_page_phone.phone_start_navi()
        self.route_page_glass.check_navi_glass()

    @allure.story("眼镜端设置调节音量")
    def smoke_glass_set_vol(self):
        self.route_page_glass.glass_set_vol()

    @allure.story("眼镜端设置亮度音量")
    def smoke_glass_set_bri(self):
        self.route_page_glass.glass_set_bri()

    @allure.story("眼镜端呼出关机页面")
    def smoke_glass_power_page(self):
        self.route_page_glass.glass_power_page()

    @allure.story("眼镜端启动qq音乐")
    def smoke_glass_qq_music(self):
        self.route_page_glass.glass_start_music()

