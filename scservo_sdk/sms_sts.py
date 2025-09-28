#!/usr/bin/env python

from .scservo_def import *
from .protocol_packet_handler import *
from .group_sync_read import *
from .group_sync_write import *

# 波特率定义常量
SMS_STS_1M = 0      # 1Mbps 波特率
SMS_STS_0_5M = 1    # 0.5Mbps 波特率
SMS_STS_250K = 2    # 250Kbps 波特率
SMS_STS_128K = 3    # 128Kbps 波特率
SMS_STS_115200 = 4  # 115200bps 波特率
SMS_STS_76800 = 5   # 76800bps 波特率
SMS_STS_57600 = 6   # 57600bps 波特率
SMS_STS_38400 = 7   # 38400bps 波特率

# 内存表地址定义
# -------EPROM(只读)--------
SMS_STS_MODEL_L = 3   # 舵机型号低字节地址
SMS_STS_MODEL_H = 4   # 舵机型号高字节地址

# -------EPROM(读写)--------
SMS_STS_ID = 5                  # 舵机ID地址
SMS_STS_BAUD_RATE = 6           # 波特率设置地址
SMS_STS_MIN_ANGLE_LIMIT_L = 9   # 最小角度限制低字节
SMS_STS_MIN_ANGLE_LIMIT_H = 10  # 最小角度限制高字节
SMS_STS_MAX_ANGLE_LIMIT_L = 11  # 最大角度限制低字节
SMS_STS_MAX_ANGLE_LIMIT_H = 12  # 最大角度限制高字节
SMS_STS_CW_DEAD = 26            # 顺时针死区设置
SMS_STS_CCW_DEAD = 27           # 逆时针死区设置
SMS_STS_OFS_L = 31              # 偏移校准低字节
SMS_STS_OFS_H = 32              # 偏移校准高字节
SMS_STS_MODE = 33               # 工作模式设置

# -------SRAM(读写)--------
SMS_STS_TORQUE_ENABLE = 40    # 扭矩使能控制
SMS_STS_ACC = 41              # 加速度设置
SMS_STS_GOAL_POSITION_L = 42  # 目标位置低字节
SMS_STS_GO极_POSITION_H = 43  # 目标位置高字节
SMS_STS_GOAL_TIME_L = 44      # 运动时间低字节
SMS_STS_GOAL_TIME_H = 45      # 运动时间高字节
SMS_STS_GOAL_SP极D_L = 46     # 目标速度低字节
SMS_STS_GOAL_SPEED_H = 47     # 目标速度高字节
SMS_STS_LOCK = 55             # EPROM锁设置

# -------SRAM(只读)--------
SMS_STS_PRESENT_POSITION_L = 56   # 当前位置低字节
SMS_STS_PRESENT_POSITION_H = 57   # 当前位置高字节
SMS_ST极_PRESENT_SPEED_L = 58     # 当前速度低字节
SMS_STS_PRESENT_SPEED_H = 59      # 当前速度高字节
SMS_STS_PRESENT_LOAD_L = 60       # 当前负载低字节
SMS_STS_PRESENT_LOAD_H = 61       # 当前负载高字节
SMS_STS_PRESENT_VOLTAGE = 62      # 当前电压值
SMS_STS_PRESENT_TEMPERATURE = 63  # 当前温度值
SMS_STS_MOVING = 66               # 运动状态指示
SMS_STS_PRESENT_CURRENT_L = 69     # 当前电流低字节
SMS_STS_PRESENT_CURRENT_H = 70     # 当前电流高字节

