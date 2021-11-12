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
class JobMachineTableBase :
	""" Job x Machine データを格納する基底クラス """
	def __init__ ( self ) :
		self._mTable, self._ptTable = self._initTables()

	def _initTables ( self ) :
		"""問題ごとに派生クラスでオーバーライドする"""
		return None, None

	def _convertJMTable ( self, jmTable ) :
		# 機械番号をゼロ開始に変更しつつ機械番号用のテーブルと加工時間用のテーブルに分けて格納
		mTable, ptTable = [], []
		for row in jmTable :
			machines, pt_list = [], []
			for m, p in row :
				machines.append ( m-1 )
				pt_list.append ( p )
			mTable.append ( machines )
			ptTable.append ( pt_list )
		return mTable, ptTable

	def getJobsCount ( self ) :
		""" ジョブ数を取得 """
		return len ( self._mTable )

	def getMachinesCount ( self ) :
		""" ジョブの工程数（機械数）を取得 """
		return len ( self._mTable [ 0 ] )

	def getMachine ( self, job_num, process_index ) :
		""" job_numジョブのprocess_index工程のMachine番号を取得 """
		return self._mTable [ job_num ][ process_index ]

	def getProcessTime( self, job_num, process_index ) :
		""" job_numジョブのprocess_index工程の処理時間を取得 """
		return self._ptTable [ job_num ][ process_index ]

	def getChild ( self ) :
		return JobMachineChild ( self )


class JobMachineChild :
	""" ジョブの状態を管理するクラス """
	def __init__ ( self, jmParent ) :
		self._jmParent = jmParent
		# ジョブごとの次工程番号を格納する配列
		self._next_process_indexes = [ 0 ] * jmParent.getJobsCount()
		# ジョブごとの次工程が開始できる時刻の配列
		self._next_process_starts = [ 0 ] * jmParent.getJobsCount()
	def getMachine ( self, job_num ) :
		""" job_numのジョブの次工程の機械番号を取得 """
		process_index = self._next_process_indexes [ job_num ]
		return self._jmParent.getMachine ( job_num, process_index )
	def getProcessTime( self, job_num ) :
		""" job_numのジョブの次工程の処理時間を取得 """
		process_index = self._next_process_indexes [ job_num ]
		return self._jmParent.getProcessTime ( job_num, process_index )
	def getEarliest ( self, job_num ) :
		""" job_numジョブの最も早い次工程の開始時刻を取得; この時間より後に開始できない"""
		return self._next_process_starts [ job_num ]
	def setNextEarliest ( self, job_num, job_end ) :
		""" job_numジョブを次工程に進める。次工程は現工程の終了時刻以降に開始できる """
		self._next_process_starts [ job_num ] = job_end
		self._next_process_indexes [ job_num ] += 1

class EX3_4 ( JobMachineTableBase ) :
	""" サンプル用の問題 """
	def _initTables ( self ) :
		"""EX3x4のテーブルを取得"""
		jmTable = [
			[ [1,3], [2,2], [3,4], [4,1] ]
			, [[2,2], [4,2], [3,1], [1,3] ]
			, [[1,2], [3,2], [2,1], [4,2] ]
		]
		# 機械番号をゼロ開始に変更しつつ機械番号用のテーブルと加工時間用のテーブルに分けて格納
		return self._convertJMTable ( jmTable )

class MT6_6 ( JobMachineTableBase ) :
	""" MT6x6問題 """
	def _initTables ( self ) :
		"""MT6x6のテーブルを取得"""
		jmTable = [
			[ [3,1], [1,3], [2,6], [4,7], [6,3], [5,6] ]
			, [[2,8], [3,5], [5,10], [6,10], [1,10], [4,4] ]
			, [[3,5], [4,4], [6,8], [1,9], [2,1], [5,7] ]
			, [[2,5], [1,5], [3,5], [4,3], [5,8], [6,9] ]
			, [[3,9], [2,3], [5,5], [6,4], [1,3], [4,1] ]
			, [[2,3], [4,3], [6,9], [1,10], [5,4], [3,1] ]
		]
		# 機械番号をゼロ開始に変更しつつ機械番号用のテーブルと加工時間用のテーブルに分けて格納
		return self._convertJMTable ( jmTable )

class MT10_10 ( JobMachineTableBase ) :
	""" MT10x10問題 """
	def _initTables ( self ) :
		"""MT10x10のテーブルを取得"""
		jmTable = [
			[ [1,29], [2,78], [3,9], [4,36], [5,49], [6,11], [7,62], [8,56], [9,44], [10,21] ]
			, [ [1,43], [3,90], [5,75], [10,11], [4,69], [2,28], [7,46], [6,46], [8,72], [9,30] ]
			, [ [2,91], [1,85], [4,39], [3,74], [9,90], [6,10], [8,12], [7,89], [10,45], [5,33] ]
			, [ [2,81], [3,95], [1,71], [5,99], [7,9], [9,52], [8,85], [4,98], [10,22], [6,43] ]
			, [ [3,14], [1,6], [2,22], [6,61], [4,26], [5,69], [9,21], [8,49], [10,72], [7,53] ]
			, [ [3,84], [2,2], [6,52], [4,95], [9,48], [10,72], [1,47], [7,65], [5,6], [8,25] ]
			, [ [2,46], [1,37], [4,61], [3,13], [7,32], [6,21], [10,32], [9,89], [8,30], [5,55] ]
			, [ [3,31], [1,86], [2,46], [6,74], [5,32], [7,88], [9,19], [10,48], [8,36], [4,79] ]
			, [ [1,76], [2,69], [4,76], [6,51], [3,85], [10,11], [7,40], [8,89], [5,26], [9,74] ]
			, [ [2,85], [1,13], [3,61], [7,7], [9,64], [10,76], [6,47], [4,52], [5,90], [8,45] ]
		]
		# 機械番号をゼロ開始に変更しつつ機械番号用のテーブルと加工時間用のテーブルに分けて格納
		return self._convertJMTable ( jmTable )

