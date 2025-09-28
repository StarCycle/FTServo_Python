#!/usr/bin/env python

from .scservo_def import *

class GroupSyncWrite:
    def __init__(self, ph, start_address, data_length):
        """
        初始化同步写入组对象
        输入参数:
            ph - 协议包处理器对象
            start_address - 起始内存地址
            data_length - 数据长度
        功能: 创建同步写入组，用于同时向多个舵机写入数据
        """
        self.ph = ph  # 协议包处理器
        self.start_address = start_address  # 起始内存地址
        self.data_length = data_length  # 数据长度

        self.is_param_changed = False  # 参数是否改变标志
        self.param = []  # 参数列表
        self.data_dict = {}  # 数据字典，存储舵机ID和对应数据

        self.clearParam()  # 初始化时清空参数

    def makeParam(self):
        """
        生成参数列表
        输入参数: 无
        输出: 无
        功能: 根据数据字典中的舵机ID和数据生成参数列表
        """
        if not self.data_dict:  # 如果数据字典为空
            return

        self.param = []  # 清空参数列表

        for scs_id in self.data_dict:
            if not self.data_dict[scs_id]:  # 如果舵机数据为空
                return  # 直接返回

            self.param.append(scs_id)  # 添加舵机ID到参数列表
            self.param.extend(self.data_dict[scs_id])  # 添加舵机数据到参数列表

    def addParam(self, scs_id, data):
        """
        添加舵机参数和数据
        输入参数:
            scs_id - 舵机ID
            data - 要写入的数据列表
        输出: 布尔值，表示是否成功添加
        功能: 将指定舵机ID和对应数据添加到同步写入组中
        """
        if scs_id in self.data_dict:  # 如果舵机ID已存在
            return False  # 添加失败

        if len(data) > self.data_length:  # 如果数据长度超过设置值
            return False  # 添加失败

        self.data_dict[scs_id] = data  # 存储舵机数据
        self.is_param_changed = True  # 标记参数已改变
        return True  # 添加成功

    def removeParam(self, scs_id):
        """
        移除舵机参数
        输入参数: scs_id - 舵机ID
        输出: 无
        功能: 从同步写入组中移除指定舵机ID及其数据
        """
        if scs_id not in self.data_dict:  # 如果舵机ID不存在
            return  # 直接返回

        del self.data_dict[scs_id]  # 从数据字典中删除舵机ID
        self.is_param_changed = True  # 标记参数已改变

    def changeParam(self, scs_id, data):
        """
        修改舵机参数和数据
        输入参数:
            scs_id - 舵机ID
            data - 新的数据列表
        输出: 布尔值，表示是否成功修改
        功能: 修改指定舵机ID的写入数据
        """
        if scs_id not in self.data_dict:  # 如果舵机ID不存在
            return False  # 修改失败

        if len(data) > self.data_length:  # 如果数据长度超过设置值
            return False  # 修改失败

        self.data_dict[scs_id] = data  # 更新舵机数据
        self.is_param_changed = True  # 标记参数已改变
        return True  # 修改成功

    def clearParam(self):
        """
        清空所有参数
        输入参数: 无
        输出: 无
        功能: 清空同步写入组中的所有舵机参数和数据
        """
        self.data_dict.clear()  # 清空数据字典

    def txPacket(self):
        """
        发送同步写入数据包
        输入参数: 无
        输出: 通信结果代码
        功能: 发送同步写入指令到所有已添加的舵机
        """
        if len(self.data_dict.keys()) == 0:  # 如果没有添加任何舵机
            return COMM_NOT_AVAILABLE  # 返回不可用状态

        if self.is_param_changed is True or not self.param:  # 如果参数已改变或参数列表为空
            self.makeParam()  # 重新生成参数列表

        # 调用协议处理器的同步写入发送方法
        return self.ph.syncWriteTxOnly(
            self.start_address, 
            self.data_length, 
            self.param,
            len(self.data_dict.keys()) * (1 + self.data_length)  # 计算总参数长度
        )
