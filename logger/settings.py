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
import time, logging.config, os, os.path
from common.common import log_dirname, log_name, report_name, detail_name

class UTCFormatter ( logging.Formatter ) :
	converter = time.gmtime

report_base = os.environ [ 'LOG_PATH' ] if 'LOG_PATH' in os.environ else report_dir
if os.path.isdir ( report_base ) is False :
	os.makedirs ( report_base )
log_dir = report_base
if os.path.isdir ( log_dir ) is False :
	os.makedirs ( log_dir )

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'brief': {
			'()': UTCFormatter,
			'format': '%(message)s',
		},
		'local': {
			'()': UTCFormatter,
			'format': '[%(levelname)s] %(message)s',
		},
		'verbose': {
			'()': UTCFormatter,
			'format': '[%(levelname)s] %(asctime)s %(module)s %(message)s',
		}
	},
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
			'formatter': 'local',
		},
		'file': {
			'class': 'logging.FileHandler',
			'formatter': 'verbose',
			'filename': os.path.join ( log_dir, log_name )
		},
		'report': {
			'class': 'logging.FileHandler',
			'formatter': 'brief',
			'filename': os.path.join ( log_dir, report_name )
		},
		'detail': {
			'class': 'logging.FileHandler',
			'formatter': 'brief',
			'filename': os.path.join ( log_dir, detail_name )
		},
	},
	'loggers': {
		'vnd': {
			'handlers': [ 'file', 'console' ],
			'level': 'INFO',
			'propagate': True,
		},
		'report': {
			'handlers': [ 'report' ],
			'level': 'INFO',
			'propagate': True,
		},
		'detail': {
			'handlers': [ 'detail' ],
			'level': 'INFO',
			'propagate': True,
		},
	},
}
