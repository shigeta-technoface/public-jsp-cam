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
import sys, random
import array
import JobMachineTable
from operator import attrgetter
from deap import base
from copy import copy, deepcopy

def toStrAry ( sc, sep='', emp=' ' ) :
	strAry = []
	for row_num, row in enumerate ( sc ) :
		strM = ( 'M%2d:' + sep ) % row_num
		cur = 0
		for st, ed, job in row :
			if cur < st :
				strM += ( emp + sep ) * ( st - cur )
				cur = st
			strM += ( str ( job ) + sep ) * ( ed - st )
			cur = ed
		strAry.append ( strM )
	return strAry

def getGantt ( jmTable, individual ) :
	"""
	個体からガントチャートを取得する
	@param	jmTable	job x machine num, process time table
	@param	individual
	"""
	MAX_MACHINES = jmTable.getMachinesCount()
	# gantt [ MACHINE NUMBER ] = [ [0,0,None], [start, end, job_num], ...]
	# startの昇順に並ぶ、初期値にダミーの作業をセットしておく
	# 非稼働日があるならここでセットする
	gantt = [ [[0, 0, None], [sys.maxsize, sys.maxsize, None]] for _ in range ( MAX_MACHINES ) ]
	jmChild = jmTable.getChild()
	for job_num in individual :
		# job_numジョブのこの工程の(Machine番号, 処理時間)を取得
		machine = jmChild.getMachine ( job_num )
		process_time = jmChild.getProcessTime ( job_num )
		# このジョブの最も早い開始時刻を取得
		job_earliest = jmChild.getEarliest ( job_num )
		#print ( job_num, machine, process_time )
		# 左シフトで挿入できる隙間をさがす
		for idx, ( ( st0, ed0, _ ), ( st1, ed1, _ ) ) \
			in enumerate ( zip ( gantt [ machine ][:-1], gantt [ machine ][1:] ) ) :
			gap_st, gap_ed = ed0, st1
			# 隙間終了時刻でも最早時刻に満たない スキップ
			if gap_ed <= job_earliest : continue
			# 最早時刻が隙間の途中にあるとき 隙間の開始時刻を最早時刻にする
			gap_st = job_earliest if gap_st < job_earliest else ed0
			# 隙間にこの処理が入らない スキップ
			if ( gap_ed - gap_st ) < process_time : continue
			# 隙間にこの処理が入る; スケジュールにこの工程を挿入
			job_end = gap_st + process_time
			gantt [ machine ].insert ( idx + 1, [ gap_st, job_end, job_num ] )
			break

		jmChild.setNextEarliest ( job_num, job_end )
	# 最初と最後のダミー作業を削除
	gantt = [ row[1:-1] for row in gantt ]
	return gantt

def eval ( jmTable, individual ) :
	""" individualの適応度を取得する """
	# individualからガントチャートを取得する
	gantt = getGantt ( jmTable, individual )
	# 最後の作業終了時刻からメイクスパンを取得する
	makespan = 0
	for row in gantt :
		# rowは [ start, end, job_num ]のリスト
		makespan = max ( makespan, row [ -1 ][ 1 ] )
	return makespan,

