from typing import List, Callable
from geometry import Point, Segment, Endpoint, Geometry

class MinHeap:
    """Generic min heap. comparator(a, b) should return True when a belongs before b."""
    def __init__(self, comparator: Callable[[object, object], bool]):
        self._data: List[object] = []
        self._before = comparator

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def peek_min(self):
        if self.is_empty():
            raise IndexError("Heap is empty")
        return self._data[0]

    def insert(self, item) -> None:
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def extract_min(self):
        if self.is_empty():
            raise IndexError("Heap is empty")

        minimum = self._data[0]
        last = self._data.pop()

        if self._data:
            self._data[0] = last
            self._sift_down(0)

        return minimum

    def remove(self, item) -> None:
        try:
            i = self._data.index(item)
        except ValueError:
            return

        last_index = len(self._data) - 1
        if i == last_index:
            self._data.pop()
            return

        self._data[i] = self._data.pop()

        if i > 0:
            parent = (i - 1) // 2
            if self._before(self._data[i], self._data[parent]):
                self._sift_up(i)
                return

        self._sift_down(i)

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self._before(self._data[i], self._data[parent]):
                self._data[i], self._data[parent] = (self._data[parent], self._data[i])
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self._data)
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = i

            if left < n and self._before(self._data[left], self._data[smallest]):
                smallest = left

            if right < n and self._before(self._data[right], self._data[smallest]):
                smallest = right

            if smallest == i:
                break

            self._data[i], self._data[smallest] = (self._data[smallest], self._data[i])
            i = smallest

class EventsHeap(MinHeap):
    """Stores ENDPOINTS. The minimum endpoint is the next endpoint encountered during CCW sweep."""
    def __init__(self, Q: Point):
        self.Q = Q
        super().__init__(self._angular_before)

    def _half(self, p: Point) -> int:
        """
        Split rays around Q into two halves (Cartesian).
        Half 0: upper/right half (dy > 0)
        Half 1: lower/left half
        """
        dx = p.x - self.Q.x
        dy = p.y - self.Q.y

        if dy > 0 or (dy == 0 and dx >= 0):
            return 0
        return 1

    def _angular_before(self, e1: Endpoint, e2: Endpoint) -> bool:
        p1 = e1.point
        p2 = e2.point

        h1 = self._half(p1)
        h2 = self._half(p2)

        if h1 != h2:
            return h1 < h2

        if p1.x == p2.x and p1.y == p2.y:
            return e1.is_birth and not e2.is_birth

        return Geometry.isCCW(self.Q, p1, p2) == -1

    @staticmethod
    def build(Q: Point, segments: List[Segment]):
        heap = EventsHeap(Q)

        for s in segments:
            # Auto-correct Birth vs Death events in case the user clicked them CW instead of CCW
            if Geometry.isCCW(Q, s.A, s.B) == 1: 
                birth_pt, death_pt = s.B, s.A
            else:
                birth_pt, death_pt = s.A, s.B

            heap.insert(Endpoint(birth_pt, s, is_birth=True))
            heap.insert(Endpoint(death_pt, s, is_birth=False))

        return heap


class SegmentHeap(MinHeap):
    """Active-segment heap H. Stores SEGMENTS."""
    def __init__(self, Q: Point):
        self.Q = Q
        super().__init__(self._closer_to_Q)

    def _ray_hits_segment(self, P: Point, seg: Segment) -> bool:
        side_A = Geometry.isCCW(self.Q, P, seg.A)
        side_B = Geometry.isCCW(self.Q, P, seg.B)
        return (side_A != 0 and side_B != 0 and side_A != side_B)

    def _closer_to_Q(self, s1: Segment, s2: Segment) -> bool:
        for p in (s1.A, s1.B):
            if self._ray_hits_segment(p, s2):
                side_Q = Geometry.isCCW(s2.A, s2.B, self.Q)
                side_p = Geometry.isCCW(s2.A, s2.B, p)
                return side_Q == side_p

        for p in (s2.A, s2.B):
            if self._ray_hits_segment(p, s1):
                side_Q = Geometry.isCCW(s1.A, s1.B, self.Q)
                side_p = Geometry.isCCW(s1.A, s1.B, p)
                return side_Q != side_p

        # Fallback to squared distance if segments perfectly share an endpoint 
        d1 = min((self.Q.x - s1.A.x)**2 + (self.Q.y - s1.A.y)**2,
                 (self.Q.x - s1.B.x)**2 + (self.Q.y - s1.B.y)**2)
        d2 = min((self.Q.x - s2.A.x)**2 + (self.Q.y - s2.A.y)**2,
                 (self.Q.x - s2.B.x)**2 + (self.Q.y - s2.B.y)**2)
        
        return d1 < d2

    def sees_root(self, segment: Segment) -> bool:
        return (not self.is_empty() and self._data[0] is segment)