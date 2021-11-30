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
import os, sys, argparse, random, array
from multiprocessing import Pool
import numpy as np

from deap import base
from deap import creator
from deap import tools

import JobMachineTable, schedule

def initIndividual ( job_num, machine_num ) :
	# 0からmachine_numまでの数がそれぞれjob_numあるリストを作成しシャッフルする
	src = list ( range ( job_num ) ) * machine_num
	random.shuffle ( src )
	return src

def getJmTable ( is_test ) :
	jmTable = None
	if is_test :
		"""
		real    0m1.921s
		user    0m12.600s
		sys     0m0.780s
		"""
		jmTable = JobMachineTable.MT6_6()
		#jmTable = JobMachineTable.EX3_4()
	else :
		"""
		real    1m1.123s
		user    8m52.286s
		sys     0m7.350s
		"""
		jmTable = JobMachineTable.MT10_10()
	return jmTable

def initialize ( is_test, no_cam ) :
	"""job machine Tableをもとに個体、世代の初期設定"""
	from functools import partial
	jmTable = getJmTable ( is_test )
	MAX_JOBS = jmTable.getJobsCount()
	MAX_MACHINES = jmTable.getMachinesCount()
	# makespan最小化
	creator.create ( "FitnessMin", base.Fitness, weights=(-1.0,) )
	# 個体はジョブ番号のリスト
	#creator.create ( "Individual", list, fitness=creator.FitnessMin )
	creator.create ( "Individual", array.array, typecode='b', fitness=creator.FitnessMin ) # 'b' is signed char
	toolbox = base.Toolbox()
	# ゼロからMAX_MACHINES未満までがMAX_JOBS回ランダムに並ぶ個体と設定
	gen_ind = partial ( initIndividual, MAX_JOBS, MAX_MACHINES )
	toolbox.register ( "individual", tools.initIterate, creator.Individual, gen_ind )
	# 初期世代を生成する関数を登録、初期世代はIndividualのリストとして設定
	toolbox.register ( "population", tools.initRepeat, list, toolbox.individual )
	# 評価関数を登録
	toolbox.register ( "evaluate", schedule.eval, jmTable )
	# 交叉関数を登録
	toolbox.register ( "mate", schedule.crossover )
	# 突然変異を登録
	toolbox.register ( "mutate", schedule.mutation )
	# ルーレット選択を登録
	toolbox.register ( "select", tools.selRoulette )
	# 置換操作を登録
	if no_cam :
		# 通常の置換操作
		toolbox.register ( "getArgWorst", schedule.getArgWorst )
	else :
		# クラスタ平均法（CAM）による置換操作
		toolbox.register ( "getArgWorst", schedule.getArgWorstCAM )
	return toolbox, jmTable

### report_log, detail_log
def sort_log( fname, func ) :
	""" detail_logをseed, generationの昇順に並び替える """
	import csv
	with open ( fname ) as f :
		reader = csv.reader ( f, delimiter='\t' )
		header = next(reader)
		rows = sorted ( reader, key=func )
	with open ( fname, 'w' ) as f :
		writer = csv.writer ( f, delimiter='\t' )
		writer.writerow ( header )
		writer.writerows ( rows )

def write_detail_header ( no_cam ) :
	""" detail_logのヘッダ部を保存する """
	from logger import detail_log
	header = [ 'seed', 'generation', 'best_fit', 'best_gen', 'Min', 'Max', 'Avg', 'Std', ]
	if no_cam : pass
	else :
		# 各クラスターの大きさと最大クラスターと最小クラスターとの差分を記録（40を境に置換処理が変わるため）
		header += [ 'C%02d' % idx for idx in range ( 10 ) ] + [ 'Cdiff' ]
	detail_log.info ( '\t'.join ( header ) )

def write_detail_body ( pop, best_ind, best_gen, seed, cur_gen, no_cam ) :
	""" detail_logに統計値を記録する """
	from logger import detail_log
	# 統計値計算
	fits = np.array ( [ ind.fitness.values[0] for ind in pop ] )
	row = [ seed, cur_gen, best_ind.fitness.values[0], best_gen, fits.min(), fits.max(), fits.mean(), fits.std() ]
	if no_cam : pass
	else :
		clist = schedule.getClusterList ( pop )
		row += clist + [ max(clist)-min(clist) ]
	detail_log.info ( '\t'.join ( [ str(x) for x in row ] ) )
	return

