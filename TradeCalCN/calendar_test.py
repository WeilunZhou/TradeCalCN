#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  7 18:10:48 2023

@author: zhouweilun
"""

import pandas as pd 
import numpy as np 
import datetime as dt 
import baostock as bs 

class Cal():
    def __init__(self, sd, ed):
        '''
        Parameters
        ----------
        sd : datetime.date
            起始日期，可以不是交易日
        ed : TYPE
            终点日期，可以不是交易日
        Returns
        -------
        self.ddays:从baostock官网获得交易日序列然后转为存放datetime.date的数组，方便后续函数操作
        '''
        # 从baostock 官网获得交易日序列然后转为存放datetime.date的数组，方便后续函数操作
        bs.login()
        rs = bs.query_trade_dates(start_date=sd.strftime('%Y-%m-%d'), end_date=ed.strftime('%Y-%m-%d'))
        dates = rs.get_data()
        
        ddays = dates[dates['is_trading_day']=='1']['calendar_date'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').date()).values
        self.ddays = ddays
        
    def get_tdc(self, td, ct):
        '''
        函数:给定一个日期td，和间隔日ct，得到d向前的第ct个交易日，如果ct<0则得到d向后的第|ct|个交易日
        Parameters
        ----------
        td : datetime.date
            日期，可以是交易日或者非交易日，注意 ct = 0 时, 如果是td是交易日则返回td，如果td不是交易日则返回 get_td(td, 1)
        ct : int
            时间间隔，可以为正或为负
        注意: 如果td +/- ct的目标交易日超过日历交易日总长度，则报错
        Returns
        -------
        TYPE: datetime.date
        所求日期
        '''
        ddays = self.ddays
        if ct > 0:
            vds = ddays[ddays > td]
            return vds[ct - 1]
            
        elif ct < 0:
            vds = ddays[ddays < td]
            return vds[ct]
        
        else:
            if td in ddays:
                return td
            else:
                return self.get_tdc(td, 1)
    
    def get_head_tail_td(self, td, freq, dire=None):
        '''
        函数:用来获取日期td所在周/月的第一个和最后一个交易日
        Parameters
        ----------
        td : datetime.date()
            日期
        freq : str
            freq = 'w'代表根据所在周判断，freq = 'm'代表根据所在月判断
        dire: str
            默认None，代表返回(head, tail)，否则dire = h/t 代表单独返回 head / tail
    
        Returns
        -------
        datetime.date
            返回所求日期
        '''
        get_tdc = self.get_tdc 
        if freq == 'w':
            # 获取 td 所在是周几， 0-6分别代表周一-周日
            wd = td.weekday()
            
            if wd >= 5: 
                tail = get_tdc(td, -1)
                head = get_tdc(tail, -4)
            
            else:
                head = get_tdc(td, -wd)
                tail = get_tdc(td, 4-wd)
                
        elif freq == 'm':
            # 获取 td 所在年份和月份
            y, m = td.year, td.month
            head = get_tdc(dt.date(y, m, 1), 0)
            
            if m < 12:
                tail = get_tdc(dt.date(y, m+1, 1),-1)
            else:
                tail = get_tdc(dt.date(y+1, 1, 1),-1)
            
        # 根据dire选择返回哪个值
        if dire == 'h':
            return head 
        
        elif dire == 't':
            return tail
        
        elif dire == None:
            return (head, tail)
    
    
    def get_td_ymw(self, year, month=None, dire=None):
        '''
        函数：生成某年某月的第一个和最后一个交易日
        Parameters
        ----------
        year : int
            年份
        month : int
            月份, 默认None,此时生成该年度第一个和最后一个交易日,
            其余状态下可选1-12, 代表1-12个月，变为求对应月份的首尾交易日
       
        dire : str
            DESCRIPTION.
    
        Returns
        -------
        datetime.date
        '''
        get_tdc = self.get_tdc
        if month == None:
            head = get_tdc(dt.date(year, 1, 1),0)
            tail = get_tdc(dt.date(year+1, 1, 1), -1)
        
        else:
            head = get_tdc(dt.date(year, month, 1),0)
            if month == 12:
                tail = get_tdc(dt.date(year, 1, 1), -1)
            else:
                tail = get_tdc(dt.date(year, month+1, 1), -1)
            
        if dire == None:
            return (head, tail)
        
        elif dire == 'h':
            return head 
        
        else:
            return tail 
    
    def get_td_next(self, td, freq, dire=None):
        '''
        函数:获得日期td的下一周/下一月/的首尾交易日
        Parameters
        ----------
        td : datetime.date
            日期,可以是交易日或者非交易日
        freq : str
            频率,freq = 'w'代表下一周, freq='m'代表下一月
        dire : str, optional
            默认None代表同时返回(head, tail)，dire = 'h'/'t'代表只返回'head'/'tail'
        Returns
        -------
        datetime.date
        所求日期
        '''
        get_tdc = self.get_tdc
        get_td_ymw = self.get_td_ymw
        
        if freq == 'm':
            y,m = td.year, td.month 
            if m == 12:
                head, tail = get_td_ymw(y + 1, 1)
            else:
                head, tail = get_td_ymw(y, m+1)
                
        elif freq == 'w':
            wd = td.weekday()
            
            if wd <=5:
                
                head = get_tdc(td, 5-wd)
                tail = get_tdc(td, 9-wd)
            else:
                head = get_tdc(td, 1)
                tail = get_tdc(head, 4)
            
        if dire == None:
            return (head, tail)
        
        elif dire == 'h':
            return head 
        
        else:
            return tail 
    
    def get_report_period_end(self, td, freq):
        '''
        函数：获取td过去最近一次财报的期末日期(注意是报告期期末而不是公告日)
        td: 可以是交易日也可以是非交易日
        freq: 财报披露的频率，freq = 'H'代表只观察年报和半年报, freq = 'Q'代表观察季报
        
        '''
        y,m = td.year, td.month 
        
        get_tdc = self.get_tdc
        
        if freq == "H":
            
            # 在每年的4月第一个交易日之前都无法获得上一年的年报，只有上一年的半年报
            if td <= get_tdc(dt.date(y, 4, 1), 0):
                period_end = dt.date(y-1, 6, 30)
            
            # 在每年的9月第一个交易日之前无法获得该年度的半年报，只有上一年的年报
            elif td <= get_tdc(dt.date(y, 9, 1),0):
                period_end = dt.date(y-1, 12, 31)
            
            else:
            # 每年的9月 - 12月都可以获得本年的半年报数据
                period_end = dt.date(y, 6, 30)
            
        return period_end    

    def get_dates_vectorize(self, tds, fun, params):
        '''
        上述函数都是针对某一个日期使用，本函数可以对一系列日期，实现向量化的生成
        例如：对 [t1, t2, t3] 同时使用 get_tdc函数
        
        Parameters
        ----------
        tds : iterable()
            可迭代对象，可以作为pd.Series(tds)跑通，如果是数组必须是一个一维数组
        fun : functions
            映射使用函数，只使用本python包下的函数
        params : dict
            function函数的对应使用字典
        Returns
        -------
        numpy.ndarray
        '''
        series = pd.Series(tds)
        res = series.apply(lambda x: fun(x, **params)).values
        return res 

