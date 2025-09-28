#!/usr/bin/env python

from .scservo_def import *

# 定义数据包最大长度
TXPACKET_MAX_LEN = 250  # 发送包最大长度
RXPACKET_MAX_LEN = 250  # 接收包最大长度

# 数据包字段索引定义
PKT_HEADER0 = 0      # 包头字节0
PKT_HEADER1 = 1      # 包头字节1
PKT_ID = 2           # 舵机ID字段
PKT_LENGTH = 3       # 包长度字段
PKT_INSTRUCTION = 4  # 指令字段
PKT_ERROR = 4        # 错误字段（与指令字段相同位置）
PKT_PARAMETER0 = 5   # 参数起始字段

# 错误位定义
ERRBIT_VOLTAGE = 1    # 电压错误
ERRBIT_ANGLE = 2      # 角度传感器错误
ERRBIT_OVERHEAT = 4   # 过热错误
ERRBIT_OVERELE = 8    # 过流错误
ERRBIT_OVERLOAD = 32  # 过载错误


class protocol_packet_handler(object):
    def __init__(self, portHandler, protocol_end):
        """
        初始化协议包处理器。
        
        参数:
            portHandler: 端口处理对象，用于底层串口通信
            protocol_end: 协议端序设置（STS/SMS=0, SCS=1）
        """
        self.portHandler = portHandler
        self.scs_end = protocol_end

    def scs_getend(self):
        """
        获取当前协议端序设置。
        
        返回:
            int: 当前端序值（0或1）
        """
        return self.scs_end

    def scs_setend(self, e):
        """
        设置协议端序。
        
        参数:
            e: 端序值（0或1）
        """
        self.scs_end = e

    def scs_tohost(self, a, b):
        """
        将数据从舵机格式转换到主机格式（处理有符号数）。
        
        参数:
            a: 要转换的数据
            b: 符号位位置
            
        返回:
            int: 转换后的数据（有符号整数）
        """
        if (a & (1<<b)):
            return -(a & ~(1<<b))
        else:
            return a

    def scs_toscs(self, a, b):
        """
        将数据从主机格式转换到舵机格式（处理有符号数）。
        
        参数:
            a: 要转换的数据
            b: 符号位位置
            
        返回:
            int: 转换后的数据（无符号整数）
        """
        if (a<0):
            return (-a | (1<<b))
        else:
            return a

    def scs_makeword(self, a, b):
        """
        将两个字节组合成一个字（16位），根据端序设置。
        
        参数:
            a: 低字节或高字节（取决于端序）
            b: 高字节或低字节（取决于端序）
            
        返回:
            int: 组合后的字
        """
        if self.scs_end==0:
            return (a & 0xFF) | ((b & 0xFF) << 8)
        else:
            return (b & 0xFF) | ((a & 0xFF) << 8)

    def scs_makedword(self, a, b):
        """
        将两个字组合成一个双字（32位）。
        
        参数:
            a: 低字
            b: 高字
            
        返回:
            int: 组合后的双字
        """
        return (a & 0xFFFF) | (b & 0xFFFF) << 16

    def scs_loword(self, l):
        """
        获取双字的低字部分（低16位）。
        
        参数:
            l: 双字数据
            
        返回:
            int: 低字
        """
        return l & 0xFFFF

    def scs_hiword(self, h):
        """
        获取双字的高字部分（高16位）。
        
        参数:
            h: 双字数据
            
        返回:
            int: 高字
        """
        return (h >> 16) & 0xFFFF

    def scs_lobyte(self, w):
        """
        获取字的低字节（低8位），根据端序设置。
        
        参数:
            w: 字数据
            
        返回:
            int: 低字节
        """
        if self.scs_end==0:
            return w & 0xFF
        else:
            return (w >> 8) & 0xFF

    def scs_hibyte(self, w):
        """
        获取字的高字节（高8位），根据端序设置。
        
        参数:
            w: 字数据
            
        返回:
            int: 高字节
        """
        if self.scs_end==0:
            return (w >> 8) & 0xFF
        else:
            return w & 0xFF
        
    def getProtocolVersion(self):
        """
        获取协议版本。
        
        返回:
            float: 协议版本号（当前为1.0）
        """
        return 1.0

    def getTxRxResult(self, result):
        """
        根据通信结果代码获取描述字符串。
        
        参数:
            result: 通信结果代码
            
        返回:
            str: 结果描述
        """
        if result == COMM_SUCCESS:
            return "[TxRxResult] Communication success!"
        elif result == COMM_PORT_BUSY:
            return "[TxRxResult] Port is in use!"
        elif result == COMM_TX_FAIL:
            return "[TxRxResult] Failed transmit instruction packet!"
        elif result == COMM_RX_FAIL:
            return "[TxRxResult] Failed get status packet from device!"
        elif result == COMM_TX_ERROR:
            return "[TxRxResult] Incorrect instruction packet!"
        elif result == COMM_RX_WAITING:
            return "[TxRxResult] Now receiving status packet!"
        elif result == COMM_RX_TIMEOUT:
            return "[TxRxResult] There is no status packet!"
        elif result == COMM_RX_CORRUPT:
            return "[TxRxResult] Incorrect status packet!"
        elif result == COMM_NOT_AVAILABLE:
            return "[TxRxResult] Protocol does not support this function!"
        else:
            return ""

    def getRxPacketError(self, error):
        """
        根据错误位获取错误描述字符串。
        
        参数:
            error: 错误位掩码
            
        返回:
            str: 错误描述
        """
        if error & ERRBIT_VOLTAGE:
            return "[ServoStatus] Input voltage error!"

        if error & ERRBIT_ANGLE:
            return "[ServoStatus] Angle sen error!"

        if error & ERRBIT_OVERHEAT:
            return "[ServoStatus] Overheat error!"

        if error & ERRBIT_OVERELE:
            return "[ServoStatus] OverEle error!"
        
        if error & ERRBIT_OVERLOAD:
            return "[ServoStatus] Overload error!"

        return ""

    def txPacket(self, txpacket):
        """
        发送数据包。
        
        参数:
            txpacket: 要发送的数据包列表
            
        返回:
            int: 通信结果代码
        """
        checksum = 0
        total_packet_length = txpacket[PKT_LENGTH] + 4  # 4: HEADER0 HEADER1 ID LENGTH

        if self.portHandler.is_using:
            return COMM_PORT_BUSY
        self.portHandler.is_using = True

        # 检查包长度是否超限
        if total_packet_length > TXPACKET_MAX_LEN:
            self.portHandler.is_using = False
            return COMM_TX_ERROR

        # 设置包头
        txpacket[PKT_HEADER0] = 0xFF
        txpacket[PKT_HEADER1] = 0xFF

        # 计算校验和（除包头和校验和外所有字节的和的取反）
        for idx in range(2, total_packet_length - 1):  # 排除包头和校验和
            checksum += txpacket[idx]

        txpacket[total_packet_length - 1] = ~checksum & 0xFF

        # 发送数据包
        self.portHandler.clearPort()
        written_packet_length = self.portHandler.writePort(txpacket)
        if total_packet_length != written_packet_length:
            self.portHandler.is_using = False
            return COMM_TX_FAIL

        return COMM_SUCCESS

    def rxPacket(self):
        """
        接收数据包。
        
        返回:
            tuple: (接收到的数据包列表, 通信结果代码)
        """
        rxpacket = []

        result = COMM_TX_FAIL
        checksum = 0
        rx_length = 0
        wait_length = 6  # 最小长度 (HEADER0 HEADER1 ID LENGTH ERROR CHKSUM)

        while True:
            rxpacket.extend(self.portHandler.readPort(wait_length - rx_length))
            rx_length = len(rxpacket)
            if rx_length >= wait_length:
                # 查找包头
                for idx in range(0, (rx_length - 1)):
                    if (rxpacket[idx] == 0xFF) and (rxpacket[idx + 1] == 0xFF):
                        break

                if idx == 0:  # 在包开头找到包头
                    if (rxpacket[PKT_ID] > 0xFD) or (rxpacket[PKT_LENGTH] > RXPACKET_MAX_LEN) or (
                            rxpacket[PKT_ERROR] > 0x7F):
                        # 无效ID、长度或错误值
                        del rxpacket[0]  # 移除第一个字节
                        rx_length -= 1
                        continue

                    # 重新计算期望的接收包长度
                    if wait_length != (rxpacket[PKT_LENGTH] + PKT_LENGTH + 1):
                        wait_length = rxpacket[PKT_LENGTH] + PKT_LENGTH + 1
                        continue

                    if rx_length < wait_length:
                        # 检查超时
                        if self.portHandler.isPacketTimeout():
                            if rx_length == 0:
                                result = COMM_RX_TIMEOUT
                            else:
                                result = COMM_RX_CORRUPT
                            break
                        else:
                            continue

                    # 计算校验和
                    for i in range(2, wait_length - 1):  # 排除包头和校验和
                        checksum += rxpacket[i]
                    checksum = ~checksum & 0xFF

                    # 验证校验和
                    if rxpacket[wait_length - 1] == checksum:
                        result = COMM_SUCCESS
                    else:
                        result = COMM_RX_CORRUPT
                    break

                else:
                    # 移除不必要的字节
                    del rxpacket[0: idx]
                    rx_length -= idx

            else:
                # 检查超时
                if self.portHandler.isPacketTimeout():
                    if rx_length == 0:
                        result = COMM_RX_TIMEOUT
                    else:
                        result = COMM_RX_CORRUPT
                    break

        self.portHandler.is_using = False
        return rxpacket, result

    def txRxPacket(self, txpacket):
        """
        发送并接收数据包（事务处理）。
        
        参数:
            txpacket: 要发送的数据包列表
            
        返回:
            tuple: (接收到的数据包列表, 通信结果代码, 错误码)
        """
        rxpacket = None
        error = 0

        # 发送数据包
        result = self.txPacket(txpacket)
        if result != COMM_SUCCESS:
            return rxpacket, result, error

        # 如果是广播ID，不需要等待状态包
        if (txpacket[PKT_ID] == BROADCAST_ID):
            self.portHandler.is_using = False
            return rxpacket, result, error

        # 设置包超时时间
        if txpacket[PKT_INSTRUCTION] == INST_READ:
            self.portHandler.setPacketTimeout(txpacket[PKT_PARAMETER0 + 1] + 6)
        else:
            self.portHandler.setPacketTimeout(6)  # HEADER0 HEADER1 ID LENGTH ERROR CHECKSUM

        # 接收数据包
        while True:
            rxpacket, result = self.rxPacket()
            if result != COMM_SUCCESS or txpacket[PKT_ID] == rxpacket[PKT_ID]:
                break

        if result == COMM_SUCCESS and txpacket[PKT_ID] == rxpacket[PKT_ID]:
            error = rxpacket[PKT_ERROR]

        return rxpacket, result, error

    def ping(self, scs_id):
        """
        Ping舵机，获取模型号。
        
        参数:
            scs_id: 舵机ID
            
        返回:
            tuple: (模型号, 通信结果代码, 错误码)
        """
        model_number = 0
        error = 0

        txpacket = [0] * 6

        if scs_id > BROADCAST_ID:
            return model_number, COMM_NOT_AVAILABLE, error

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 2
        txpacket[PKT_INSTRUCTION] = INST_PING

        rxpacket, result, error = self.txRxPacket(txpacket)

        if result == COMM_SUCCESS:
            # 读取模型号（地址3，2字节）
            data_read, result, error = self.readTxRx(scs_id, 3, 2)
            if result == COMM_SUCCESS:
                model_number = self.scs_makeword(data_read[0], data_read[1])

        return model_number, result, error

    def action(self, scs_id):
        """
        执行注册的写入动作（触发REG_WRITE操作）。
        
        参数:
            scs_id: 舵机ID
            
        返回:
            int: 通信结果代码
        """
        txpacket = [0] * 6

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 2
        txpacket[PKT_INSTRUCTION] = INST_ACTION

        _, result, _ = self.txRxPacket(txpacket)

        return result

    def readTx(self, scs_id, address, length):
        """
        发送读取指令（只发送，不接收）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            length: 要读取的数据长度
            
        返回:
            int: 通信结果代码
        """
        txpacket = [0] * 8

        if scs_id > BROADCAST_ID:
            return COMM_NOT_AVAILABLE

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 4
        txpacket[PKT_INSTRUCTION] = INST_READ
        txpacket[PKT_PARAMETER0 + 0] = address
        txpacket[PKT_PARAMETER0 + 1] = length

        result = self.txPacket(txpacket)

        # 设置接收超时
        if result == COMM_SUCCESS:
            self.portHandler.setPacketTimeout(length + 6)

        return result

    def readRx(self, scs_id, length):
        """
        接收读取的数据（在发送读取指令后调用）。
        
        参数:
            scs_id: 舵机ID
            length: 期望的数据长度
            
        返回:
            tuple: (读取的数据列表, 通信结果代码, 错误码)
        """
        result = COMM_TX_FAIL
        error = 0

        rxpacket = None
        data = []

        while True:
            rxpacket, result = self.rxPacket()

            if result != COMM_SUCCESS or rxpacket[PKT_ID] == scs_id:
                break

        if result == COMM_SUCCESS and rxpacket[PKT_ID] == scs_id:
            error = rxpacket[PKT_ERROR]

            data.extend(rxpacket[PKT_PARAMETER0 : PKT_PARAMETER0+length])

        return data, result, error

    def readTxRx(self, scs_id, address, length):
        """
        发送并接收读取指令（完整事务）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            length: 要读取的数据长度
            
        返回:
            tuple: (读取的数据列表, 通信结果代码, 错误码)
        """
        txpacket = [0] * 8
        data = []

        if scs_id > BROADCAST_ID:
            return data, COMM_NOT_AVAILABLE, 0

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 4
        txpacket[PKT_INSTRUCTION] = INST_READ
        txpacket[PKT_PARAMETER0 + 0] = address
        txpacket[PKT_PARAMETER0 + 1] = length

        rxpacket, result, error = self.txRxPacket(txpacket)
        if result == COMM_SUCCESS:
            error = rxpacket[PKT_ERROR]

            data.extend(rxpacket[PKT_PARAMETER0 : PKT_PARAMETER0+length])

        return data, result, error

    def read1ByteTx(self, scs_id, address):
        """
        发送读取1字节指令（只发送）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            
        返回:
            int: 通信结果代码
        """
        return self.readTx(scs_id, address, 1)

    def read1ByteRx(self, scs_id):
        """
        接收1字节数据（在发送读取指令后调用）。
        
        参数:
            scs_id: 舵机ID
            
        返回:
            tuple: (读取的数据, 通信结果代码, 错误码)
        """
        data, result, error = self.readRx(scs_id, 1)
        data_read = data[0] if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read1ByteTxRx(self, scs_id, address):
        """
        发送并接收1字节读取指令（完整事务）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            
        返回:
            tuple: (读取的数据, 通信结果代码, 错误码)
        """
        data, result, error = self.readTxRx(scs_id, address, 1)
        data_read = data[0] if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read2ByteTx(self, scs_id, address):
        """
        发送读取2字节指令（只发送）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            
        返回:
            int: 通信结果代码
        """
        return self.readTx(scs_id, address, 2)

    def read2ByteRx(self, scs_id):
        """
        接收2字节数据（在发送读取指令后调用）。
        
        参数:
            scs_id: 舵机ID
            
        返回:
            tuple: (读取的数据, 通信结果代码, 错误码)
        """
        data, result, error = self.readRx(scs_id, 2)
        data_read = self.scs_makeword(data[0], data[1]) if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read2ByteTxRx(self, scs_id, address):
        """
        发送并接收2字节读取指令（完整事务）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            
        返回:
            tuple: (读取的数据, 通信结果代码, 错误码)
        """
        data, result, error = self.readTxRx(scs_id, address, 2)
        data_read = self.scs_makeword(data[0], data[1]) if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read4ByteTx(self, scs_id, address):
        """
        发送读取4字节指令（只发送）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            
        返回:
            int: 通信结果代码
        """
        return self.readTx(scs_id, address, 4)

    def read4ByteRx(self, scs_id):
        """
        接收4字节数据（在发送读取指令后调用）。
        
        参数:
            scs_id: 舵机ID
            
        返回:
            tuple: (读取的数据, 通信结果代码, 错误码)
        """
        data, result, error = self.readRx(scs_id, 4)
        data_read = self.scs_makedword(self.scs_makeword(data[0], data[1]),
                                  self.scs_makeword(data[2], data[3])) if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read4ByteTxRx(self, scs_id, address):
        """
        发送并接收4字节读取指令（完整事务）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            
        返回:
            tuple: (读取的数据, 通信结果代码, 错误码)
        """
        data, result, error = self.readTxRx(scs_id, address, 4)
        data_read = self.scs_makedword(self.scs_makeword(data[0], data[1]),
                                  self.scs_makeword(data[2], data[3])) if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def writeTxOnly(self, scs_id, address, length, data):
        """
        发送写入指令（只发送，不接收响应）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            length: 数据长度
            data: 要写入的数据列表
            
        返回:
            int: 通信结果代码
        """
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1: PKT_PARAMETER0 + 1 + length] = data[0: length]

        result = self.txPacket(txpacket)
        self.portHandler.is_using = False

        return result

    def writeTxRx(self, scs_id, address, length, data):
        """
        发送写入指令并接收响应。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            length: 数据长度
            data: 要写入的数据列表
            
        返回:
            tuple: (通信结果代码, 错误码)
        """
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1: PKT_PARAMETER0 + 1 + length] = data[0: length]
        rxpacket, result, error = self.txRxPacket(txpacket)

        return result, error

    def write1ByteTxOnly(self, scs_id, address, data):
        """
        发送写入1字节指令（只发送）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            data: 要写入的数据（1字节）
            
        返回:
            int: 通信结果代码
        """
        data_write = [data]
        return self.writeTxOnly(scs_id, address, 1, data_write)

    def write1ByteTxRx(self, scs_id, address, data):
        """
        发送写入1字节指令并接收响应。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            data: 要写入的数据（1字节）
            
        返回:
            tuple: (通信结果代码, 错误码)
        """
        data_write = [data]
        return self.writeTxRx(scs_id, address, 1, data_write)

    def write2ByteTxOnly(self, scs_id, address, data):
        """
        发送写入2字节指令（只发送）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            data: 要写入的数据（2字节）
            
        返回:
            int: 通信结果代码
        """
        data_write = [self.scs_lobyte(data), self.scs_hibyte(data)]
        return self.writeTxOnly(scs_id, address, 2, data_write)

    def write2ByteTxRx(self, scs_id, address, data):
        """
        发送写入2字节指令并接收响应。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            data: 要写入的数据（2字节）
            
        返回:
            tuple: (通信结果代码, 错误码)
        """
        data_write = [self.scs_lobyte(data), self.scs_hibyte(data)]
        return self.writeTxRx(scs_id, address, 2, data_write)

    def write4ByteTxOnly(self, scs_id, address, data):
        """
        发送写入4字节指令（只发送）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            data: 要写入的数据（4字节）
            
        返回:
            int: 通信结果代码
        """
        data_write = [self.scs_lobyte(self.scs_loword(data)),
                      self.scs_hibyte(self.scs_loword(data)),
                      self.scs_lobyte(self.scs_hiword(data)),
                      self.scs_hibyte(self.scs_hiword(data))]
        return self.writeTxOnly(scs_id, address, 4, data_write)

    def write4ByteTxRx(self, scs_id, address, data):
        """
        发送写入4字节指令并接收响应。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            data: 要写入的数据（4字节）
            
        返回:
            tuple: (通信结果代码, 错误码)
        """
        data_write = [self.scs_lobyte(self.scs_loword(data)),
                      self.scs_hibyte(self.scs_loword(data)),
                      self.scs_lobyte(self.scs_hiword(data)),
                      self.scs_hibyte(self.scs_hiword(data))]
        return self.writeTxRx(scs_id, address, 4, data_write)

    def regWriteTxOnly(self, scs_id, address, length, data):
        """
        发送注册写入指令（只发送，不执行，等待ACTION指令触发执行）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            length: 数据长度
            data: 要写入的数据列表
            
        返回:
            int: 通信结果代码
        """
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_REG_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1: PKT_PARAMETER0 + 1 + length] = data[0: length]

        result = self.txPacket(txpacket)
        self.portHandler.is_using = False

        return result

    def regWriteTxRx(self, scs_id, address, length, data):
        """
        发送注册写入指令并接收响应（不执行，等待ACTION指令触发执行）。
        
        参数:
            scs_id: 舵机ID
            address: 内存地址
            length: 数据长度
            data: 要写入的数据列表
            
        返回:
            tuple: (通信结果代码, 错误码)
        """
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_REG_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1: PKT_PARAMETER0 + 1 + length] = data[0: length]

        _, result, error = self.txRxPacket(txpacket)

        return result, error

    def syncReadTx(self, start_address, data_length, param, param_length):
        """
        发送同步读取指令（只发送）。
        
        参数:
            start_address: 起始内存地址
            data_length: 每个舵机要读取的数据长度
            param: 舵机ID列表
            param_length: 舵机数量
            
        返回:
            int: 通信结果代码
        """
        txpacket = [0] * (param_length + 8)
        # 8: HEADER0 HEADER1 ID LEN INST START_ADDR DATA_LEN CHKSUM

        txpacket[PKT_ID] = BROADCAST_ID
        txpacket[PKT_LENGTH] = param_length + 4  # 7: INST START_ADDR DATA_LEN CHKSUM
        txpacket[PKT_INSTRUCTION] = INST_SYNC_READ
        txpacket[PKT_PARAMETER0 + 0] = start_address
        txpacket[PKT_PARAMETER0 + 1] = data_length

        txpacket[PKT_PARAMETER0 + 2: PKT_PARAMETER0 + 2 + param_length] = param[0: param_length]

        # print(txpacket)
        result = self.txPacket(txpacket)
        return result

    def syncReadRx(self, data_length, param_length):
        """
        接收同步读取的数据。
        
        参数:
            data_length: 每个舵机的数据长度
            param_length: 舵机数量
            
        返回:
            tuple: (通信结果代码, 接收到的数据包)
        """
        wait_length = (6 + data_length) * param_length
        self.portHandler.setPacketTimeout(wait_length)
        rxpacket = []
        rx_length = 0
        while True:
            rxpacket.extend(self.portHandler.readPort(wait_length - rx_length))
            rx_length = len(rxpacket)
            if rx_length >= wait_length:
                result = COMM_SUCCESS
                break
            else:
                # 检查超时
                if self.portHandler.isPacketTimeout():
                    if rx_length == 0:
                        result = COMM_RX_TIMEOUT
                    else:
                        result = COMM_RX_CORRUPT
                    break
        self.portHandler.is_using = False
        return result, rxpacket

    def syncWriteTxOnly(self, start_address, data_length, param, param_length):
        """
        发送同步写入指令（只发送，不接收响应）。
        
        参数:
            start_address: 起始内存地址
            data_length: 每个舵机的数据长度
            param: 参数数据（包含舵机ID和对应数据）
            param_length: 参数数据总长度
            
        返回:
            int: 通信结果代码
        """
        txpacket = [0] * (param_length + 8)
        # 8: HEADER0 HEADER1 ID LEN INST START_ADDR DATA_LEN ... CHKSUM

        txpacket[PKT_ID] = BROADCAST_ID
        txpacket[PKT_LENGTH] = param_length + 4  # 4: INST START_ADDR DATA_LEN ... CHKSUM
        txpacket[PKT_INSTRUCTION] = INST_SYNC_WRITE
        txpacket[PKT_PARAMETER0 + 0] = start_address
        txpacket[PKT_PARAMETER0 + 1] = data_length

        txpacket[PKT_PARAMETER0 + 2: PKT_PARAMETER0 + 2 + param_length] = param[0: param_length]

        _, result, _ = self.txRxPacket(txpacket)

        return result

    def reOfsCal(self, scs_id, position):
        """
        执行舵机偏移校准。
        
        参数:
            scs_id: 舵机ID
            position: 校准位置值
            
        返回:
            tuple: (通信结果代码, 错误码)
        """
        error = 0

        txpacket = [0] * 8

        if scs_id > BROADCAST_ID:
            return COMM_NOT_AVAILABLE, error

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 4
        txpacket[PKT_INSTRUCTION] = INST_OFSCAL
        txpacket[PKT_PARAMETER0] = self.scs_lobyte(position)
        txpacket[PKT_PARAMETER0+1] = self.scs_hibyte(position)

        rxpacket, result, error = self.txRxPacket(txpacket)

        return result, error

    def reSet(self, scs_id):
        """
        执行舵机重置（清除圈数等状态信息）。
        
        参数:
            scs_id: 舵机ID
            
        返回:
            tuple: (通信结果代码, 错误码)
        """
        error = 0

        txpacket = [0] * 6

        if scs_id > BROADCAST_ID:
            return COMM_NOT_AVAILABLE, error

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 2
        txpacket[PKT_INSTRUCTION] = INST_RESET

        rxpacket, result, error = self.txRxPacket(txpacket)

        return result, error
