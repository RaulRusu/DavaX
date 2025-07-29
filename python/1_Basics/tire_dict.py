class Trie:
    END_FLAG = "_END_"

    def __init__(self):
        self._root = {}

    def insert(self, word: str) -> None:
        current = self._root

        for char in word:
            if char not in current:
                current[char] = {}
            current = current[char]

        current[Trie.END_FLAG] = True

    def _traverse(self, word):
        current = self._root

        for char in word:
            if char not in current:
                return None
            current = current[char]

        return current

    def search(self, word: str) -> bool:
        end = self._traverse(word)
        if end is None:
            return False

        return Trie.END_FLAG in end

    def startsWith(self, prefix: str) -> bool:
        end = self._traverse(prefix)

        return end is not None

#Your Trie object will be instantiated and called as such:
word = 'abc'
prefix = 'ac'
obj = Trie()
obj.insert(word)
param_2 = obj.search(word)
param_3 = obj.startsWith(prefix)

print(param_2, param_3)