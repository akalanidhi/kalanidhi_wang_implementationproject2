#minHeap, eventsHeap (Sisi), segmentHeap (Anjali)
#minHeap is the design structure for eventsHeap and segmentHeaps since both are minHeaps/
#In eventsHeap, "before" means point 1 comes earlier in CCW angular sweep than point 2 (angular comparison)
#and segmentHeap means point 1 closer to Q along ray r than point 2 (distance-to-Q comparison)

"""
heaps.py
========
A generic MinHeap, plus the two configurations used by the algorithm:
 
  - EventsHeap  : orders Endpoints by CCW angle around Q
                  (drives the sweep -- "what happens next")
  - SegmentHeap : orders currently-active Segments by distance to Q
                  along the current ray r ("what's closest right now")
 
Both are just MinHeap with a different comparator plugged in -- that's
the "glue different data structures together" idea from the assignment.
"""
 
from typing import List, Callable
from geometry import Point, Segment, Endpoint, Geometry
 
 
class MinHeap:
    """
    A generic binary min-heap parameterized by a comparator function.
    comparator(a, b) should return True if a comes strictly before b
    (i.e. a should end up closer to the root than b).
    """
    def __init__(self, comparator: Callable[[object, object], bool]):
        self._data: List[object] = []
        self._before = comparator  # comparator(a, b) -> bool
 
    def is_empty(self) -> bool:
        return len(self._data) == 0
 
    def peek_min(self) -> object:
        return self._data[0]
 
    def insert(self, item: object) -> None:
        """
        Append item, then sift-up using self._before to maintain heap order.
        TODO: implement sift-up.
        """
        raise NotImplementedError
 
    def extract_min(self) -> object:
        """
        Remove and return the root, move last element to root, sift-down.
        TODO: implement sift-down.
        """
        raise NotImplementedError
 
    def remove(self, item: object) -> None:
        """
        Needed for death events: remove a specific segment from H
        (not necessarily the root). Find its index, swap with last,
        pop, then sift-up or sift-down from that index as needed.
        TODO: implement.
        """
        raise NotImplementedError
 
 
class EventsHeap(MinHeap):
    """
    Wraps MinHeap with the angular comparator: endpoint p_i comes before p_j
    iff IsCCW(Q, p_i, p_j) is negative (i.e. walking Q -> p_i -> p_j is CCW,
    meaning the ray reaches p_i first as it sweeps CCW).
    """
    def __init__(self, Q: Point):
        self.Q = Q
        super().__init__(self._angular_before)
 
    def _angular_before(self, e1: Endpoint, e2: Endpoint) -> bool:
        """
        TODO: return True if e1.point should be visited before e2.point
        when sweeping CCW around self.Q. Use Geometry.is_ccw(Q, e1.point, e2.point).
        """
        raise NotImplementedError
 
    @staticmethod
    def build(Q: Point, segments: List[Segment]) -> "EventsHeap":
        """
        Build the full events heap from all 2n endpoints.
        For each segment, push a birth Endpoint(A) and a death Endpoint(B).
        """
        heap = EventsHeap(Q)
        for s in segments:
            heap.insert(Endpoint(s.A, s, is_birth=True))
            heap.insert(Endpoint(s.B, s, is_birth=False))
        return heap
 
 
class SegmentHeap(MinHeap):
    """
    Wraps MinHeap with the "closer to Q along current ray" comparator.
    Since obstacle segments never cross each other, this order -- once
    established between two active segments -- never flips while both
    remain active, so no dynamic re-intersection computation is needed.
    """
    def __init__(self, Q: Point):
        self.Q = Q
        super().__init__(self._closer_to_Q)
 
    def _closer_to_Q(self, s1: Segment, s2: Segment) -> bool:
        """
        TODO: return True if s1 is nearer to Q (along the current ray)
        than s2. Use orientation tests (Geometry.is_ccw) on the segments'
        endpoints relative to Q -- do NOT compute exact intersection
        points with r (the doc explicitly says you don't need to).
        """
        raise NotImplementedError
 
    def sees_root(self, segment: Segment) -> bool:
        """Convenience check: is `segment` currently at the root of H?"""
        return (not self.is_empty()) and self.peek_min() is segment
 