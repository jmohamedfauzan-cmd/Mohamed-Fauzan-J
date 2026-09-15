# =============================================================
#  Routine Singly Linked List – All Basic Operations (Python)
# =============================================================


class Node:
    """Represents a single node in the linked list."""

    def __init__(self, data):
        self.data = data   # Value stored in the node
        self.next = None   # Pointer to the next node


class LinkedList:
    """Singly Linked List with all common operations."""

    def __init__(self):
        self.head = None   # Head (first node) of the list

    # ── INSERT ──────────────────────────────────────────────

    def insert_at_beginning(self, data):
        """Insert a new node at the front of the list.  O(1)"""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def insert_at_end(self, data):
        """Append a new node at the tail of the list.  O(n)"""
        new_node = Node(data)
        if self.head is None:          # Empty list edge case
            self.head = new_node
            return
        current = self.head
        while current.next:            # Walk to the last node
            current = current.next
        current.next = new_node

    def insert_at_position(self, data, position):
        """Insert at a given 0-based position.  O(n)"""
        if position == 0:
            self.insert_at_beginning(data)
            return
        new_node = Node(data)
        current = self.head
        for _ in range(position - 1):
            if current is None:
                raise IndexError("Position out of range")
            current = current.next
        if current is None:
            raise IndexError("Position out of range")
        new_node.next = current.next
        current.next = new_node

    # ── DELETE ──────────────────────────────────────────────

    def delete_by_value(self, data):
        """Remove the first node whose data matches.  O(n)"""
        if self.head is None:
            print("List is empty.")
            return
        if self.head.data == data:     # Remove head
            self.head = self.head.next
            return
        current = self.head
        while current.next and current.next.data != data:
            current = current.next
        if current.next is None:
            print("Value", data, "not found in the list.")
        else:
            current.next = current.next.next  # Bypass target node

    def delete_at_position(self, position):
        """Remove the node at a given 0-based position.  O(n)"""
        if self.head is None:
            print("List is empty.")
            return
        if position == 0:              # Remove head
            self.head = self.head.next
            return
        current = self.head
        for _ in range(position - 1):
            if current.next is None:
                raise IndexError("Position out of range")
            current = current.next
        if current.next is None:
            raise IndexError("Position out of range")
        current.next = current.next.next  # Bypass target node

    # ── SEARCH ──────────────────────────────────────────────

    def search(self, data):
        """Return 0-based index of first occurrence, or -1.  O(n)"""
        current = self.head
        index = 0
        while current:
            if current.data == data:
                return index
            current = current.next
            index += 1
        return -1  # Not found

    # ── TRAVERSE ────────────────────────────────────────────

    def traverse(self):
        """Print all node values from head to tail.  O(n)"""
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        print(" -> ".join(elements) + " -> NULL")

    # ── REVERSE ─────────────────────────────────────────────

    def reverse(self):
        """Reverse the linked list in-place.  O(n)"""
        prev = None
        current = self.head
        while current:
            next_node = current.next   # Save next before overwriting
            current.next = prev        # Reverse the link
            prev = current             # Move prev forward
            current = next_node        # Move current forward
        self.head = prev

    # ── LENGTH ──────────────────────────────────────────────

    def length(self):
        """Return the total number of nodes in the list.  O(n)"""
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count


# =============================================================
#  Demo / Driver Code
# =============================================================

ll = LinkedList()

# 1. Insert at end
for val in [10, 20, 30, 40, 50]:
    ll.insert_at_end(val)
print("After inserting 10 20 30 40 50 at end:")
ll.traverse()
# 10 -> 20 -> 30 -> 40 -> 50 -> NULL

# 2. Insert at beginning
ll.insert_at_beginning(5)
print("\nAfter inserting 5 at beginning:")
ll.traverse()
# 5 -> 10 -> 20 -> 30 -> 40 -> 50 -> NULL

# 3. Insert at position 3
ll.insert_at_position(25, 3)
print("\nAfter inserting 25 at position 3:")
ll.traverse()
# 5 -> 10 -> 20 -> 25 -> 30 -> 40 -> 50 -> NULL

# 4. Search
print("\nSearch 30  -> index:", ll.search(30))   # 4
print("Search 99  -> index:", ll.search(99))    # -1

# 5. Length
print("\nLength of list:", ll.length())          # 7

# 6. Delete by value
ll.delete_by_value(25)
print("\nAfter deleting value 25:")
ll.traverse()
# 5 -> 10 -> 20 -> 30 -> 40 -> 50 -> NULL

# 7. Delete at position 0 (head)
ll.delete_at_position(0)
print("\nAfter deleting node at position 0:")
ll.traverse()
# 10 -> 20 -> 30 -> 40 -> 50 -> NULL

# 8. Reverse
ll.reverse()
print("\nAfter reversing the list:")
ll.traverse()
# 50 -> 40 -> 30 -> 20 -> 10 -> NULL