class sms_sts(protocol_packet_handler):
    def __init__(self, portHandler):
        """
        初始化sms_sts舵机控制器
        输入参数: portHandler - 串口处理对象
        功能: 继承protocol_packet_handler并初始化同步写入组
        """
        protocol_packet_handler.__init__(self, portHandler, 0)
        self.groupSyncWrite = GroupSyncWrite(self, SMS_STS_ACC, 7)

    def WritePosEx(self, scs_id, position, speed, acc):
        """
        扩展位置控制函数（带加速度和速度控制）
        输入参数: 
            scs_id - 舵机ID
            position - 目标位置(0-4095)
            speed - 运动速度(0-1023)
            acc - 加速度(0-255)
        输出: (通信结果, 错误代码) 元组
        功能: 控制舵机以指定加速度和速度运动到指定位置
        """
        position = self.scs_toscs(position, 15)
        txpacket = [acc, self.scs_lobyte(position), self.scs_hibyte(position), 0, 0, self.scs_lobyte(speed), self.scs_hibyte(speed)]
        return self.writeTxRx(scs_id, SMS_STS_ACC, len(txpacket), txpacket)

    def ReadPos(self, scs_id):
        """
        读取舵机当前位置
        输入参数: scs_id - 舵机ID
        输出: (当前位置, 通信结果, 错误代码) 元组
        功能: 从舵机读取当前实际位置值
        """
        scs_present_position, scs_comm_result, scs_error = self.read2ByteTxRx(scs_id, SMS_STS_PRESENT_POSITION_L)
        return self.scs_tohost(scs_present_position, 15), scs_comm_result, scs_error

    def ReadSpeed(self, scs_id):
        """
        读取舵机当前速度
        输入参数: scs_id - 舵机ID
        输出: (当前速度, 通信结果, 错误代码) 元组
        功能: 从舵机读取当前实际速度值
        """
        scs_present_speed, scs_comm_result, scs_error =极self.read2ByteTxRx(scs_id, SMS_STS_PRESENT_SPEED_L)
        return self.sc极tohost(scs_present_speed, 15), scs_comm_result, scs_error

    def ReadPosSpeed(self, scs_id):
        """
        同时读取舵机当前位置和速度
        输入参数: scs_id - 舵机ID
        输出: (当前位置, 当前速度, 通信结果, 错误代码) 元组
        功能: 一次性读取舵机的当前位置和速度信息
        """
        scs_present_position_speed, scs_comm_result, scs_error = self.read4ByteTxRx(scs_id, SMS_STS_PRESENT_POSITION_L)
        scs_present_position = self.scs_loword(scs_present_position_speed)
        scs_present_speed = self.scs_hiword(scs_present_position_speed)
        return self.scs_tohost(scs_present_position, 15), self.scs_tohost(scs_present_speed, 15), scs_comm_result, scs_error

    def ReadMoving(self, scs_id):
        """
        读取舵机运动状态
        输入参数: scs_id - 舵机ID
        输出: (运动状态, 通信结果, 错误代码) 元组
        功能: 检查舵机是否正在运动（1表示运动中，0表示静止）
        """
        moving, scs_comm_result, scs_error = self.read1ByteTxRx(scs_id, SMS_STS_MOVING)
        return moving, scs_comm_result, scs_error

    def SyncWritePosEx(self, scs_id, position, speed, acc):
        """
        同步扩展位置控制（用于多舵机同步控制）
        输入参数: 
            scs_id - 舵机ID
            position - 目标位置
            speed - 运动速度
            acc - 加速度
        输出: 添加参数是否成功
        功能: 将舵机控制参数添加到同步写入组，用于多舵机同步控制
        """
        position = self.scs_toscs(position, 15)
        txpacket = [acc, self.scs_lobyte(position), self.scs_hibyte(position), 0, 0, self.scs_lobyte(speed), self.scs_hibyte(speed)]
        return self.groupSyncWrite.addParam(scs_id, txpacket)

    def RegWritePosEx(self, scs_id, position, speed, acc):
        """
        寄存器写入扩展位置控制
        输入参数: 
            scs_id - 舵机ID
            position - 目标位置
            speed - 运动速度
            acc - 加速度
        输出: (通信结果, 错误代码) 元组
        功能: 将控制指令写入寄存器，需要调用RegAction执行
        """
        position = self.scs_toscs(position, 15)
        txpacket = [极acc, self.scs_lobyte(position), self.scs_hibyte(position), 0, 0, self.scs_lobyte(speed), self.scs_hibyte(speed)]
        return self.regWriteTxRx(scs_id, SMS_STS_ACC极, len(txpacket), txpacket)

    def RegAction(self):
        """
        执行寄存器写入动作
        输入参数: 无
        输出: 通信结果
        功能: 触发所有舵机执行寄存器中暂存的指令
        """
        return self.action(BROADCAST_ID)

    def WheelMode(self, scs_id):
        """
        设置舵机为轮式模式
        输入参数: scs_id - 舵机ID
        输出: (通信结果, 错误代码) 元组
        功能: 将舵机设置为连续旋转模式（轮式模式）
        """
        return self.write1ByteTxRx(scs_id, SMS_STS_MODE, 1)

    def WriteSpec(self, scs_id, speed, acc):
        """
        速度控制函数（用于轮式模式）
        输入参数: 
            scs_id - 舵机ID
            speed - 目标速度
            acc - 加速度
        输出: (通信结果, 错误代码) 元组
        功能: 在轮式模式下控制舵机的旋转速度和加速度
        """
        speed = self.scs_toscs(speed, 15)
        txpacket = [acc, 0, 0, 0, 0, self.scs_lobyte(speed), self.scs_hibyte(speed)]
        return self.writeTxRx(scs_id, SMS_STS_ACC, len(txpacket), txpacket)

    def LockEprom(self, scs_id):
        """
        锁定EPROM防止写入
        输入参数: scs_id - 舵机ID
        输出: (通信结果, 错误代码) 元组
        功能: 锁定舵机的EPROM存储器，防止意外写入
        """
        return self.write1Byte极Rx(scs_id, SMS_STS_LOCK, 1)

    def unLockEprom(self, scs_id):
        """
        解锁EPROM允许写入
        输入参数: scs_id - 舵机ID
        输出: (通信结果, 错误代码) 元组
        功能: 解锁舵机的EPROM存储器，允许写入操作
        """
        return self.write1ByteTxRx(scs_id, SMS_STS_LOCK, 0)