def sort_detail_log() :
	""" detail_logをseed, generationの昇順に並び替える """
	import csv
	from logger import detail_log
	# detail_logのファイル名を取得
	fname = detail_log.handlers[0].baseFilename
	sort_log ( fname, lambda r: ( int ( r [ 0 ] ), int ( r [ 1 ] ) ) )

def write_report_header() :
	""" report_logのヘッダ部を保存する """
	from logger import report_log
	report_log.info ( '\t'.join ( ( 'seed', 'best_fit', 'best_gen', 'best_ind' ) ) )

def write_report_body ( seed, best_gen, best_fit, best_ind ) :
	""" report_logのボディ部を保存する """
	from logger import report_log
	report_log.info ( '\t'.join ( ( '%d', '%d', '%d', '%s' ) )
									% ( seed, best_fit, best_gen, best_ind.tolist() ) )

def sort_report_log() :
	""" report_logをseedの昇順に並び替える """
	import csv
	from logger import report_log
	# report_logのファイル名を取得
	fname = report_log.handlers[0].baseFilename
	sort_log ( fname, lambda r: int ( r [ 0 ] ) )

def write_best_of_loop ( best_fits, best_inds ) :
	""" 全ループでのベスト個体を記録する """
	from logger import root_log
	bf = np.array ( best_fits )
	root_log.info ( "Min:%s Max:%s Avg:%s Std:%s" % ( bf.min(),bf.max(),bf.mean(),bf.std() ) )
	best_ind = best_inds [ np.argmin ( bf ) ]
	root_log.info ( "Best individual: %s" % best_ind.tolist() )
	root_log.info ( "\n"+"\n".join ( schedule.toStrAry( schedule.getGantt ( gJmTable, best_ind ), sep='' ) ) )

def write_line_profile ( prof ) :
	""" line profile結果を記録する """
	import io
	from logger import root_log
	with io.StringIO() as bs :
		prof.print_stats ( stream=bs, output_unit=0.001 )
		root_log.info ( '\n' + bs.getvalue() )

### main process
def test2 ( population ) :
	""" populationに遺伝的操作を施す """
	# 交叉確率、突然変異確率
	global gToolbox
	CXPB, MUTPB = 0.8, 0.5
	# idx1, idx2 をルーレット選択し複製
	inds = list ( map ( gToolbox.clone, gToolbox.select ( population, 2 ) ) )
	# 交叉確率の割合で交叉処理を実施
	if random.random() < CXPB :
		gToolbox.mate ( inds [ 0 ], inds [ 1 ] )
		# 操作した個体の適応度を無効にする
		del inds [ 0 ].fitness.values
		del inds [ 1 ].fitness.values
	# 選択した個体それぞれに操作
	for ind in inds :
		# 突然変異確率の割合で突然変異処理を実施
		if random.random() < MUTPB :
			gToolbox.mutate ( ind )
			# 操作した個体の適応度を無効にする
			del ind.fitness.values
		# 適応度が無効である個体を再評価
		if not ind.fitness.valid :
			ind.fitness.values = gToolbox.evaluate ( ind )
		# 既存の個体と置換
		worst_idx = gToolbox.getArgWorst ( population, 1 )[ 0 ]
		population [ worst_idx ] = ind
	return population

