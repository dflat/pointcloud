import peewee
from db_config import air_login
from db_config import ground_login
from collections import namedtuple
import threading
from queue import Queue
import time, random

HOST     = air_login['host']
DATABASE = air_login['database']
USER     = air_login['user']
PASS     = air_login['password']
RAMS = peewee.MySQLDatabase(database=DATABASE, host=HOST, user=USER, passwd=PASS) 

HOST     = ground_login['host']
DATABASE = ground_login['database']
USER     = ground_login['user']
PASS     = ground_login['password']
GROUND = peewee.MySQLDatabase(database=DATABASE, host=HOST, user=USER, passwd=PASS) 

encoded_white_bal = "$*$,$)0+$)2+$)2,$)2-$)1+$*$2$)20$)30$)3-$)2,$)2$$)3'$*$1$)2$$)3'$)1($)13$*&($)2-$).-$)/+$)2%$)22$)10$)2&$*%)$)2.$)3*$)2/$)3&$)20$)3)$)3$$)2+$)3.$)30$)32$)1%$).2$)2($)3+$*$$$)3($)2($)3&$)3)$)13$)0'$)3($*%-$)2-$)1$$)1/$*$%$)03$)2&$),,$)2/$)2+$*$3$)2%$)1-$)3+$*%$$)3)$)2($)1)$)3$$)2&$*%'$)11$)1.$)3)$)20$*%%$)3*$*$%$*$/$)2%$)2/$*$-$*$&$)1-$)01$)1*$)3($)2*$)3$$*$2$)22$)30$)1'$)3+$)//$)2$$)3/$)3)$)3-$)1,$)01$)3.$)2&$*$)$*$)$*$,$)23$*$.$)3.$)10$)20$)21$)2/$)3($*$)$)12$*$)$*$,$*$2$*%/$)3.$)31$)3,$)2+$)0.$)3+$)1+$*$)$)32$*$-$)3'$)/$$)2,$)3-$)3,$)/0$)10$)1%$)-/$*$&$)0-$)2,$)3$$)+%$*%)$*$/$*$)$*$)$*$%$)2-$)2+$)2&$)31$*%$$*$/$)/&$)30$*%%$)23$)2+$)/.$*$'$)23$*$2$)3,$*%($)2+$)32$)30$)3*$)22$)3$$*$$$)2&$)3,$*$%$)3'$)03$)3&$).1$)30$)32$)3,$)30$)0)$)2)$)1)$)10$)3%$*$0$*$($)0,$*$&$*$)$*$.$*$,$*$'$*%,$)3,$)1)$)0+$)12$)3,$)2+$)1&$)3-$*%*$)3($)31$)2'$)3($*''$*)3$*$/$*+-$*+1$*)$$*%-$*%)$*&,$)3/$*%)$)3)$)3$$*$'$*%2$)33$*&,$)3-$)30$*$+$)3.$*$-$)3&$)3($)/2$*$/$)3.$)3-$)2'$)10$*%%$)0%$)3$$*$1$*$1$)3+$*%*$*%)$*'$$*&)$*$-$)20$*$*$)0+$*$*$)..$)2.$*&($*$3$*%+$*$2$*&%$)3*$*$$$)03$*%1$)3,$*%,$*%'$)3.$)20$*%'$*%1$)1&$*%$$*&,$*$,$)32$)2&$)3*$)3'$)2%$)3)$*$0$*$1$*%%$*&%$)23$*%)$)3($*%$$*&($*$+$*$%$)31$*%3$)22$*%/$*$)$*$/$*%/$*%,$*%-$)11$*%)$*$($)31$*$3$*$*$*&'$*%%$*%3$*%.$*%1$*%+$*%+$*(*$*%0$*(1$*(-$*)1$*,+$*+2$*+1$*-%$*,&$*+*$*(*$*)+$*(,$*)-$*(/$*(3$**-$*'%$*'2$*)'$*)0$*&,$*)$$*&'$*%2$*''$*%+$*%,$*&-$*',$*&*$*$3$*&($*'%$*%,$*&*$*$+$)3*$*&&$(&%$*$-$*$%$*$,$*&$$)3($)2$$)3,$*%*$*$/$)3)$)&1$)3*$)3/$*$$$*%$$*%%$*$*$).,$)22$*%%$*%'$)12$*$2$*$%$*$3$)3+$)3+$)30$)3)$)2'$*$($).2$*$+$)3($)2$$)3/$*$)$*%+$)23$*$,$)3/$)2($)//$)1.$)3($)21$*$&$)32$*$,$*$3$)3*$)2,$)2+$*$'$)0'$).&$)3($*%-$)3'$)0($)2$$)33$*&$$*%-$)32$)23$*&,$*$/$*$0$*&$$*$-$*$,$*'.$*'1$*+)$**+$*-/$*.2$*3'$++%$+13$,*/$,.+$,2-$-$+$-&&$,30$,1($,20$-&%$-(/$-)1$-*($-+$$-%%$,+)$,)2$+2-$+/+$+-'$+*&$+&)$+$&$*-%$*.0$*-/$*+1$*+-$*+)$*+*$*(.$*(.$*''$*%2$*%2$*$$$*$3$*%1$)/3$*%$$*&'$)2.$*$%$)31$*%.$*$2$*$($*$3$)2*$)21$*&%$*%($)12$)03$*&'$)32$)23$)3+$*$&$)2,$*&&$*$+$)2*$*$&$)0-$)3'$*$3$)/1$)23$*$+$)3+$)2,$*&,$*%+$*$-$*'0$*$)$*)*$*'0$*(*$**3$*)&$*)2$*'1$*+&$*+.$**2$*,,$*-)$*..$*.3$*/%$*1$$*/&$*0+$*.$$*1($*0%$*33$*13$*3$$*1+$*2)$*-)$*+/$*,/$*)($*-1$*+0$*0&$*3%$*2%$*1*$*1.$*.($*-($**,$*(3$*+'$**+$**-$*'*$*),$*.)$*,%$*.-$*.-$*,'$*+/$*)1$*+$$*'/$*(*$*'0$*'/$*)1$*)'$*(+$*(.$*,-$*,&$*+$$*.*$*3)$+(,$,$/$-.,$/,/$1-,$20($3/'$3-%$2+/$1&($/1($.*$$.%,$-*'$-$%$,)*$+3/$+-0$+)/$+'($*0&$+$+$*2/$*10$+$)$+%)$*..$+'&$+'*$*3+$+&1$+%3$+&($+*,$+(+$+%.$+'.$+)1$+'2$+%'$+&%$+&/$+&%$+%2$+)$$+*'$+.%$++,$++,$+('$+$,$*0)$*).$*+2$*)($)32$*($$*$$$*&3$*&-$*$)$*%%$*$.$)3*$)3,$*$1$*')$*&%$*'$$)3*$*'0$*%-$*'%$*'$$*&0$*%3$*&0$*$)$*(.$)2)$*'2$*%-$*''$*(1$*('$)0-$**,$*)&$***$*+*$*+.$*).$*'.$*(+$*(,$*)$$*($$)/&$*$3$*(/$*'1$*$0$*(($*&)$*(.$*'$$*'/$*%$$)30$*(+$*&0$*(2$*(-$*$+$*(-$*(*$*&($*&+$*'%$*&'$*&0$*$*$*%1$*'.$*&)$*&-$*&'$*&&$*&'$*%,$*&($*&-$)31$)01$*$*$*%&$*%0$)3.$)3/$*%$$*$,$*$-$*')$*%'$)31$*&'$)3,$*$($*%)$*&($*$,$*%3$*$3$*%)$*%*$*%'$*%2$*&,$*$3$*$,$*&0$*%'$)3,$*'&$*)'$*)'$*()$*&,$*'$$*$0$*$)$)1($*&($)1/$)0)$*&,$*%)$*(*$*&.$*'-$*$/$*%)$*&1$*$2$)3+$*$+$*%1$)30$)/*$)2*$*%$$*$&$*$*$)-3$)3,$*$%$*%/$*$3$*&-$*&+$*'1$*(&$*+&$*,+$*-$$*-3$*03$*1'$*/($*,1$*+.$*.1$*-$$**+$*-+$*('$*,1$*-2$*'3$*'*$*'*$*'&$)/.$)0,$)1'$)1&$)3*$*$*$)33$)3.$*&*$)3)$)11$)0+$)3)$)3.$)2+$).($)2($)3-$)3&$)12$)1+$*$&$)1'$*$'$)20$)00$)21$)3)$)22$)1-$*$+$)33$)2'$*$+$)32$*$&$*$3$)32$*$&$*%($)2/$)3'$*$*$)0&$)-/$)3)$*$,$*%+$)2-$)3*$)1$$)3%$*%%$*$*$*$,$*$%$)3%$*%0$)3/$)21$)2+$)2&$)2$$)2+$)31$)2-$)1%$*$*$*$*$)0,$*$+$*$$$*$$$)3)$)3$$*$&$*$%$*%,$*%)$)2)$)3,$)/($)*3$)-+$)2*$*$-$)3($*%%$)23$)3)$)1)$)33$)11$)2+$)3&$*$/$)32$*$-$)2-$)2+$*$'$*$3$)32$)30$)3)$)/0$*$1$)-3$*$%$)3/$*$2$*$$$*%'$)32$*$%$)2'$).-$*$$$*$%$*%&$*$)$)3/$)2/$)1.$*$-$*%%$)3%$)2'$)1,$*%'$*$+$*%3$)23$*%+$)30$)1-$*%($)--$*$*$)3)$)31$*$2$)1)$)+0$*$'$)1.$)32$),($)3&$)30$)0$$*$.$)0-$)2/$)3+$)3)$)33$*$'$)3$$)3)$)3+$*$+$)2%$*$.$*$+$*%&$)2*$*%($)1)$)21$*$'$)1+$*%($*$2$).3$)3*$*$,$*$($)2*$)1&$)22$)2,$*$,$*%&$)1-$)00$)3($)1/$)1.$*%%$),)$*%($*$-$)3+$*%$$*$+$)3/$)3($*$2$)(*$*$2$)22$)2&$*$/$)2($*$+$)2*$*$,$)1+$*%%$*$/$*$)$)3,$*$,$)22$)1*$)2($*$%$)0/$*$2"
encoded_signature = "$*$+$)0$$)2+$)2,$)2*$)03$*$,$)21$*$%$)3/$)2)$)1.$)3)$*$,$)12$)3%$)1&$)2$$*%3$)2'$).*$)/&$)2&$)20$)1)$)2*$*%)$)2)$)3)$)2.$)3%$)21$)3&$)3&$)2*$)3'$)3,$)32$)01$).1$)2)$)3,$)30$)3$$)2*$)3&$)3+$)2%$)0%$)3%$*%,$)2.$)1'$)1-$*$&$)01$)2&$),+$)2,$)2.$*$/$)2'$)1.$)3'$*%$$)3+$)2'$)02$)21$)2%$*%.$)10$)1-$)3&$)20$*%$$)3'$)33$*$1$)2%$)2)$*$&$*$%$)1*$)0/$)1'$)3&$)2'$)3$$*$/$)2-$)32$)1&$)3,$)/($)2%$)3+$)3*$)3/$)1*$)0.$)3,$)2-$*$($*$'$*$-$)2/$*$*$)3,$)10$)3$$)2+$)20$)3*$*$'$)12$*$'$*$($*$/$*%.$)3($)3,$)3%$)2)$)02$)3-$)1,$)32$)3/$*$)$)23$)./$)2+$)33$)3.$)/0$)1+$)01$)-0$*$&$)0*$)2.$)23$)+($*%($*$0$*$+$*$/$)32$)3'$)2'$)2&$)32$*%%$*$1$)/&$)30$*$2$)21$)2*$)/1$*$($)22$*$2$)3)$*%$$)2)$*$$$)31$)3*$)3&$)23$)33$)2)$)3*$*$&$)3*$)01$)3%$).3$)31$*$&$)3+$)3-$)0)$)2*$)1)$)1.$)3&$*%%$*$+$)0.$)33$*$)$*$/$*$0$*$&$*%*$)3+$)1.$)0+$)2'$)3)$)2+$)1,$)30$*%*$)3-$)31$)2'$*$$$*(($*+'$*&0$*-0$*-/$**0$*&($*&&$*&0$)32$*%*$)3+$)3'$*$.$*%3$*$$$*&+$)32$)3,$*$+$)3/$*$0$)3.$)3,$)0$$*$2$*$%$*$'$)2'$)10$*%*$)0.$)3'$*%/$*%'$*$$$*%-$*%0$*'&$*&+$*%%$)3%$*$1$)02$*$)$).0$)3&$*&)$*%,$*&$$*$3$*&($)3-$*$,$)1&$*%1$)3/$*%2$*%+$)33$)3($*%,$*&&$)1+$*%'$*&2$*$0$)33$)2)$)3-$)3*$)2'$)3.$*%'$*%$$*%*$*&*$)3'$*%,$)3-$*%($*&($*$-$*$%$*$%$*&($)30$*%3$*$/$*%&$*%*$*%,$*&'$)2%$*%-$*$)$*$&$*%-$*$/$*&,$*%%$*&($*&%$*&0$*&%$*%,$*)&$*&,$*)1$*).$*+%$*.$$*-2$*-/$*.0$*-3$*-$$*)2$**3$**'$**-$*)/$**+$*+2$*(($*(0$**($*+%$*'*$**$$*'($*&1$*'2$*&+$*&&$*')$*(+$*&3$*%($*&0$*'*$*&%$*&/$*$/$)3/$*&,$(&,$*$1$*$)$*$2$*&($)32$)2%$)33$*%)$*$1$)3.$)&+$)3/$)32$)33$*%($*%&$*$+$).3$)3&$*%%$*%$$)13$*%&$)32$*$1$)3+$)30$)3.$)3-$)2+$*$*$).2$*$.$)3*$)2$$*$%$*$'$*%,$)2.$*$-$)3-$)13$)/.$)1.$)3&$)2.$)33$*$'$*$+$*$.$)3'$)2+$)2.$*$/$)0'$).&$)3*$*%1$)3&$)0($)2&$*$*$*%3$*%2$*$+$)3'$*&.$*%$$*$0$*&,$*%*$*%+$*(($*(0$*,-$*,%$*0'$*2%$+'+$+0.$,)-$-$+$-)0$-.2$-1*$-20$-/.$-,2$-.+$-2/$.&.$.'*$.(%$.()$-1/$-&($,32$,*1$,&+$+3($+/1$+*3$+(*$*02$*12$*0)$*.,$*-($*,3$*,2$*)3$*))$*'3$*&+$*&-$*$1$*%,$*&'$)0*$*%+$*&.$)22$*$*$)30$*&%$*$2$*$.$*%)$)22$)21$*&)$*%.$)2'$)1*$*&'$)31$)3%$)3,$*$-$)20$*&%$*%$$)2'$*$*$)0,$)3-$*%&$)//$)3%$*$0$)3)$)2/$*&+$*%.$*%$$*(+$*%)$**)$*(1$***$*,)$**3$*++$*)+$*,3$*-/$*-)$*..$*/3$*1($*2%$*12$*33$*2($*3-$*1-$+$1$*3($+'($+%/$+&1$+%'$+%*$*0'$*.)$*..$*+)$*0)$*.*$*3'$+&($+%1$+$+$+$,$*1+$*/-$*,.$**1$*-$$*,%$*,($*))$*+,$*0*$*.+$*1'$*03$*.+$*-,$*+0$*,)$*)&$*),$*(1$*(+$*+$$**,$**$$*)3$*-2$*-1$*,2$*1($+&2$+-'$,+3$.,%$000$3()%$/0%%0.%%.+%$)/$2/%$1&*$/+&$.3)$.&'$-.($,12$,**$+3.$+.,$++-$*30$+'3$+&'$+%&$+'1$+(1$*2'$++$$++$$+'+$++$$+*($+*-$+.2$+-$$+*'$++1$+.,$+,&$+)&$+)3$+*%$+*%$+*%$+-,$+/&$+3($+0,$+0-$++3$+'-$*2/$*++$*,/$***$*%%$*)$$*$0$*'.$*'*$*%&$*%/$*%+$*$%$*$*$*%,$*(&$*&.$*'($*$%$*(($*&($*',$*',$*'($*&,$*'-$*$3$*(0$)3%$*(.$*&)$*'0$*)/$*)'$)1-$*+/$**.$*,$$*,3$*-&$**,$*(.$*)/$*))$*)2$*(3$)0'$*%/$*)1$*(0$*%+$*(0$*&/$*)'$*'/$*('$*%'$*$*$*)'$*'+$*),$*)+$*%+$*)+$*)-$*'$$*'$$*'2$*&0$*'+$*$.$*&,$*'3$*&3$*&0$*&2$*&,$*&/$*%3$*&/$*&2$*$'$)1*$*%%$*%*$*%2$*$&$)33$*%($*$/$*$-$*',$*%2$*$&$*&-$)31$*$.$*%1$*&3$*%$$*&*$*%($*&'$*%*$*%,$*&$$*&2$*%+$*$.$*&3$*%+$*$.$*($$***$*)1$*)&$*'($*'/$*%'$*$.$)10$*&'$)1/$)0*$*&2$*%1$*(3$*&3$*'1$*%($*%)$*&2$*%+$)3/$*$,$*%1$)32$)/,$)2,$*$0$)32$*$&$)-2$)3-$*$'$*%1$*%*$*'%$*&/$*(-$*)%$*,($*-3$*.-$*/3$*3($*3,$*10$*/%$*-0$*0($*.,$*,)$*/'$*)3$*.)$*/&$*)+$*(+$*'/$*'.$)/3$)01$)1,$)1)$)3'$*$'$)33$)3-$*&)$)3'$)10$)0/$)3)$)3/$)2)$).'$)2)$)3/$)3&$)12$)1,$*$'$)1*$*$($)21$)0.$)21$)3'$)2.$)11$*$+$)3+$)2*$*$-$*$$$*$'$*$3$)3/$*$($*%*$)22$)3&$*$,$)/3$)-+$)3&$*$*$*%*$)2.$)3.$)03$)20$*%*$*$+$*$)$*$%$)23$*&&$)32$)3%$)2($)2*$)10$)2,$)3/$)2-$)00$*$-$*$*$)0+$*$2$)3-$)31$)3*$)20$*$%$)33$*%*$*%+$)2,$)3'$)/&$)*.$)-*$)2-$*$,$)3)$*$.$)20$)3+$)1+$)30$)1-$)2/$)23$*$($)30$*$.$)2-$)20$*$)$*$-$*$&$*$%$)3*$)/,$*$.$).%$*$&$)3,$*$1$)3+$*%&$)3.$)32$)2'$).-$)32$*$'$*%$$*$,$)3($)20$)1-$*$*$*%,$)23$)2($)1'$*%+$*$($*%0$)23$*%,$)31$)2%$*%($)-)$*$)$)3.$)32$*$/$)1&$)+0$*$.$)10$)30$),($)21$)32$)/3$*$0$)0-$)22$)3($)3+$)32$*$%$)20$)3*$)3/$*$($)13$*$.$*$.$*$2$)2)$*$2$)1%$)23$*$*$)1.$*$2$*$0$)./$)3)$*$)$)32$)2*$)1'$)22$)2)$*$,$*$1$)1($)1%$)3'$)11$)1/$*$0$),*$*%,$*$.$)3)$*$1$*$/$)3-$)3)$*$1$)($$*$1$)3%$)2&$*$.$)2'$*$'$)2&$*$'$)1($*%$$*$/$*$&$)3'$*$'$)20$)1)$)13$)32$)0/$*$1"
def drop_and_create():

	#RAMS
	RAMS.execute_sql('DROP TABLE IF EXISTS voxel;')
	RAMS.execute_sql('DROP TABLE IF EXISTS spectrum;')
	RAMS.execute_sql('DROP TABLE IF EXISTS scan;')

	RAMS.execute_sql(\
	'''
	CREATE TABLE scan( id INT NOT NULL AUTO_INCREMENT,
	start_time INT, white_bal TEXT, PRIMARY KEY(id) );
	''')
	RAMS.execute_sql(\
	'''
	CREATE TABLE spectrum( id INT NOT NULL AUTO_INCREMENT, time INT, exposure INT, 
	signature TEXT, scan_id INT , PRIMARY KEY(id), FOREIGN KEY (scan_id) REFERENCES scan(id) );
	''')
	RAMS.execute_sql(\
	'''
	CREATE TABLE voxel( id INT NOT NULL AUTO_INCREMENT, time INT, x SMALLINT, y SMALLINT, z SMALLINT, 
	scan_id INT, spectrum_id INT REFERENCES spectrum(id) , PRIMARY KEY(id),
	FOREIGN KEY (spectrum_id) REFERENCES spectrum(id));
	''')
	#GROUND
	GROUND.execute_sql('DROP TABLE IF EXISTS voxel;')
	GROUND.execute_sql('DROP TABLE IF EXISTS spectrum;')
	GROUND.execute_sql('DROP TABLE IF EXISTS scan;')

	GROUND.execute_sql(\
	'''
	CREATE TABLE scan( id INT NOT NULL AUTO_INCREMENT, start_time INT, white_bal TEXT, PRIMARY KEY(id) );
	''');
	GROUND.execute_sql(\
	'''
	CREATE TABLE spectrum( id INT NOT NULL AUTO_INCREMENT, time INT, signature TEXT,
	red INT, green INT, blue INT, scan_id INT, PRIMARY KEY(id),FOREIGN KEY (scan_id) REFERENCES scan(id) );
	''')
	GROUND.execute_sql(\
	'''
	CREATE TABLE voxel( id INT NOT NULL AUTO_INCREMENT, time INT, x SMALLINT, y SMALLINT, z SMALLINT,
	scan_id INT, spectrum_id INT, PRIMARY KEY(id), FOREIGN KEY (spectrum_id) REFERENCES spectrum(id) );
	''')


