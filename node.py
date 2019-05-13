import json
import time

from hashlib import sha256


class Block:
    def __init__(self, index_, transactions_, timestamp_, previous_hash, nonce_=0):
        self.index_ = index_
        self.transactions_ = transactions_
        self.timestamp_ = timestamp_
        self.previous_hash = previous_hash
        self.nonce_ = nonce_

    def compute(self):
        """
        Return the hash of the block
        """
        block_ = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_.encode()).hexdigest()


def proof_of_work(block_):
    block_.nonce_ = 0

    computed_hash = block_.compute()
    while not computed_hash.startswith('0' * Chain.difficulty):
        block_.nonce_ += 1
        computed_hash = block_.compute()

    return computed_hash


class Chain:
    difficulty = 2

    def __init__(self):
        self.transactions_remaining = []
        self.chain_ = []

    def first_block(self):
        first_block = Block(0, [], time.time(), "0")
        first_block.hash_ = first_block.compute()
        self.chain_.append(first_block)

    @property
    def last_block(self):
        return self.chain_[-1]

    def insert_block(self, block_, pow_):
        previous_hash = self.last_block.hash_

        if previous_hash != block_.previous_hash:
            return False
        elif not Chain.is_valid_pow(block_, pow_):
            return False

        block_.hash_ = pow_
        self.chain_.append(block_)
        return True

    def insert_new_transaction(self, transaction_):
        self.transactions_remaining.append(transaction_)

    @classmethod
    def is_valid_pow(cls, block_, hash_):
        return hash_.startswith('0' * Chain.difficulty) and hash_ == block_.compute()

    @classmethod
    def check_validity(cls, chain_):
        result = True
        previous_hash = "0"

        for block_ in chain_:
            hash_ = block_.hash_
            delattr(block_, "hash")
            if not cls.is_valid_pow(block_, block_.hash_) or previous_hash != block_.previous_hash:
                result = False
                break

            block_.hash_, previous_hash = hash_, hash_

        return result

    def mine(self):
        if not self.transactions_remaining:
            return False

        last_block = self.last_block

        new_block = Block(index_=last_block.index_ + 1,
                          transactions_=self.transactions_remaining,
                          timestamp_=time.time(),
                          previous_hash=last_block.hash_)

        pow_ = proof_of_work(new_block)
        self.insert_block(new_block, pow_)
        self.transactions_remaining = []

        return new_block

