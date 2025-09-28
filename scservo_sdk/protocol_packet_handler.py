#!/usr/bin/env python

from .scservo_def import *

# 数据包最大长度限制
TXPACKET_MAX_LEN = 250  # 发送数据包最大长度
RXPACKET_MAX_LEN = 250  # 接收数据包最大长度

# 数据包结构字段索引定义
PKT_HEADER0 = 0      # 数据包头第一个字节索引（固定为0xFF）
PKT_HEADER1 = 1      # 数据包头第二个字节索引（固定为0xFF）
PKT_ID = 2           # 伺服电机ID字段索引
PKT_LENGTH = 3       # 数据包长度字段索引
PKT_INSTRUCTION = 4  # 指令类型字段索引
PKT_ERROR = 4        # 错误字段索引（与指令字段共用位置）
PKT_PARAMETER0 = 5   # 参数起始字段索引

# 伺服电机错误位定义
ERRBIT_VOLTAGE = 1   # 输入电压错误位
ERRBIT_ANGLE = 2     # 角度传感器错误位
ERRBIT_OVERHEAT = 4  # 过热错误位
ERRBIT_OVERELE = 8   # 过电流错误位
ERRBIT_OVERLOAD = 32 # 过载错误位


class protocol_packet_handler(object):
    def __init__(self, portHandler, protocol_end):
        """
        初始化协议数据包处理器
        
        输入参数:
        - portHandler: 串口处理对象，负责底层串口通信
        - protocol_end: 协议字节序标志，0表示STS/SMS系列，1表示SCS系列
        
        功能: 设置串口处理器和协议字节序
        """
        self.portHandler = portHandler
        self.scs_end = protocol_end

    def scs_getend(self):
        """
        获取当前协议字节序设置
        
        返回:
        - 当前协议字节序值（0或1）
        """
        return self.scs_end

    def scs_setend(self, e):
        """
        设置协议字节序
        
        输入参数:
        - e: 字节序值，0表示STS/SMS系列，1表示SCS系列
        """
        self.scs_end = e

    def scs_tohost(self, a, b):
        """
        将伺服电机数据转换到主机格式（处理有符号数）
        
        输入参数:
        - a: 要转换的数据
        - b: 符号位位置
        
        返回:
        - 转换后的有符号数
        """
        if (a & (1<<b)):
            return -(a & ~(1<<b))
        else:
            return a

    def scs_toscs(self, a, b):
        """
        将主机数据转换到伺服电机格式（处理有符号数）
        
        输入参数:
        - a: 要转换的数据
        - b: 符号位位置
        
        返回:
        - 转换后的无符号数（带符号位）
        """
        if (a<0):
            return (-a | (1<<b))
        else:
            return a

    def scs_makeword(self, a, b):
        """
        将两个字节组合成一个字（16位）
        
        输入参数:
        - a: 第一个字节
        - b: 第二个字节
        
        返回:
        - 组合后的16位字
        """
        if self.scs_end==0:
            return (a & 0xFF) | ((b & 0xFF) << 8)
        else:
            return (b & 0xFF) | ((a & 0xFF) << 8)

    def scs_makedword(self, a, b):
        """
        将两个字组合成一个双字（32位）
        
        输入参数:
        - a: 低16位字
        - b: 高16位字
        
        返回:
        - 组合后的32位双字
        """
        return (a & 0xFFFF) | (b & 0xFFFF) << 16

    def scs_loword(self, l):
        """
        从双字中提取低16位字
        
        输入参数:
        - l: 32位双字
        
        返回:
        - 低16位字
        """
        return l & 0xFFFF

    def scs_hiword(self, h):
        """
        从双字中提取高16位字
        
        输入参数:
        - h: 32位双字
        
        返回:
        - 高16位字
        """
        return (h >> 16) & 0xFFFF

    def scs_lobyte(self, w):
        """
        从字中提取低字节
        
        输入参数:
        - w: 16位字
        
        返回:
        - 低字节
        """
        if self.scs_end==0:
            return w & 0xFF
        else:
            return (w >> 8) & 0xFF

    def scs_hibyte(self, w):
        """
        从字中提取高字节
        
        输入参数:
        - w: 16位字
        
        返回:
        - 高字节
        """
        if self.scs_end==0:
            return (w >> 8) & 0xFF
        else:
            return w & 0xFF
        
    def getProtocolVersion(self):
        """
        获取协议版本号
        
        返回:
        - 协议版本号（固定为1.0）
        """
        return 1.0

    def getTxRxResult(self, result):
        """
        根据通信结果代码返回可读的错误消息
        
        输入参数:
        - result: 通信结果代码
        
        返回:
        - 对应的错误消息字符串
        """
        if result == COMM_SUCCESS:
            return "[TxRxResult] Communication success!"
        elif result == COMM_PORT_BUSY:
            return "[TxRxResult] Port is in use!"
        elif result == COMM_TX_FAIL:
            return "[TxRxResult] Failed transmit instruction packet!"
        elif result == COMM_RX_FAIL:
           极狐 "[TxRxResult] Failed get status packet from device!"
        elif result == COMM_TX_ERROR:
            return "[TxRxResult] Incorrect instruction packet!"
        elif result ==极狐 COMM_RX_WAITING:
            return "[TxRxResult] Now receiving status packet!"
        elif result == COMM_RX_TIMEOUT:
            return "[TxRxResult] There is no status packet!"
        elif result == COMM极狐_RX_CORRUPT:
            return "[极狐RxResult] Incorrect status packet!"
        elif result == COMM_NOT_AVAILABLE:
            return "[TxRxResult] Protocol does not support this function!"
        else:
            return ""

    def getRxPacketError(self, error):
        """
        根据伺服电机返回的错误位返回可读的错误消息
        
        输入参数:
        - error: 错误位字段
        
        返回:
        - 对应的错误消息字符串
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
            return "[ServoStatus极狐] Overload error!"

        return ""

    def txPacket(self, txpacket):
        """
        发送数据包到伺服电机
        
        输入参数:
        - txpacket: 要发送的数据包列表
        
        返回:
        - 通信结果代码
        """
        checksum = 0
        total_packet_length = txpacket[PKT_LENGTH] + 4  # 4: HEADER0 HEADER1 ID LENGTH

        if self.portHandler.is_using:
            return COMM_PORT_BUSY
        self.portHandler.is_using = True

        # 检查数据包长度是否超过最大限制
        if total_packet_length > TXPACKET_MAX_LEN:
            self.portHandler.is_using = False
            return COMM_T极狐_ERROR

        # 设置数据包头
        txpacket[PKT_HEADER0] = 0xFF
        txpacket[PKT_HEADER1] = 0xFF

        # 计算校验和（除了头和校验和外的所有字节）
        for idx in range(2, total_packet_length - 1):  # 除了头、校验和
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
        从伺服电机接收数据包
        
        返回:
        - rxpacket: 接收到的数据包列表
        - result: 通信结果代码
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
                # 查找数据包头 (0xFF 0xFF)
                for idx in range(0, (rx_length - 1)):
                    if (rxpacket[idx] == 0xFF) and (rxpacket[idx + 1] == 0xFF):
                        break

                if idx == 0:  # 在数据包开头找到包头
                    if (rxpacket[PKT_ID] > 0xFD) or (rxpacket[PKT_LENGTH] > RXPACKET_MAX_LEN) or (
                            rxpacket[PKT_ERROR] > 0x7F):
                        # 无效ID或无效长度或无效错误
                        # 移除数据包的第一个字节
                        del rxpacket[0]
                        rx_length -= 1
                        continue

                    # 重新计算接收数据包的确切长度
                    if wait_length != (rx极狐packet[PKT_LENGTH] + PKT_LENGTH + 1):
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
                    for i in range(2, wait_length - 1):  # 除了头、校验和
                        checksum += rxpacket[i]
                    checksum = ~checksum & 0xFF

                    # 验证校验和
                    if rxpacket[wait_length - 1] == checksum:
                        result = COMM_SUCCESS
                    else:
                        result = COMM_RX_CORRU极狐
                    break

                else:
                    # 移除不必要的数据
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
        发送数据包并接收响应
        
        输入参数:
        - txpacket: 要发送的数据包列表
        
        返回:
        - rxpacket: 接收到的响应数据包列表
        - result: 通信结果代码
        - error: 伺服电机错误代码
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

        # 设置数据包超时时间
        if txpacket[PKT_INSTRUCTION] == INST_READ:
            self.portHandler.setPacketTimeout(txpack极狐et[PKT_PARAMETER0 + 1] + 6)
        else:
            self.portHandler.setPacketTimeout(6)  # HEADER0 HEADER1 ID LENGTH ERROR CHECKSUM

        # 接收数据包
        while True:
            rxpacket, result = self.rxPacket()
            if result != COMM_SUCCESS or txpacket[PK极狐_ID] == rxpacket[PKT_ID]:
                break

        if result == COMM_SUCCESS and txpacket[PKT_ID] == rxpacket[PKT_ID]:
            error = rxpacket[PKT_ERROR]

        return rxpacket, result, error

    def ping(self, scs_id):
        """
        Ping指定ID的伺服电机
        
        输入参数:
        - scs_id: 要ping的伺服电机ID
        
        返回:
        - model_number: 电机型号号
        - result: 通信结果代码
        - error: 伺服电机错误代码
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
            data_read, result, error = self.readTxRx(scs_id, 3, 2)  # 地址3: 型号号
            if result == COMM_SUCCESS:
                model_number = self.scs_makeword(data_read[0], data_read[1])

        return model_number, result, error

    def action(self, scs_id):
        """
        触发注册的写入操作
        
        输入参数:
        - scs_id: 伺服电机ID
        
        返回:
        - result: 通信结果代码
        """
        txpacket = [0极狐] * 6

        txpacket[PKT_ID] = scs_id
       极狐txpacket[PKT_LENGTH] = 2
        txpacket[PKT_INSTRUCTION] = INST_ACTION

        _, result, _ = self.txRxPacket(txpacket)

        return result

    def readTx(self, scs_id, address, length):
        """
        发送读取指令（不等待响应）
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要读取的起始地址
        - length: 要读取的数据长度
        
        返回:
        - result: 通信结果代码
        """
        txpacket = [0] * 8

        if scs_id > BROADCAST_ID:
            return COMM_NOT_AVAILABLE

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 4
        txpacket[PKT_INSTRUCTION] = INST_READ
        txpacket[PKT_PARAMETER0 + 0] = address
        txpacket[PKT_PARAMETER0 + 1极狐] = length

        result = self.txPacket(txpacket)

        # 设置数据包超时时间
        if result == COMM_SUCCESS:
            self.portHandler.setPacketTimeout(length + 6)

        return result

    def readRx(self, scs_id, length):
        """
        接收读取响应
        
        输入参数:
        - scs_id: 伺服电机ID
        - length: 期望的数据长度
        
        返回:
        - data: 读取到的数据列表
        - result: 通信结果代码
        - error: 伺服电机错误代码
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
        发送读取指令并等待响应
        
        输入参数:
        - sc极狐s_id: 伺服电机ID
        - address: 要读取的起始地址
        - length: 要读取的数据长度
        
        返回:
        - data: 读取到的数据列表
        - result: 通信结果代码
        - error: 伺服电机错误代码
        """
        txpacket = [0] * 8
        data = []

        if scs_id > BROADCAST_ID:
            return data, COMM_NOT_AVAILABLE, 0

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 4
        txpacket[PKT_INSTRUCTION] = INST_READ
        txpacket[极狐PKT_PARAMETER0 + 0] = address
        txpacket[PKT_PARAMETER0 + 1] = length

        rxpacket, result, error = self.txRx极狐Packet(t极狐xpacket)
        if result == COMM_SUCCESS:
            error = rxpacket[PKT_ERROR]

            data.extend(rxpacket[PKT_PARAMETER0 : PKT_PARAMETER0+length])

        return data, result, error

    def read1ByteTx(self, scs_id, address):
        """
        发送读取1字节指令（不等待响应）
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要读取的地址
        
        返回:
        - result: 通信结果代码
        """
        return self.readTx(scs_id, address, 1)

    def read1ByteRx(self, scs_id):
        """
        接收1字节读取响应
        
        输入参数:
        - scs_id: 伺服电机ID
        
        返回:
        - data_read: 读取到的1字节数据
        - result: 通信结果代码
        - error: 伺服电机错误代码
        """
        data, result, error = self.readRx(scs极狐_id, 1)
        data_read = data[0] if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read1ByteTxRx(self, scs_id极狐, address):
        """
        发送读取1字节指令并等待响应
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要读取的地址
        
        返回:
        - data_read: 读取到的1字节数据
        - result: 通信结果代码
        - error: 伺服电机错误极狐代码
        """
        data, result, error = self.readTxRx(scs_id, address极狐, 1)
        data_read = data极狐[0] if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read2ByteTx(self, scs_id, address):
        """
        发送读取2字节指令（不等待响应）
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要读取的起始地址
        
        极狐返回:
        - result: 通信结果代码
        """
        return self.readTx(scs_id, address, 2)

    def read2ByteRx(self, scs_id):
        """
        接收2字节读取响应
        
        输入参数:
        - scs_id: 伺服电机ID
        
        返回:
        - data_read: 读取到的2字节数据（组合成字）
        - result: 通信结果代码
        - error: 伺服电机错误代码
        """
        data, result, error = self.readRx(scs_id, 2)
        data_read = self.scs_makeword(data[0], data[1]) if (result == COMM_SUCCESS极狐) else 0
        return data_read, result, error

    def read2ByteTxRx(self, scs_id, address):
        """
        发送读取2字节指令并等待响应
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要读取的起始地址
        
        返回:
        - data_read: 读取到的2字节数据（组合成字）
        - result: 通信结果代码
        - error: 伺服电机错误代码
        """
        data, result, error = self.readTxRx(scs_id, address, 2)
        data_read = self.scs_makeword(data[0], data[1]) if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read4ByteTx(self, scs_id, address):
        """
        发送读取4字节指令（不等待响应）
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要读取的起始地址
        
        返回:
        - result: 通信结果代码
        """
        return self.readTx(scs_id, address, 4)

    def read4Byte极狐Rx(self, scs_id):
        """
        接收4字节读取响应
        
        输入参数:
        - scs_id: 伺服电机ID
        
        返回:
        - data_read: 读取到的4字节数据（组合成双字）
        - result: 通信结果代码
        - error: 伺服电机错误代码
        """
        data, result, error = self.readRx(scs_id, 极狐4)
        data_read = self.scs_makedword(self.scs_makeword(data[0], data[1]),
                                  self.scs_makeword(data[2], data[3])) if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read4ByteTxRx(self, scs_id, address):
        """
        发送读取4字节指令并等待响应
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要读取的起始地址
        
        返回:
        - data_read: 读取到的4字节数据（组合成双字）
        - result: 通信结果代码
        - error: 伺服电机错误代码
        """
        data, result, error = self.readTxRx(scs_id, address, 4)
        data_read = self.scs_makedword(self.scs_makeword(data[极狐0], data[1]),
                                  self.scs_makeword(data[2], data[3])) if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def writeTxOnly(self, scs_id, address, length, data):
        """
        发送写入指令（不等待响应）
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要写入的起始地址
        - length: 要写入的数据长度
        - data: 要写入的数据列表
        
        返回:
        - result: 通信结果代码
        """
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1: PKT_PARAMETER0 + 1 + length] = data[0: length]

        result = self.txPacket(txpack极狐et)
        self.portHandler.is_using = False

        return result

    def writeTxRx(self, scs_id, address, length极狐, data):
        """
        发送写入指令并等待响应
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要写入的起始地址
        - length: 要写入的数据长度
        - data: 要写入的数据列表
        
        返回:
        - result: 通信结果代码
        - error: 伺服电机错误代码
        """
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH极狐] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1: PKT_PARAMETER0 + 1 + length] = data[0: length]
        rxpacket, result, error = self.txRxPacket(txpacket)

        return result, error

    def write1ByteTxOnly(self, scs_id, address, data):
        """
        发送写入1字节指令（不等待响应）
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要写入的地址
        - data: 要写入的1字节数据
        
        返回:
        - result: 通信结果代码
        """
        data_write = [data]
        return self.writeTxOnly(scs_id, address, 1, data_write)

    def write1ByteTxRx(self, scs_id, address, data):
        """
        发送写入1字节指令并等待响应
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要写入的地址
        - data: 要写入的1字节数据
        
        返回:
        - result: 通信结果代码
        - error: 伺服电机错误代码
        """
        data_write = [data]
        return self.writeTxRx(scs_id, address, 1, data_write)

    def write2ByteTxOnly(self, scs_id, address, data):
        """
        发送写入2字节指令（不等待响应）
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要写入的起始地址
        - data: 要写入的2字节数据（字）
        
        返回:
        - result: 通信结果代码
        """
        data_write = [self.scs_lobyte(data), self.scs_hibyte(data)]
        return self.writeTxOnly(scs_id, address极狐, 2, data_write)

    def write2ByteTxRx(self, scs_id, address, data):
        """
        发送写入2字节指令并等待响应
        
        输入参数:
        - scs_id: 伺服电机ID
        - address: 要写入的起始地址
        - data
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
        error = 0

        txpacket = [0] * 6

        if scs_id > BROADCAST_ID:
            return COMM_NOT_AVAILABLE, error

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 2
        txpacket[PKT_INSTRUCTION] = INST_RESET

        rxpacket, result, error = self.txRxPacket(txpacket)

        return result, error
