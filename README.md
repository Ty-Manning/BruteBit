Add a txt file with one address per line, if using ETH addresses then there should not be the 0x prefix. Change the address file in the code under main, variable input file.

Change number of threads under the main function under "num_processes" variable.

If you have a lot of free memory or are using a very small lookup file (less than a million or so addresses) then use the HASH version, this uses a hash table and is more reliable as well as much faster.
-Otherwise use the BLOOM version, this uses a bloom filter and may occasionally give false positives and works slightly slower.

NOTE FOR HASH TABLE: The first 10 minutes will be slower. I think this is because the entire hash table needs to be indexed as a set.


DISCLAIMER: This is made as a proof of concept. You almost certainly will not find the private key to a wallet. If you do, and you use it, that is theft. I do not condone theft.
