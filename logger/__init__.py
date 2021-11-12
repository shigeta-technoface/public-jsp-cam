# coding: utf-8
"""
@title	A Python DEAP implementation of Genetic Algorithms with Cluster Averaging Method for Solving Job-Shop Scheduling Problems
@see	https://www.jstage.jst.go.jp/article/jjsai/10/5/10_769/_article/-char/ja/
@see	https://www.personal-media.co.jp/book/comp/173/
@author	Shigeta Yosuke
@email	shigeta@technoface.co.jp
@company	Technoface K.K.
@license	Apache 2.0
@copyright	Copyright 2021, Technoface K.K.
@created date	2021-11-12
"""
import os
from . import Logger

logger = Logger.Logger()
root_log = logger.getLogger ( 'vnd' )
report_log = logger.getLogger ( 'report' )
detail_log = logger.getLogger ( 'detail' )
