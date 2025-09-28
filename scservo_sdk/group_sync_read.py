#!/usr/bin/env python

from .scservo_def import *

class GroupSyncRead:
    def __init__(self, ph, start_address, data_length):
        """
        初始化同步读取组对象
        输入参数:
            ph - 协议包处理器对象
            start_address - 起始内存地址
            data_length - 数据长度
        功能: 创建同步读取组，用于同时读取多个舵机的数据
        """
        self.ph = ph
        self.start_address = start_address
        self.data_length = data_length

        self.last_result = False  # 上一次操作结果
        self.is_param_changed = False  # 参数是否改变标志
        self.param = []  # 参数列表
        self.data_dict = {}  # 数据字典，存储舵机ID和对应数据

        self.clearParam()  # 初始化时清空参数

    def makeParam(self):
        """
        生成参数列表
        输入参数: 无
        输出: 无
        功能: 根据数据字典中的舵机ID生成参数列表
        """
        if not self.data_dict:  # 如果数据字典为空
            return

        self.param = []  # 清空参数列表

        for scs_id in self.data_dict:
            self.param.append(scs_id)  # 将舵机ID添加到参数列表

    def addParam(self, scs_id):
        """
        添加舵机参数
        输入参数: scs_id - 舵机ID
        输出: 布尔值，表示是否成功添加
        功能: 将指定舵机ID添加到同步读取组中
        """
        if scs_id in self.data_dict:  # 如果舵机ID已存在
            return False  # 添加失败

        self.data_dict[scs_id] = []  # 为舵机ID创建空数据列表
        self.is_param_changed = True  # 标记参数已改变
        return True  # 添加成功

    def removeParam(self, scs_id):
        """
        移除舵机参数
        输入参数: scs_id - 舵机ID
        输出: 无
        功能: 从同步读取组中移除指定舵机ID
        """
        if scs_id not in self.data_dict:  # 如果舵机ID不存在
            return  # 直接返回

        del self.data_dict[scs_id]  # 从数据字典中删除舵机ID
        self.is_param_changed = True  # 标记参数已改变

    def clearParam(self):
        """
        清空所有参数
        输入参数: 无
        输出: 无
        功能: 清空同步读取组中的所有舵机参数
        """
        self.data_dict.clear()  # 清空数据字典

    def txPacket(self):
        """
        发送同步读取数据包
        输入参数: 无
        输出: 通信结果代码
        功能: 发送同步读取指令到所有已添加的舵机
        """
        if len(self.data_dict.keys()) == 0:  # 如果没有添加任何舵机
            return COMM_NOT_AVAILABLE  # 返回不可用状态

        if self.is_param_changed is True or not self.param:  # 如果参数已改变或参数列表为空
            self.makeParam()  # 重新生成参数列表

        # 调用协议处理器的同步读取发送方法
        return self.ph.syncReadTx(self.start_address, self.data_length, self.param, len(self.data_dict.keys()))

    def rxPacket(self):
        """
        接收同步读取响应数据包
        输入参数: 无
        输出: 通信结果代码
        功能: 接收并解析所有舵机的响应数据
        """
        self.last_result = True  # 初始化结果为成功

        result = COMM_RX_FAIL  # 默认接收失败

        if len(self.data_dict.keys()) == 0:  # 如果没有添加任何舵机
            return COMM_NOT_AVAILABLE  # 返回不可用状态

        # 调用协议处理器的同步读取接收方法
        result, rxpacket = self.ph.syncReadRx(self.data_length, len(self.data_dict.keys()))
        
        if len(rxpacket) >= (self.data_length+6):  # 检查响应包长度是否足够
            for scs_id in self.data_dict:  # 遍历所有舵机ID
                # 解析每个舵机的响应数据
                self.data_dict[scs_id], result = self.readRx(rxpacket, scs_id, self.data_length)
                if result != COMM_SUCCESS:  # 如果解析失败
                    self.last_result = False  # 标记整体结果为失败
        else:
            self.last_result = False  # 响应包长度不足，标记为失败
            
        return result  # 返回通信结果

    def txRxPacket(self):
        """
        发送并接收同步读取数据包
        输入参数: 无
        输出: 通信结果代码
        功能: 发送同步读取指令并接收响应，完成完整的同步读取操作
        """
        result = self.txPacket()  # 先发送数据包
        if result != COMM_SUCCESS:  # 如果发送失败
            return result  # 直接返回错误

        return self.rxPacket()  # 接收并返回结果

    def readRx(self, rxpacket, scs_id, data_length):
        """
        解析单个舵机的响应数据
        输入参数:
            rxpacket - 响应数据包
            scs_id - 舵机ID
            data_length - 数据长度
        输出: (数据列表, 通信结果) 元组
        功能: 从响应数据包中提取指定舵机的数据
        """
        data = []  # 初始化数据列表
        rx_length = len(rxpacket)  # 响应包长度
        rx_index = 0  # 响应包索引
        
        while (rx_index+6+data_length) <= rx_length:  # 确保有足够的数据可解析
            headpacket = [0x00, 0x00, 0x00]  # 初始化包头检测缓冲区
            
            # 查找包头(0xFF 0xFF ID)
            while rx_index < rx_length:
                headpacket[2] = headpacket[1]
                headpacket[1] = headpacket[0]
                headpacket[0] = rxpacket[rx_index]
                rx_index += 1
                if (headpacket[2] == 0xFF) and (headpacket[1] == 0xFF) and headpacket[0] == scs_id:
                    break  # 找到包头
            
            if (rx_index+3+data_length) > rx_length:  # 检查数据长度是否足够
                break
                
            if rxpacket[rx_index] != (data_length+2):  # 检查长度字段是否正确
                rx_index += 1
                continue  # 长度不匹配，继续查找
                
            rx_index += 1  # 跳过长度字段
            Error = rxpacket[rx_index]  # 读取错误字段
            rx_index += 1  # 跳过错误字段
            
            # 计算校验和
            calSum = scs_id + (data_length+2) + Error
            data = [Error]  # 将错误码添加到数据列表
            
            # 提取数据部分
            data.extend(rxpacket[rx_index : rx_index+data_length])
            
            # 计算数据部分的校验和
            for i in range(0, data_length):
                calSum += rxpacket[rx_index]
                rx_index += 1
                
            calSum = ~calSum & 0xFF  # 取反并截断为8位
            
            if calSum != rxpacket[rx_index]:  # 校验和验证
                return None, COMM_RX_CORRUPT  # 校验失败，返回数据损坏
                
            return data, COMM_SUCCESS  # 解析成功，返回数据和成功状态
            
        return None, COMM_RX_CORRUPT  # 未找到有效数据，返回数据损坏

    def isAvailable(self, scs_id, address, data_length):
        """
        检查指定舵机的数据是否可用
        输入参数:
            scs_id - 舵机ID
            address - 内存地址
            data_length - 数据长度
        输出: (是否可用, 错误代码) 元组
        功能: 检查指定舵机的数据是否已成功读取且地址有效
        """
        if scs_id not in self.data_dict:  # 如果舵机ID不存在
            return False, 0
            
        # 检查地址是否在有效范围内
        if (address < self.start_address) or (self.start_address + self.data_length - data_length < address):
            return False, 0
            
        if not self.data_dict[scs_id]:  # 如果数据为空
            return False, 0
            
        if len(self.data_dict[scs_id]) < (data_length+1):  # 如果数据长度不足
            return False, 0
            
        return True, self.data_dict[scs_id][0]  # 数据可用，返回True和错误码

    def getData(self, scs_id, address, data_length):
        """
        获取指定舵机的数据
        输入参数:
            scs_id - 舵机ID
            address - 内存地址
            data_length - 数据长度
        输出: 数据值
        功能: 从已读取的数据中提取指定地址的数据
        """
        if data_length == 1:  # 1字节数据
            return self.data_dict[scs_id][address-self.start_address+1]
        elif data_length == 2:  # 2字节数据
            return self.ph.scs_makeword(
                self.data_dict[scs_id][address-self.start_address+1],
                self.data_dict[scs_id][address-self.start_address+2])
        elif data_length == 4:  # 4字节数据
            return self.ph.scs_makedword(
                self.ph.scs_makeword(
                    self.data_dict[scs_id][address-self.start_address+1],
                    self.data_dict[scs_id][address-self.start_address+2]),
                self.ph.scs_makeword(
                    self.data_dict[scs_id][address-self.start_address+3],
                    self.data_dict[scs_id][address-self.start_address+4]))
        else:  # 不支持的数据长度
            return 0
