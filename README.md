# BruteBit

This script checks a list of wallet addresses against a lookup file to find matches. It offers two methods: HASH and BLOOM, depending on your memory availability and lookup file size.

## Usage

1. **Prepare Input File:**
   - Create a text file (`addresses.txt`) with one wallet address per line. If using ETH addresses, omit the `0x` prefix.

2. **Configure the Script:**
   - Open the script and locate the `main` function.
   - Set the `input_file` variable to point to your `addresses.txt` file.

3. **Adjust Settings:**
   - In the `main` function, adjust the `num_processes` variable to specify the number of threads (parallel processes) to use.

4. **Choose Method:**
   - Decide between HASH and BLOOM methods:
     - **HASH:** Use for large memory and small lookup files (< 1 million addresses). It provides reliable and fast results but may have slower initial indexing.
     - **BLOOM:** Use for larger lookup files or limited memory situations. It employs a bloom filter and may occasionally produce false positives, running slightly slower.

## Important Notes

- **HASH Table Performance:** The script may have slower initial performance (up to 10 minutes) as it indexes the entire hash table.
- **DISCLAIMER:** This script is a proof of concept. Finding a private key through this method is highly unlikely and using any discovered private keys without permission is considered theft.
