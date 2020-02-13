import gzip
from timeit import default_timer as timer

filename = 'D:\MAG_data\Papers.txt.gz'
out_file = "D:\MAG_data\PaperIds.txt.gz"

count = 0
t1 = timer()

with gzip.open(filename, 'rb') as in_file, gzip.open(out_file, 'wb') as f_out:
    line = in_file.readline()
    while line != "":
        out = line.split(b'\t', 1)[0]
        out += b'\t\r\n'
        f_out.write(out)
        count += 1
        # if count % 1000000 == 0:
        #     print(count)

print(f'Done! {count} lines written to {out_file}, in {timer() - t1} seconds')
