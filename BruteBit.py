import hashlib
import random
import os.path
import hashlib
import base58
from bitcoinlib.wallets import Wallet, wallet_delete
from pybloom_live import ScalableBloomFilter
from tqdm import tqdm
import secrets
from ecdsa import SECP256k1, SigningKey
import time

# Function to load addresses from file into a list
def load_addresses(file_path):
    addresses = []
    file_size = os.path.getsize(file_path)
    with open(file_path, 'r') as file:
        with tqdm(total=file_size, desc='Loading Addresses', unit='B', unit_scale=True) as pbar:
            for line in file:
                address = line.strip()
                addresses.append(address)
                pbar.update(len(line))
    return addresses

# Function to create or load a Bloom Filter
def create_or_load_bloom_filter(file_path, addresses=None):
    bloom_filter_file = file_path + '.blm' 
    if os.path.exists(bloom_filter_file):
        bloom_filter = ScalableBloomFilter.fromfile(open(bloom_filter_file, 'rb'))
    else:
        bloom_filter = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        if addresses:
            total_addresses = len(addresses)
            batch_size = 10000  # Adjust the batch size as needed
            num_batches = (total_addresses + batch_size - 1) // batch_size
            with tqdm(total=num_batches, desc='Creating Bloom Filter', unit=' Batches') as pbar:
                for i in range(0, total_addresses, batch_size):
                    batch = addresses[i:i+batch_size]
                    for address in batch:
                        bloom_filter.add(address)
                    pbar.update(1)
        bloom_filter.tofile(open(bloom_filter_file, 'wb'))
    return bloom_filter

# Function to generate a random private key
def generate_private_key():
    # Generate a random 256-bit (64-character) hexadecimal string
    return secrets.token_hex(32)

def private_key_to_address(private_key):
    # Step 1: Convert private key to WIF format
    wif_prefix = b'\x80'
    private_key_bytes = bytes.fromhex(private_key)
    wif_data = wif_prefix + private_key_bytes
    checksum = hashlib.sha256(hashlib.sha256(wif_data).digest()).digest()[:4]
    wif = base58.b58encode(wif_data + checksum).decode('utf-8')

    # Step 2: Derive public key from private key
    signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    verifying_key = signing_key.verifying_key
    public_key = b'\x04' + verifying_key.to_string()

    # Step 3: Hash the public key
    public_key_hash = hashlib.sha256(public_key).digest()
    ripemd160_hash = hashlib.new('ripemd160')
    ripemd160_hash.update(public_key_hash)
    hash160 = ripemd160_hash.digest()

    # Step 4: Create Legacy Address
    address_prefix = b'\x00'
    address_data = address_prefix + hash160
    checksum = hashlib.sha256(hashlib.sha256(address_data).digest()).digest()[:4]
    legacy_address = base58.b58encode(address_data + checksum).decode('utf-8')

    # Step 5: Create SegWit Address
    segwit_prefix = b'\x05'
    segwit_data = segwit_prefix + hash160
    checksum = hashlib.sha256(hashlib.sha256(segwit_data).digest()).digest()[:4]
    segwit_address = base58.b58encode(segwit_data + checksum).decode('utf-8')

    return legacy_address, segwit_address

#____________________________________________________________________________________________
# Main function
def main():
    input_file = 'address.txt'  # Change this to your input file

    # Load addresses from file into memory
    addresses = load_addresses(input_file)

    # Create or load a Bloom Filter
    bloom_filter = create_or_load_bloom_filter(input_file, addresses)

    # Set to keep track of tested private keys
    tested_private_keys = set()

    # Variable to keep track of the number of addresses checked
    addresses_checked = 0
    total_addresses_checked = 0

    # Variable to store the start time
    start_time = time.time()

    # Loop to generate and test private keys
    while True:
        # Generate a random private key
        private_key = generate_private_key()

        # Convert private key to addresses
        legacy_address, segwit_address = private_key_to_address(private_key)

        # Check if either address matches any address in the Bloom Filter
        if legacy_address in bloom_filter or segwit_address in bloom_filter:
            with open('found.txt', 'a') as found_file:
                found_file.write(f"Private Key: {private_key}\nLegacy Address: {legacy_address}\nSegWit Address: {segwit_address}\n\n")
        


        # Add tested private key to set
        tested_private_keys.add(private_key)

        # Increment the number of addresses checked
        addresses_checked += 1
        total_addresses_checked +=1

        # Print status every 10 seconds
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10:
            keys_per_second = addresses_checked / elapsed_time
            print(f"Addresses Checked: {total_addresses_checked}, Keys/s: {keys_per_second:.2f}")
            start_time = time.time()  # Reset start time
            addresses_checked = 0  # Reset addresses checked count

# Execute the main function
if __name__ == "__main__":
    main()