def insert_many(spectrum_count, voxels_count, scan_id):
	ran = random.randint
	for s in range(spectrum_count):	

			query = "insert into spectrum ( time, exposure, signature, scan_id) values (%s,%s,%s,%s);"
			values = (1,1, encoded_white_bal, scan_id)
			inserted = RAMS.execute_sql(query, values)
			# inserted = RAMS.execute_sql(f'insert into spectrum ( time, exposure, signature, scan_id)\
			# 							 values (1,{ran(1,20)},{ran(20,30)},{scan_id});')
			s_id = inserted.lastrowid
			print('inserted spectrum:', s_id)
			time.sleep(2)
			for i in range(voxels_count):
				x = random.randint(-50,50)
				y = random.randint(-50,50)
				z = random.randint(-50,50)
				query = "insert into voxel( time, x, y,z,spectrum_id) values (%s,%s,%s,%s,%s);"
				values = (0,x,y,z,s_id)
				RAMS.execute_sql(query, values)
				# RAMS.execute_sql(f'insert into voxel ( time, x,y,z,spectrum_id) values\
				# 					 (0,{x},{y},{z},{s_id});')
				time.sleep(0)

def fill():

	query = "INSERT INTO scan (start_time, white_bal) VALUES (%s,%s);"
	values = (99, encoded_white_bal)
	inserted = RAMS.execute_sql(query, values)
	scan_id = inserted.lastrowid
	time.sleep(5)
	insert_many(spectrum_count=20, voxels_count=100, scan_id=scan_id)


