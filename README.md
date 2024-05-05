Add a txt file with one address per line, if using ETH addresses then there should not be the 0x prefix. Change the address file in the code under main, variable input file.

Change number of threads under the main function under "num_processes" variable.

If you have a lot of free memory then use the HASH version, this uses a hash table and is more reliable as well as much faster.
-Otherwise use the BLOOM version, this uses a bloom filter and may occasionally give false positives and works slightly slower.


DISCLAIMER: This is made as a proof of concept. You almost certainly will not find the private key to a wallet. If you do, and you use it, that is theft. I do not condone theft.