def crossover ( ind1, ind2 ) :
	"""JSP用の2点交叉処理"""
	# ind1, ind2の長さは同じ
	size = len ( ind1 )
	cxpoint1, cxpoint2 = 0, 0
	while cxpoint1 == cxpoint2 :
		cxpoint1 = random.randrange ( 0, size )
		cxpoint2 = random.randrange ( 0, size )
	# 2点目が1点目より前なら入れ替える
	if cxpoint2 < cxpoint1 :
		cxpoint1, cxpoint2 = cxpoint2, cxpoint1
	# 部分遺伝子を取得
	sub1 = array.array ( ind1.typecode, ind1 [ cxpoint1 : cxpoint2 ] )
	sub2 = array.array ( ind2.typecode, ind2 [ cxpoint1 : cxpoint2 ] )
	new_sub1 = array.array ( ind1.typecode, [ -1 ] * ( cxpoint2 - cxpoint1 ) )
	new_sub2 = array.array ( ind2.typecode, [ -1 ] * ( cxpoint2 - cxpoint1 ) )
	for s1_idx, s1 in enumerate ( ind1 [ cxpoint1 : cxpoint2 ] ) :
		# ind1の部分遺伝子の要素がind2の部分遺伝子にみつからない
		if s1 not in sub2 : continue
		# みつかったら相手のnew_subに位置を保存してコピー
		s2_idx = sub2.index ( s1 )
		new_sub1 [ s2_idx ] = s1
		new_sub2 [ s1_idx ] = s1
		# コピーした要素は-1にしておく
		sub1 [ s1_idx ] = -1
		sub2 [ s2_idx ] = -1
	# コピーしなかった要素を順序を保存して戻す
	for s1 in sub1 :
		# -1の場合コピー済み
		if s1 == -1 : continue
		# new_sub1の未コピー位置を取得
		idx = new_sub1.index ( -1 )
		new_sub1 [ idx ] = s1
	for s2 in sub2 :
		if s2 == -1 : continue
		idx = new_sub2.index ( -1 )
		new_sub2 [ idx ] = s2
	# 部分遺伝子を個体にセット
	ind1 [ cxpoint1 : cxpoint2 ] = new_sub1
	ind2 [ cxpoint1 : cxpoint2 ] = new_sub2
	return ind1, ind2

def mutation ( ind ) :
	"""JSP用の突然変異処理"""
	size = len ( ind )
	# 理由は不明だがオリジナルソースでは2回実施している
	for _ in range ( 2 ) :
		pos1 = random.randrange ( 0, size )
		pos2 = random.randrange ( 0, size )
		ind [ pos1 ], ind [ pos2 ] = ind [ pos2 ], ind [ pos1 ]
	return ind

def getWorst ( population, n ) :
	"""
	fitnessesの大きい方からn個の個体を取得
	@param	population	individualのリスト
	@param	n	取得する個体数
	@return nth worst individuals
	"""
	return sorted ( population, key=lambda x: x.fitness.values, reverse=True  )[ : n ]

def getArgWorst ( population, n ) :
	"""
	fitnessesの大きい方からn個のインデックスを取得
	@param	population	individualのリスト
	@param	n	取得する個体数
	@return nth worst indexes
	"""
	s_inds = getWorst ( population, n )
	selected = []
	for ind in s_inds :
		selected.append ( population.index ( ind ) )
	return selected

def getClusters ( population ) :
	clusters = {}
	for ind in population :
		# 各個体の先頭遺伝子だけを取得
		if ind [ 0 ] not in clusters :
			clusters [ ind [ 0 ] ] = []
		clusters [ ind [ 0 ] ].append ( ind )
	return clusters

def getClusterList ( population, n=10 ) :
	cluster = getClusters ( population )
	cl = [ 0 ] * n
	for k, v in cluster.items() :
		cl [ k ] = len ( v )
	return cl

def getArgWorstCAM ( population, n ) :
	"""クラスタ平均化法(Cluster Averaging Method)により適応度が悪い個体をn個選択
	@param	population	numpy.array	個体リスト。順序は適応度の小さい順に変わる
	@param	n	個体選択数
	@return	選択した個体インデックスリスト
	"""
	selected = []
	# 各個体の先頭遺伝子別のクラスターを取得
	clusters = getClusters ( population )
	max_cluster = max ( clusters.values(), key=len )
	max_cluster_sz = len ( max_cluster )
	min_cluster_sz = len ( min ( clusters.values(), key=len ) )
	# 最大のクラスターと最小のクラスターと個体数の差が小さければ全体から探す
	if ( max_cluster_sz - min_cluster_sz  ) < 40 :
		selected = getArgWorst ( population, n )
	# 最大のクラスターと最小のクラスターと個体数の差が大きければ最大クラスターから探す
	else :
		# 最大のクラスターの個体の適応度下位n件を取得
		s_inds = getWorst ( max_cluster, n )
		for ind in s_inds :
			selected.append ( population.index ( ind ) )
	return selected

if __name__ == "__main__" :
	pass