def main():
	print('dropping and rebuilding tables..')
	drop_and_create()
	print('tables clean..')
	print('population with randomized data..')
	fill()
	print('finished.')






# def Process(signature):
# 	print('proccessing..', signature)
# 	r,g,b = 255,0,0
# 	return r,g,b

# ################ data flow for db transfer ################

# def get_latest_spectrum(scan_id):
# 	rams_cursor = RAMS.execute_sql(f"SELECT * FROM spectrum WHERE scan_id = {scan_id}\
# 									ORDER BY id DESC LIMIT 1;")
# 	result = rams_cursor.fetchone()
# 	print('get latest',result)
# 	if result:
# 		return Spectrum._make(result)
# 	return None


# def monitor(scan_id): #accepts scan_id from RAMS 
# 	last_seen = None
# 	while True:
# 		latest = get_latest_spectrum(scan_id)
# 		print('monitor..', scan_id, latest)
# 		if latest and latest.id != last_seen:
# 			last_seen = latest.id
# 			spectrum_queue.put(latest) # When new spectrum, put in queue namedtuple of record
# 		time.sleep(POLL_INTERVAL)  # Ideal polling time, 400ms?


# def commit_voxels_for(spectrum, ground_scan_id):
# 	rams_cursor = RAMS.execute_sql(f'SELECT * FROM voxel WHERE spectrum_id = {spectrum.id};')
# 	voxels = map( Voxel._make, rams_cursor.fetchall() )
# 	print('inserting spectrum to GROUND.. with scan_id' , ground_scan_id)
# 	#######################################
# 	## add processing here to get R G B  ##
# 	#  with input: spectrum.signature     #
# 	#	Process is a stub         		  #
# 	#######################################
# 	R,G,B = Process(spectrum.signature)

