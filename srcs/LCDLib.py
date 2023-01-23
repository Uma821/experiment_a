# -*- coding: utf-8 -*-
#
# LCDLib.py
#    参考書[1]の第7章（p.167--171）で紹介されている 07-02-LCD.py を
#    LCD モジュール 1602A に対応させたもの
# [1] 金丸著, Raspberry Piで学ぶ電子工作, 講談社, 2016.
#
# 以下のメソッドを提供
# class LCD1602A
# - setup()
# - clear()
# - newline()
# - write_string('abcd\nefg')
# - cursor_blink(True)
# - move_cursor(0, 3)
# 
import smbus
import sys
from time import sleep

class LCD1602A:

    def __init__(self, i2c_addr=0x27, chars=16, lines=2):
        self.bus = smbus.SMBus(1)
        self.address_1602a = i2c_addr
        self.register_setting = 0x00
        self.register_display = 0x40
        self.chars_per_line = chars # LCDの横方向の文字数
        self.display_lines = lines # LCDの行数
        self.display_chars = chars * lines
        self.position = 0
        self.line = 0
        self.DELAY = 0.0005

    def put_byte(self, ch, reg):
        if reg == self.register_setting:
            mode = 0x00 # command
        elif reg == self.register_display:
            mode = 0x01 # data
        else:
            raise Exception()

        backlight = 0x08 # on=0x08, off=0x00
        enable = 0b0000_0100

        bits_high_a = (ch & 0xf0) | backlight | mode
        bits_high_b = (ch & 0xf0) | backlight | mode | enable
        bits_low_a = ((ch & 0x0f)<<4) | backlight | mode
        bits_low_b = ((ch & 0x0f)<<4) | backlight | mode | enable

        # lines labeled X seem to be needless
        #self.bus.write_byte_data(self.address_1602a, reg, bits_high_a) # X
        #sleep(self.DELAY)
        self.bus.write_byte_data(self.address_1602a, reg, bits_high_b) # Y
        #self.bus.write_byte_data(self.address_1602a, reg, bits_high_a) # X
        #sleep(self.DELAY)
        #self.bus.write_byte_data(self.address_1602a, reg, bits_low_a) # X
        sleep(self.DELAY) # needed for the fast i2c bus such as 100kHz
        self.bus.write_byte_data(self.address_1602a, reg, bits_low_b) # Y
        self.bus.write_byte_data(self.address_1602a, reg, bits_low_a) # Y
        sleep(self.DELAY)

    def put_command(self, com):
        self.put_byte(com, self.register_setting)

    def put_char(self, ch):
        self.put_byte(ch, self.register_display)
        self.position += 1

    def cursor_blink(self, f):
        if f:
            self.put_command(0x0d)
        else:
            self.put_command(0x0c)

    def move_cursor(self, li, co):
        if li >= 0 and li <= 1 and co >= 0 and co <= 15:
            pos = (li * 0x40 + co) | 0x80
            self.put_command(pos)
            self.line = li
            self.position = li * self.chars_per_line + co
        else:
            print("position out of range")

    def setup(self):
        trials = 5
        for i in range(trials):
            try:
                # c_lower = (contrast & 0xf)
                # c_upper = (contrast & 0x30)>>4
                # self.bus.write_i2c_block_data(self.address_st7032, self.register_setting,
                #         [0x38, 0x39, 0x14, 0x70|c_lower, 0x54|c_upper, 0x6c])
                # sleep(0.2)
                # self.bus.write_i2c_block_data(self.address_1602a, self.register_setting, 
                #                          [0x38, 0x0d, 0x01])

                self.put_command(0x33) # init
                self.put_command(0x32) # init
                self.put_command(0x06) # cursor move direction
                self.put_command(0x0c) # display on, cursor off, blink off

                self.put_command(0x28) # data length, number of lines, font size
                # 4-bit bus, 2-line display, 5x8

                self.put_command(0x01) # clear display
                self.put_command(0x80) # 1st line

                sleep(0.001)

                break
            except IOError:
                print("IOError")
                if i==trials-1:
                    sys.exit()

    def clear(self):
        self.position = 0
        self.line = 0
        self.put_command(0x01)
        sleep(0.001)

    def newline(self):
        if self.line == self.display_lines-1:
            self.clear()
        else:
            self.line += 1
            self.position = self.chars_per_line * self.line
            self.put_command(0xc0)
            sleep(0.001)

    def write_string(self, s):
        for c in list(s):
            self.write_char(ord(c))

    def write_char(self, c):
        byte_data = self.check_writable(c)
        if self.position == self.display_chars: # スクリーンの末尾
            self.clear()
        elif self.position == self.chars_per_line*(self.line+1): # 行の末尾
            self.newline()
        if byte_data == ord('\n'): # 改行文字
            self.newline()
        else:
            self.put_char(byte_data) # 普通の文字

    def check_writable(self, c):
        if 0x06 <= c <= 0xff:
            return c
        elif 0xFF61 <= c <= 0xFF9F: # UTF-16->ASCII 半角カナ
            return c - 0xFF61 + 0xA1
        else:
            return 0x20 # 空白文字
