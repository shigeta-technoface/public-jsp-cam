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
import os, os.path, datetime, configparser

dir_name = os.path.abspath ( os.path.join ( os.path.dirname ( __file__ ) , os.path.pardir ) )
time_stamp = datetime.datetime.now() .strftime ( "%Y%m%d%H%M%S%f" ) [ : -3 ]
report_dir = os.path.join ( dir_name, 'report' )
log_dirname = 'logs'
log_name = "%s_log.log" % time_stamp
report_name = "%s_report.dat" % time_stamp
detail_name = "%s_detail.dat" % time_stamp

if __name__ == "__main__":
	pass