# 	inserted = GROUND.execute_sql(f"INSERT INTO spectrum\
# 									(time, signature, red, green, blue, scan_id) VALUES\
# 						({spectrum.time}, {spectrum.signature}, {R},{G},{B}, {ground_scan_id});")

# 	new_spec_id = inserted.lastrowid
# 	print('inserting Voxels to GROUND..with spectrum id..', new_spec_id)
# 	with GROUND.atomic():
# 		for v in voxels:
# 			GROUND.execute_sql(f'INSERT INTO voxel (time, x, y, z, spectrum_id, scan_id)\
# 								VALUES ({v.time},{v.x},{v.y},{v.z},{new_spec_id},{ground_scan_id});')
		
# def consume_spectra(ground_scan_id):
# 	finished_spectrum = None
# 	while True:
# 		if finished_spectrum == None:
# 			finished_spectrum = spectrum_queue.get() # Dont progress til grab first spectrum
# 		print('got first')
# 		latest_spectrum = spectrum_queue.get() # block execution until grab second
# 		print('calling commit..')
# 		commit_voxels_for(finished_spectrum, ground_scan_id) # Antecedent spectrum

# 		finished_spectrum = latest_spectrum


# ####### end data flow for db transfer ############################

# POLL_INTERVAL = 0.4 # Seconds
# spectrum_queue = Queue()

