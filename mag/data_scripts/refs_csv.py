import csv

ids = set()


def iter_csv(filename):
    with open(filename, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        yield next(reader)


def csv_out(f_in, f_out):
    with open(f_in, "r", newline='') as csv_in, open(f_out, 'w', newline='') as csv_out:
        reader = csv.reader(csv_in, delimiter='\t')
        next(reader)
        writer = csv.writer(csv_out)
        last = None
        for row in reader:
            if last == row:
                print('last:'+last)
            else:
                print(row)
                last = row


# csv_in_generator = iter_csv('E:\Downloads\PaperReferences.txt')
csv_out('E:\Downloads\PaperReferences.txt', 'E:\PaperIds.csv')
print('Done')
