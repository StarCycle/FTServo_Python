#!/usr/bin/env python

import time
import serial
import sys
import platform

# 默认波特率设置为1000000
DEFAULT_BAUDRATE = 1000000
# 延迟计时器设置为50毫秒
LATENCY_TIMER = 50 

class PortHandler(object):
    def __init__(self, port_name):
        """
        初始化串口处理器
        输入参数: port_name - 串口设备名称(如'/dev/ttyUSB0'或'COM1')
        功能: 初始化串口处理器对象，设置默认参数
        """
        self.is_open = False  # 串口是否打开标志
        self.baudrate = DEFAULT_BAUDRATE  # 当前波特率
        self.packet_start_time = 0.0  # 数据包开始时间
        self.packet_timeout = 0.0  # 数据包超时时间
        self.tx_time_per_byte = 0.0  # 每字节传输时间

        self.is_using = False  # 串口是否正在使用标志
        self.port_name = port_name  # 串口设备名称
        self.ser = None  # 串口对象

    def openPort(self):
        """
        打开串口
        输入参数: 无
        输出: 布尔值，表示是否成功打开串口
        功能: 使用当前波特率设置打开串口
        """
        return self.setBaudRate(self.baudrate)

    def closePort(self):
        """
        关闭串口
        输入参数: 无
        输出: 无
        功能: 关闭已打开的串口连接
        """
        self.ser.close()
        self.is_open = False

    def clearPort(self):
        """
        清空串口缓冲区
        输入参数: 无
        输出: 无
        功能: 清空串口的输入输出缓冲区
        """
        self.ser.flush()

    def setPortName(self, port_name):
        """
        设置串口设备名称
        输入参数: port_name - 串口设备名称
        输出: 无
        功能: 设置要连接的串口设备名称
        """
        self.port_name = port_name

    def getPortName(self):
        """
        获取串口设备名称
        输入参数: 无
        输出: 字符串，当前设置的串口设备名称
        功能: 返回当前设置的串口设备名称
        """
        return self.port_name

    def setBaudRate(self, baudrate):
        """
        设置波特率
        输入参数: baudrate - 要设置的波特率值
        输出: 布尔值，表示是否成功设置波特率
        功能: 设置串口通信的波特率，并重新配置串口
        """
        baud = self.getCFlagBaud(baudrate)

        if baud <= 0:
            # 不支持的自定义波特率，返回失败
            return False  # TODO: 未来可能支持设置自定义波特率
        else:
            self.baudrate = baudrate
            return self.setupPort(baud)

    def getBaudRate(self):
        """
        获取当前波特率
        输入参数: 无
        输出: 整数，当前波特率值
        功能: 返回当前设置的波特率值
        """
        return self.baudrate

    def getBytesAvailable(self):
        """
        获取可读字节数
        输入参数: 无
        输出: 整数，输入缓冲区中的字节数
        功能: 返回串口输入缓冲区中当前可读取的字节数量
        """
        return self.ser.in_waiting

    def readPort(self, length):
        """
        从串口读取数据
        输入参数: length - 要读取的字节数
        输出: 字节列表或字节串，取决于Python版本
        功能: 从串口读取指定长度的数据，兼容Python 2和3
        """
        if (sys.version_info > (3, 0)):
            # Python 3: 返回字节串
            return self.ser.read(length)
        else:
            # Python 2: 返回字节值列表
            return [ord(ch) for ch in self.ser.read(length)]

    def writePort(self, packet):
        """
        向串口写入数据
        输入参数: packet - 要写入的数据（字节列表或字节串）
        输出: 整数，实际写入的字节数
        功能: 将数据写入串口输出缓冲区
        """
        return self.ser.write(packet)

    def setPacketTimeout(self, packet_length):
        """
        设置数据包超时时间（基于数据包长度）
        输入参数: packet_length - 数据包长度（字节数）
        输出: 无
        功能: 根据数据包长度计算并设置超时时间
        """
        self.packet_start_time = self.getCurrentTime()
        # 计算超时时间：传输时间 + 额外缓冲时间 + 固定延迟
        self.packet_timeout = (self.tx_time_per_byte * packet_length) + (self.tx_time_per_byte * 3.0) + LATENCY_TIMER

    def setPacketTimeoutMillis(self, msec):
        """
        设置数据包超时时间（毫秒）
        输入参数: msec - 超时时间（毫秒）
        输出: 无
        功能: 直接设置数据包超时时间为指定的毫秒数
        """
        self.packet_start_time = self.getCurrentTime()
        self.packet_timeout = msec

    def isPacketTimeout(self):
        """
        检查数据包是否超时
        输入参数: 无
        输出: 布尔值，表示是否超时
        功能: 检查自数据包开始时间以来是否已超过超时时间
        """
        if self.getTimeSinceStart() > self.packet_timeout:
            self.packet_timeout = 0  # 重置超时时间
            return True  # 已超时

        return False  # 未超时

    def getCurrentTime(self):
        """
        获取当前时间（毫秒精度）
        输入参数: 无
        输出: 浮点数，当前时间（毫秒）
        功能: 返回当前时间，精度为毫秒
        """
        return round(time.time() * 1000000000) / 1000000.0

    def getTimeSinceStart(self):
        """
        获取自数据包开始时间以来的时间
        输入参数: 无
        输出: 浮点数，经过的时间（毫秒）
        功能: 计算并返回自数据包开始时间以来经过的时间
        """
        time_since = self.getCurrentTime() - self.packet_start_time
        if time_since < 0.0:
            # 时间异常，重置开始时间
            self.packet_start_time = self.getCurrentTime()

        return time_since

    def setupPort(self, cflag_baud):
        """
        配置串口参数
        输入参数: cflag_baud - 标准波特率值
        输出: 布尔值，表示是否成功配置串口
        功能: 根据指定参数配置串口连接
        """
        if self.is_open:
            # 如果串口已打开，先关闭
            self.closePort()

        # 创建并配置串口对象
        self.ser = serial.Serial(
            port=self.port_name,
            baudrate=self.baudrate,
            # parity = serial.PARITY_ODD,  # 可选的奇偶校验设置
            # stopbits = serial.STOPBITS_TWO,  # 可选的停止位设置
            bytesize=serial.EIGHTBITS,  # 8位数据位
            timeout=0  # 非阻塞读取
        )

        self.is_open = True  # 标记串口已打开

        self.ser.reset_input_buffer()  # 清空输入缓冲区

        # 计算每字节传输时间（毫秒）
        self.tx_time_per_byte = (1000.0 / self.baudrate) * 10.0

        return True  # 配置成功

    def getCFlagBaud(self, baudrate):
        """
        检查波特率是否受支持
        输入参数: baudrate - 要检查的波特率值
        输出: 整数，标准波特率值或-1（如果不支持）
        功能: 检查指定的波特率是否在支持的波特率列表中
        """
        # 支持的波特率列表
        if baudrate in [4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 250000, 500000, 1000000]:
            return baudrate  # 返回支持的波特率
        else:
            return -1  # 不支持的波特率    
