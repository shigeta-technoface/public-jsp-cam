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
import logging
import logging.config
from logger.settings import LOGGING

class Logger ( object ) :
	def __init__ ( self, config=LOGGING ) :
		logging.config.dictConfig ( config )

	@staticmethod
	def getLogger ( label='vnd' ) :
		return logging.getLogger ( label )

if __name__ == "__main__":
	pass
