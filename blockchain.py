import hashlib, time
from uuid import uuid4
from typing import Dict, List

class Wallet:
    def __init__(self, address):
        self.address = address
        self.balance = 0

    def receive_reward(self, amount: int):
        self.balance += amount

    def __getitem__(self, value):
        return self.address
    
    def __setitem__(self, key):
        self.address = key

    def __contain__(self, key):
        return self.address == key
    
    def __eq__(self, value):
        return self.address == value
    
    def __repr__(self):
        return f'Wallet({self.address}, {self.balance})'

class Block:
    def __init__(self, index, timestamp, data, previous_hash, miner_address, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.miner_address = miner_address
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        hash_str = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        sha.update(hash_str.encode('utf-8'))
        return sha.hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def __repr__(self):
        return f'Block({self.index}, {self.timestamp}, "{self.data}", {self.previous_hash}, {self.nonce}, {self.hash})'

    def __hash__(self):
        return self.hash

class Blockchain:
    def __init__(self, difficulty=1, difficulty_correction_interval=10, target_time=30, initial_reward=100, halving_interval=10, wallets: Dict[str, Wallet]={}):
        self.chain: List[Block] = []
        self.time: List[float] = []
        self.difficulty = difficulty # сложность майнинга (количество ведущих нулей в хэше)
        self.difficulty_correction_interval = difficulty_correction_interval # через какое кол-во блоков корректировать сложность майнинга в соответствии с целевым временем
        self.target_time = target_time # секунд цикла майнинга
        self.initial_reward = initial_reward  # вознаграждение за майнинг блока
        self.reward_amount = self.initial_reward  # вознаграждение за майнинг блока
        self.halving_interval = halving_interval # как часто уменьшать награду за майнинг блока
        self.wallets = wallets  # словарь адресов кошельков и их балансов
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), "Genesis Block", "0", None)
        self.chain.append(genesis_block)

    def add_block(self, new_data, miner_address):
        previous_block = self.get_latest_block()
        new_index = previous_block.index + 1
        new_timestamp = time.time()
        new_block = Block(new_index, new_timestamp, new_data, previous_block.hash, miner_address)
        start_time = time.time() # start time
        new_block.mine_block(self.difficulty)
        actual_time = round(time.time() - start_time, 3) #end_time - start_time
        print(actual_time)
        self.chain.append(new_block)
        self.payout_reward(miner_address)
        self.time.append(actual_time)
        if self.get_latest_block().index % self.halving_interval == 0: self.calculate_new_reward()
        if self.get_latest_block().index % self.difficulty_correction_interval == 0: self.calculate_new_difficulty()

    def payout_reward(self, miner_address):
        if miner_address in self.wallets:
            self.wallets[miner_address].receive_reward(self.reward_amount)
        else:
            self.wallets[miner_address] = Wallet(miner_address)
            self.wallets[miner_address].receive_reward(self.reward_amount)

    def get_latest_block(self):
        return self.chain[-1]

    def is_valid_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def calculate_new_difficulty(self):
        actual_time = sum(self.time) / len(self.time)
        up_time, down_time, actual_time = round(self.target_time * 1.2, 3), round(self.target_time * 0.8, 3), round(actual_time, 3)
        print(self.time, 'seconds')
        print(f'Actual time: {actual_time}, Target time: {self.target_time}, Difficulty: {self.difficulty}')
        if actual_time > up_time: self.difficulty = self.difficulty - 1
        elif actual_time < down_time: self.difficulty = self.difficulty + 1
        print(f'{up_time} > {actual_time} > {down_time} - {up_time > actual_time > down_time}\tDifficulty: {self.difficulty}')
        self.time = []
    
    def calculate_new_reward(self):
        print('Current reward:', self.reward_amount)
        self.reward_amount = self.initial_reward / (2 ** (self.get_latest_block().index // self.halving_interval))
        print('Correction reward:', self.reward_amount)

    def __repr__(self):
        return f'Blockchain:\n\tlength: {len(self.chain)} blocks\n\tdifficulty: {self.difficulty}\n\tdifficulty correction interval: {self.difficulty_correction_interval}\n\ttarget time: {self.target_time}\n\tinitial reward: {self.initial_reward}\n\thalving interval: {self.halving_interval}\n\tminers: {self.wallets}'

# Создание блокчейна
wallet = Wallet("Alexey Ustinov")
blockchain = Blockchain(difficulty=5, target_time=2, initial_reward=50, halving_interval=100, wallets={'Alexey Ustinov': wallet})
print('Blockchain has been initialized!\n', blockchain)

startt_time = time.time()
for i in range(50):
    blockchain.add_block(f"Transaction: {uuid4()}", 'Alexey Ustinov')
endd_time = time.time()

print(blockchain.is_valid_chain())
print(len(blockchain.chain), "blocks in the chain")
print(sum([i.nonce for i in blockchain.chain]) / len(blockchain.chain), "average nonce per block")
print(f'Alexey Ustinov balance: {blockchain.wallets['Alexey Ustinov'].balance} coins')
print(endd_time - startt_time, "seconds")
