#Definition for a binary tree node.
from typing import Optional, List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    class SolContext:
        def __init__(self):
            self.result = []

    def _rec_traversal(self, current: Optional[TreeNode], sol_context: SolContext):
        if current is None:
            return

        self._rec_traversal(current.left, sol_context)
        sol_context.result.append(current.val)
        self._rec_traversal(current.right, sol_context)


    def inorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        context = Solution.SolContext()
        self._rec_traversal(root, context)

        return context.result