# # These are micro-classes to use as models instead of peewee models, way more efficient
# # they just map returned db records to field names and are part of standard library
# Scan = namedtuple('Scan', ['id','start_time','white_bal']) 
# Spectrum = namedtuple('Spectrum', ['id', 'time', 'exposure', 'signature','scan_id'])
# Voxel = namedtuple('Voxel', ['id','time','x','y','z','scan_id','spectrum_id'] )

# def main():

# 	rams_cursor = RAMS.execute_sql("SELECT * FROM scan ORDER BY id DESC LIMIT 1;") # Latest scan
# 	latest_scan = Scan._make( rams_cursor.fetchone() ) # Turn into Scan object 
	
# 	### process scan here ####
# 	### end process scan #####

# 	# Put scan in ground db
# 	print(latest_scan.white_bal)
# 	rams_scan_id = latest_scan.id

# 	inserted = GROUND.execute_sql(f'INSERT INTO scan (start_time, white_bal)\
# 									VALUES ( {latest_scan.start_time},"{latest_scan.white_bal}" );')
# 	ground_scan_id = inserted.lastrowid

# 	t = threading.Thread(target=monitor, args=(rams_scan_id,))
# 	t.daemon = True
# 	t.start()

# 	consume_spectra(ground_scan_id) # runs forever




