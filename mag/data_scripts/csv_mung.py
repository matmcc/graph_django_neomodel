import gzip
from timeit import default_timer as timer

filename = "E:\Downloads\Papers.txt"

# use next(gen) to explore lines in large gzipped csv or txt / or test if string in line (add counter for line no)
gen = (r for r in gzip.open(filename, 'rt'))

last = None
count = 0
i_count = 0
ids = set()

t_start = timer()
t1 = timer()

with open(filename, 'rb+') as f:
    for line in f:
        if b'CONTROLLER FOR OPENING AND CLOSING MEMBER' in line:
            print(line)
        # first, second = line.split()
        # ids.add(first)
        # ids.add(second)
        # count += 1
        # if count == 10000:
        #     for id in ids:
        #         outfile.write(id + '\n')
        #     count = 0
        #     i_count += 1
        #     print(f'{i_count} : {(timer() - t1)}')
        #     t1 = timer()
    # for id in ids:
    #     outfile.write(id + '\n')

print(f'{timer() - t_start}')
print('done')
