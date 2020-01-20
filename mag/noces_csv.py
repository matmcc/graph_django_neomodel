import pandas as pd
import numpy as np

# location of big edge list csv
filename = "E:\Downloads\PaperReferences.txt.gz"

# Use pandas.read_csv: can read compressed csvs, and can iterate chunks to conserve
data_iterator = pd.read_csv(filename, delimiter='\t', chunksize=1000000, compression='gzip', dtype='Int64')
# usecols=[0] if you want to get an individual column in above

# Will collect unique id's - in effect a set - may have high memory requirements. Init as numpy array
unique_ids = np.zeros((0), dtype='Int64')

# Each chunk is a FileTextReader object
for data_chunk in data_iterator:
    # Convert to pandas dataframe to get unique items in each column
    df = pd.DataFrame(data_chunk)
    col0 = df.iloc[:, 0].unique()
    col1 = df.iloc[:, 1].unique()
    # Get set union of unique items
    chunk_unique_ids = np.union1d(col0, col1)
    # Set union of unique items from chunk and unique items from previous chunks
    unique_ids = np.union1d(unique_ids, chunk_unique_ids)
    print(len(unique_ids))

# Now have all unique ids
print('Unique ids created')
unique_ids = pd.Series(unique_ids)
print('unique Series created')
# Use pandas to write compressed csv
unique_ids.to_csv('E:\nodes.csv.gz', index=False, compression='gzip')
print('done')
