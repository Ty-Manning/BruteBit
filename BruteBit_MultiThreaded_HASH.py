import hashlib
import random
import os.path
import base58
from bitcoinlib.wallets import Wallet, wallet_delete
from tqdm import tqdm
import secrets
from ecdsa import SECP256k1, SigningKey
import ecdsa
import time
from multiprocessing import Process, Queue, Value

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
#Create or load hash
def create_or_load_hash_table(file_path, addresses):
    hash_table_file = file_path + '.hash'
    if os.path.exists(hash_table_file):
        # If hash table file exists, overwrite it
        os.remove(hash_table_file)
        
    hash_table = set()
    print("Creating hash table...")
    with open(hash_table_file, 'w') as f:
        with tqdm(total=len(addresses), desc='Creating Hash Table', unit=' Addresses') as pbar:
            for address in addresses:
                hash_table.add(address)
                f.write(address + '\n')  # Write address to hash table file
                pbar.update(1)
    print("Hash table created and saved to file.")
    del addresses  # Delete the addresses list to free up memory
    print("Hash table creation complete.")
    return hash_table

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

    # Step 6: Derive Ethereum address
    public_key_hash_ethereum = hashlib.sha3_256(public_key).digest()
    ethereum_address = public_key_hash_ethereum[-20:].hex()


    return legacy_address, segwit_address, ethereum_address,

# Function to generate and test private keys
def generate_and_test_keys(hash_table, progress_queue, total_addresses_checked):
    addresses_checked = 0
    start_time = time.time()
    while True:
        private_key = generate_private_key()
        legacy_address, segwit_address, ethereum_address = private_key_to_address(private_key)
        
        # Check if addresses are in the hash table
        if legacy_address in hash_table:
            with open('found.txt', 'a') as found_file:
                found_file.write(f"Private Key: {private_key}\nLegacy Address: {legacy_address}\n")
        if segwit_address in hash_table:
            with open('found.txt', 'a') as found_file:
                found_file.write(f"Private Key: {private_key}\nSegWit Address: {segwit_address}\n")
        if ethereum_address in hash_table:
            with open('found.txt', 'a') as found_file:
                found_file.write(f"Private Key: {private_key}\nETH Address: {ethereum_address}\n")

        addresses_checked += 1
        total_addresses_checked.value += 1

        # Print status every 10 seconds
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10:
            keys_per_second = addresses_checked / elapsed_time
            progress_queue.put(addresses_checked)
            start_time = time.time()  # Reset start time
            addresses_checked = 0  # Reset addresses checked count

# Function to update progress
def update_progress(progress_queue, total_addresses_checked):
    addresses_checked_total = 0
    start_time = time.time()
    while True:
        addresses_checked = progress_queue.get()
        addresses_checked_total += addresses_checked
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10:
            keys_per_second = addresses_checked_total / elapsed_time
            print(f"Total Addresses Checked: {total_addresses_checked.value}, Keys/s: {keys_per_second:.2f}")
            start_time = time.time()  # Reset start time
            addresses_checked_total = 0  # Reset total addresses checked count

# Main function
def main():
    input_file = '120MEverything.txt'  # Change this to your input file

    addresses = load_addresses(input_file)

    # Create or load hash table
    hash_table = create_or_load_hash_table(input_file, addresses)

    # Shared value for total addresses checked
    total_addresses_checked = Value('i', 0)

    # Queue for progress updates
    progress_queue = Queue()

    # Set number of processes
    num_processes = 16

    # Create and start progress update process
    progress_process = Process(target=update_progress, args=(progress_queue, total_addresses_checked))
    progress_process.start()

    # Create and start worker processes
    processes = []
    for _ in range(num_processes):
        process = Process(target=generate_and_test_keys, args=(hash_table, progress_queue, total_addresses_checked))
        process.start()
        processes.append(process)

    # Wait for all worker processes to finish
    for process in processes:
        process.join()

    # Terminate progress update process
    progress_process.terminate()

# Execute the main function
if __name__ == "__main__":
    main()
