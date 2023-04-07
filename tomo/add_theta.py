import numpy as np 


num_dark = 19
num_flat = 10

collect_start = True
collect_end = True

a = []
if(collect_start):
	a.append(np.arange(num_dark))
	a.append(np.arange(num_flat))

a.append(np.arange(25))
a.append(np.arange(26,50))
a.append(np.arange(100,150))


if(collect_end):
	a.append(np.arange(num_dark))
	a.append(np.arange(num_flat))

a = np.concatenate(a).ravel()+1

ids_start = [0,*np.where(a[1:]-a[:-1]<0)[0]+1]

if(len(ids_start)==1):
	print(a)
else:	
	flg_start = 0
	if(collect_start and num_dark>0):
		flg_start += 1
	if(collect_start and num_flat>0):
		flg_start += 1
	print(a[ids_start[flg_start]:ids_start[flg_start+1]])