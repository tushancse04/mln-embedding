from DBManager import DBManager,dbconfig
from mln import MLN
from word2vec import word2vec
from random_cluster import random_cluster
from tuffy import tuffy
from magician import magician
from performance import performance
import sys
from common_f import common_f
from kmeans_cluster import kmeans_cluster
from bmf_cluster import bmf_cluster
import time
import random
class Test_DS:
	def __init__(self):
		pass

	def merge(self):
		for dsname in ['er','protein','webkb']:
			mln = MLN(dsname)
			db = DBManager(dsname,mln)
			db.merge()

	def compress(self):
		for dsname in ['er','protein','webkb']:
			mln = MLN(dsname)
			db = DBManager(dsname,mln)
			db.compress(mln, .1)

	def test(self):
		#self.merge()
		#self.compress()
		#return
		embedding_size = 100
		for CLUSTER_MIN_SIZE in range(4,19,2):
			for dsname in ['webkb']:
				mln = MLN(dsname)
				db = DBManager(dsname,mln)
				print('merge db dom sizes:')
				dom_obj_map = db.get_dom_objs_map(mln,db.merge_db_file)
				cf = common_f()
				cf.delete_files(mln.pickle_location)
				cf.remove_irrelevant_atoms()
				embedding_size += 100
				embedding_size = embedding_size%1000

				db.set_atoms()
				bmf = bmf_cluster(dsname)
				bmf.cluster(db,1,mln.pdm,dom_obj_map)

				print('original db dom sizes(after compression):')
				orig_dom_objs_map = db.get_dom_objs_map(mln,mln.orig_db_file)
				CLUSTER_MIN_SIZE = 10
				w2v = word2vec(dsname,db,CLUSTER_MIN_SIZE,embedding_size)
				print('w2v cluster dom sizes:')
				w2v_dom_objs_map = db.get_dom_objs_map(mln,w2v.w2v__cluster_db_file)
				cr = cf.calculate_cr(orig_dom_objs_map,w2v_dom_objs_map)


				print('cr : ' + str(cr))
				rc = random_cluster(dsname)
				rc.generate_random_db(db,w2v.pred_atoms_reduced_numbers,mln,w2v_dom_objs_map)
				print('random cluster dom sizes')
				db.get_dom_objs_map(mln,mln.random__cluster_db_file)




				kmc = kmeans_cluster(dsname)
				kmc.cluster(db,str(cr),mln.pdm,w2v_dom_objs_map,mln.dom_pred_map)
				print('kmeans cluster dom sizes:')
				kmeans_dom_objs_map = db.get_dom_objs_map(mln,kmc.kmeans__cluster_db_file)
				mln.create_magician_mln()
				magician(dsname,mln)
				#tuffy(dsname)
				orig_meta_map = {}

				orig_meta_map['bmf'] = bmf.bmf_orig_meta_map
				orig_meta_map['w2v'] = w2v.w2v_orig_meta_map
				orig_meta_map['random'] = rc.rand_orig_meta_map
				orig_meta_map['kmeans'] = kmc.kmeans_orig_meta_map
				print('Dataset : ' + dsname +  '; CR : ' + str(cr))
				p = performance(dsname,embedding_size)
				p.compare_marginal(mln,orig_meta_map,cr)
				#p.compare_map(mln,orig_meta_map,cr)


t = Test_DS()
for i in range(10):
	t.test()