def do_generation ( population ) :
	# 個体数半分だけ繰り返す、同じ個体を同時あるいは繰り返し選択してもよい
	for _ in range ( len ( population ) // 2 ) :
		test2 ( population )
	return population

def do_loop ( args ) :
	global gToolbox
	seed, population_sz, is_test, no_cam = args
	random.seed ( seed )
	# 初期世代を取得
	pop = gToolbox.population ( n=population_sz )
	# 初期世代の適応度を取得し個体にセット
	fitnesses = list ( map ( gToolbox.evaluate, pop ) )
	for ind, fit in zip ( pop, fitnesses ) :
		ind.fitness.values = fit
	# 世代ごとの処理準備
	g_max = 100 if is_test else 3000
	best_gen = 0 ; best_ind = gToolbox.clone ( tools.selBest ( pop, 1 )[ 0 ] )
	# detail_logに統計値を保存
	write_detail_body ( pop, best_ind, best_gen, seed, 0, no_cam )
	# ゼロ世代目の評価は終わっているので1世代目から始める
	for g in range ( 1, g_max ) :
		pop = do_generation ( pop )
		# このループでの最良個体を保存
		tbest_ind = tools.selBest ( pop, 1 )[ 0 ]
		if tbest_ind.fitness.values[0] < best_ind.fitness.values[0] :
			best_ind = gToolbox.clone ( tbest_ind )
			best_gen = g
		# detail_logに統計値を保存
		write_detail_body ( pop, best_ind, best_gen, seed, g, no_cam )
	# report_logに結果を記録
	write_report_body ( seed, best_gen, best_ind.fitness.values[0], best_ind )
	# finally
	return best_gen, best_ind.fitness.values[0], best_ind

def test ( seed, population_sz, loop, is_test, no_cam ) :
	global gJmTable
	# detail_log, report_logのヘッダ部書き出し
	write_detail_header ( no_cam )
	write_report_header()
	# loopをマルチプロセッシングで実行
	best_fits = [] ; best_inds = []
	do_loop_arg_list = [ ( seed + loop_idx, population_sz, is_test, no_cam ) for loop_idx in range ( loop ) ]
	results = list ( gToolbox.map ( do_loop, do_loop_arg_list ) )
	for result in results :
		_, best_fit, best_ind = result
		best_fits.append ( best_fit )
		best_inds.append ( best_ind )
	# 全ループでのベスト個体を記録
	write_best_of_loop ( best_fits, best_inds )
	# detail_log, report_logをソートする
	sort_detail_log()
	sort_report_log()

def main2 ( args ) :
	""" main処理その1の続き """
	# 処理時間を計測しない
	if args.do_perf == False :
		test ( args.seed, args.population, args.loop, args.is_test, args.no_cam )
	# 処理時間を計測する
	else :
		from line_profiler import LineProfiler
		prof = LineProfiler()
		prof.add_function ( test )
		prof.add_function ( test2 )
		prof.add_function ( schedule.eval )
		prof.add_function ( schedule.getGantt )
		# 計測開始
		prof.runcall ( test, args.seed, args.population, args.loop, args.is_test, args.no_cam )
		# 計測結果をログに記録
		write_line_profile ( prof )

def main ( args ) :
	""" main処理その1 """
	global gToolbox, gJmTable
	gToolbox, gJmTable = initialize ( args.is_test, args.no_cam )
	np.set_printoptions ( linewidth=10000 )
	# multiprocessingしない
	if args.no_mp :
		main2 ( args )
	# multiprocessingする
	else :
		# このタイミングでforkする
		with Pool ( args.processes ) as pool :
			gToolbox.register ( "map", pool.map )
			main2 ( args )

def parseArg() :
	defint = u'(default: %(default)d)'
	deffloat = u'(default: %(default)f)'
	defstr = u'(default: %(default)s)'

	parser = argparse.ArgumentParser ( description='平野の方法でJSPを解きます' )
	# input data
	parser.add_argument ( '--seed', default=0, type=int, help='the number of radom seed.' + defint )
	parser.add_argument ( '--population', default=100, type=int
			, help='the number of individuals in one population.' + defint )
	parser.add_argument ( '--loop', default=1, type=int, help='Loop count.' + defint )
	parser.add_argument ( '--processes', default=os.cpu_count(), type=int
						, help='The number of worker processes.' + defint )
	# output
	parser.add_argument ( '--logdir', default='./logs', type=lambda x: os.path.abspath ( x )
						, help=u'ログ出力ディレクトリ' + defstr )
	# control
	parser.add_argument('--do_perf', action='store_true', help=U'Do line profile.' )
	parser.add_argument('--no_mp', action='store_true', help=U'Dont multi processing.' )
	parser.add_argument('--no_cam', action='store_true', help=U'Dont use CAM..' )
	parser.add_argument('--is_test', action='store_true', help=U'MT6x6/MT10x10 and 100/3000 generation.' )
	return parser.parse_args()

if __name__ == "__main__" :
	args = parseArg()
	if 'LOG_PATH' not in os.environ :
		os.environ [ 'LOG_PATH' ] = args.logdir
	from logger import root_log
	for a in vars ( args ) :
		root_log.info ( '{}={}'.format ( a, getattr ( args, a ) ) )
	try :
		main ( args )
		root_log.info ( 'Finished!' )
	except :
		root_log.exception ( 'Exception:' )
		raise
	finally :
		pass