# 	# w = Scan.white_bal
# 	# recovered_white_bal = [ decode(w[2*i], w[2*i+1]) 
# 	# 						for i in range(29,980) ] # python iteration sugar

# 	#rams_cursor = RAMS.execute_sql(f"SELECT * FROM spectum WHERE scan = {latest_scan.id};")


# 	#spectra = map(Spectrum._make, rams_cursor.fetchall()) # Turn all records into Spectrum objects




	



	
	

# ### Models to represent records in DB as objects ######################################    
# # class BaseModel(Model):
# #     class Meta:
# #         database = RAMS
# # class Scan(BaseModel):
# #     start_time = IntegerField()
# #     white_bal = TextField()
# # class Spectrum(BaseModel):
# # 	scan = ForeignKeyField(Scan, related_name='id')
# #     time = IntegerField()
# #     spectrum = TextField()
# # class Voxel(BaseModel):
# # 	scan = ForeignKeyField(Scan, related_name='id')
# # 	spectrum = ForeignKeyField(Spectrum, related_name='id')
# #     time = IntegerField()
# #     x = IntegerField()
# #     y = IntegerField()
# #     z = IntegerField()


# # class RamsBase(Model):
# # 	class Meta:
# # 	        database = RAMS

# # class Scan(RamsBase):
# # 	start_time = IntegerField()
# #     white_bal = TextField()
# # class Spectrum(RamsBase):
# # 	time = IntegerField()
# # 	signature = TextField()
# # 	scan_id = ForeignKeyField(Scan, related_name='spectra')
# # class Voxel(RamsBase):
# # 	time = IntegerField()
# # 	x = SmallIntegerField()
# # 	y = SmallIntegerField()
# # 	z = SmallIntegerField()
# # 	spectrum_id = ForeignKeyField(Spectrum, related='voxels')
# # 	scan_id = ForeignKeyField(Scan, related ='voxels')


# #define CREATE_SCANS "CREATE TABLE scans( id INT NOT NULL AUTO_INCREMENT, start_time INT, white_bal TEXT, PRIMARY KEY(id) )"
# #define CREATE_SPECTRA "CREATE TABLE spectra( id INT NOT NULL AUTO_INCREMENT, scan INT REFERENCES scans(id), time INT, exposure INT, spectrum TEXT, PRIMARY KEY(id) )"
# #define CREATE_VOXELS "CREATE TABLE voxels( scan INT REFERENCES scans(id), spectrum INT REFERENCES spectra(id), time INT, x INT, y INT, z INT )"


if __name__ == "__main__":
	main()	


#	c language decoder
#
# 	for(int i=0; i<PIXELS; i++){
#		high = (string[2*i]-start)<<7;
#		low = (string[2*i+1]) - start;
#		output[i] = high + low;
#	}



