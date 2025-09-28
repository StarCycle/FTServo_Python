#!/usr/bin/env python

# 广播ID，用于向所有舵机发送指令
BROADCAST_ID = 0xFE  # 254

# 最大舵机ID
MAX_ID = 0xFC  # 252

# SCS协议数据字节序标志（0为小端格式，1为大端格式）
SCS_END = 0

# SCS协议指令集定义
INST_PING = 1        # 舵机检测指令
INST_READ = 2        # 读取舵机数据指令
INST_WRITE = 3       # 写入舵机数据指令
INST_REG_WRITE = 4   # 寄存器写入指令（需要配合ACTION指令执行）
INST_ACTION = 5      # 触发寄存器写入指令
INST_SYNC_WRITE = 131  # 0x83 同步写入指令（同时控制多个舵机）
INST_SYNC_READ = 130  # 0x82 同步读取指令（同时读取多个舵机状态）
INST_RESET = 10  # 0x0A 舵机复位指令
INST_OFSCAL = 11  # 0x0B 舵机偏移校准指令

# 通信结果代码定义
COMM_SUCCESS = 0  # 通信成功
COMM_PORT_BUSY = -1  # 串口繁忙（正在使用中）
COMM_TX_FAIL = -2  # 指令发送失败
COMM_RX_FAIL = -3  # 状态接收失败
COMM_TX_ERROR = -4  # 指令格式错误
COMM_RX_WAITING = -5  # 正在接收状态数据包
COMM_RX_TIMEOUT = -6  # 接收状态数据包超时
COMM_RX_CORRUPT = -7  # 状态数据包校验错误
COMM_NOT_AVAILABLE = -9  # 功能不可用
