from typing import Self
from typing import List

class TrieNode:
    #constat
    SIZE = ord('z') - ord('a') + 1

    def __init__(self, size = SIZE):
        self._next: List[Self] = [None] * size
        self._size: int = size
        self.is_end: bool = False

    def next_node(self, char: str) -> Self | None :
        code = ord(char) - ord('a')
        return self._next[code]

    def create_next(self, char: str) -> Self | None:
        code = ord(char) - ord('a')
        new_node = TrieNode(size = self._size)
        self._next[code] = new_node
        return new_node

class Trie:
    END_FLAG = "_END_"

    def __init__(self):
        self._root = TrieNode()

    def insert(self, word: str) -> None:
        current = self._root

        for char in word:
            next_node = current.next_node(char)
            if next_node is None:
                next_node = current.create_next(char)
            current = next_node

        current.is_end = True

    def _traverse(self, word: str) -> TrieNode | None:
        current = self._root

        for char in word:
            current = current.next_node(char)
            if current is None:
                break

        return current


    def search(self, word: str) -> bool:
        end = self._traverse(word)

        if end is None:
            return False

        return end.is_end

    def startsWith(self, prefix: str) -> bool:
        end = self._traverse(prefix)

        return end is not None

#Your Trie object will be instantiated and called as such:
word = 'abc'
prefix = 'ac'
obj = Trie()
param_2 = obj.search(word)
param_3 = obj.startsWith(prefix)

print(param_2, param_3)