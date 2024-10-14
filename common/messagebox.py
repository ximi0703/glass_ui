#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# @Author   : chuanwen.peng
# @Time     : 2022/4/15 14:21
# @File     : messagebox.py
# @Project  : Glass_UI
"""

import tkinter


def box(message, timeout=20):

    root = tkinter.Tk()
    root.geometry("300x100")
    root.title("提示")
    root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
    root.attributes("-topmost", True)

    _kvs = {"result": "retry"}

    # def cancel_timer(*args):
    #     root.after_cancel(_kvs['root'])
    #     root.title("Manual")
    #
    # def update_prompt():
    #     cancel_timer()

    def f(result):
        def _inner():
            _kvs['result'] = result
            root.destroy()
            root.quit()
        return _inner

    tkinter.Label(root, text=message).pack(side=tkinter.TOP, fill=tkinter.X, pady=10)

    frmbtns = tkinter.Frame(root)
    # tkinter.Button(frmbtns, text="跳过", command=f('skip')).pack(side=tkinter.LEFT)
    tkinter.Button(frmbtns, text="准备好了", command=f('retry')).pack(side=tkinter.LEFT)
    # tkinter.Button(frmbtns, text="终止", command=f('abort')).pack(side=tkinter.LEFT)
    frmbtns.pack(side=tkinter.BOTTOM)

    prompt = tkinter.StringVar()
    label1 = tkinter.Label(root, textvariable=prompt)
    label1.pack()

    # deadline = time.time() + timeout

    # def _refresh_timer():
    #     leftseconds = deadline - time.time()
    #     if leftseconds <= 0:
    #         root.destroy()
    #         return
    #     root.title("即将跳过此用例 " + str(int(leftseconds)) + " s")
    #     _kvs['root'] = root.after(500, _refresh_timer)

    # _kvs['root'] = root.after(0, _refresh_timer)
    # root.bind('<Button-1>', cancel_timer)
    root.mainloop()

    return _kvs['result']


if __name__ == '__main__':
    print(box('嗨！\n请用实体门禁卡靠近测试机NFC区域\n点击准备好了再贴卡哈'))
