#minHeap, eventsHeap (Sisi), segmentHeap (Anjali)
#minHeap is the design structure for eventsHeap and segmentHeaps since both are minHeaps/
#In eventsHeap, "before" means point 1 comes earlier in CCW angular sweep than point 2 (angular comparison)
#and segmentHeap means point 1 closer to Q along ray r than point 2 (distance-to-Q comparison)

"""
minHeap = generic minHeap
eventsHeap = drives the sweep aka processes the events in proper CCW order
segmentHeap = orders segments by distance to Q
hence, eventsHeap and segmentHeap simply implement minHeap in two diff ways
"""
 
from typing import List, Callable
from geometry import Point, Segment, Endpoint, Geometry
 
 
class MinHeap:
    """
    if a comes before b, comparator(a, b) returns True
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
        append then sift up
        """
        self._data.append(item)

        # sift up
        i = len(self._data) - 1

        while i > 0:
            parent = (i - 1) // 2

            if self._before(self._data[i], self._data[parent]):
                self._data[i], self._data[parent] = (
                    self._data[parent],
                    self._data[i]
                )
                i = parent
            else:
                break

    def extract_min(self) -> object:
        """
        remove and return the root, move last element to root and sift-down
        """
        if self.is_empty():
            raise IndexError("Heap is empty")

        minimum = self._data[0] # saves root / min elmt

        # move last element to root
        last = self._data.pop() #removes last elmt

        if not self.is_empty():
            self._data[0] = last #moves last elmt to root

            # sift down
            i = 0

            while True:
                left = 2 * i + 1
                right = 2 * i + 2
                smallest = i

                #len checks that left (or right) child exists
                if left < len(self._data) and self._before(
                    self._data[left],
                    self._data[smallest]
                ):
                    smallest = left

                if right < len(self._data) and self._before(
                    self._data[right],
                    self._data[smallest]
                ):
                    smallest = right

                if smallest != i: #smallest is either left or right child
                    self._data[i], self._data[smallest] = (
                        self._data[smallest],
                        self._data[i]
                    )
                    i = smallest
                else:
                    break

        return minimum

    def remove(self, item: object) -> None:
        """
        remove a specific item from heap
        """
        if item not in self._data:
            return

        i = self._data.index(item)

        # replace with last element
        last = self._data.pop()

        if i == len(self._data):
            return

        self._data[i] = last

        # decide whether to sift up or down
        parent = (i - 1) // 2

        if i > 0 and self._before(self._data[i], self._data[parent]):
            # sift up
            while i > 0:
                parent = (i - 1) // 2

                if self._before(self._data[i], self._data[parent]):
                    self._data[i], self._data[parent] = (
                        self._data[parent],
                        self._data[i]
                    )
                    i = parent
                else:
                    break

        else:
            # sift down
            while True:
                left = 2 * i + 1
                right = 2 * i + 2
                smallest = i

                if left < len(self._data) and self._before(
                    self._data[left],
                    self._data[smallest]
                ):
                    smallest = left

                if right < len(self._data) and self._before(
                    self._data[right],
                    self._data[smallest]
                ):
                    smallest = right

                if smallest != i:
                    self._data[i], self._data[smallest] = (
                        self._data[smallest],
                        self._data[i]
                    )
                    i = smallest
                else:
                    break
 
 
class EventsHeap(MinHeap):
    """
    heap ordered by events to process in CCW order around Q
    """

    def __init__(self, Q: Point):
        self.Q = Q
        super().__init__(self._angular_before) 
        #self._before = EventsHeap._angular_before
        #compares EventsHeap._angular_before(child, parent) instead of self._before(child, parent)

    def _angular_before(self, e1: Endpoint, e2: Endpoint) -> bool:
        """
        returns True if e1 should be visited before e2 in CCW sweep.
        """
        result = Geometry.isCCW(
            self.Q,
            e1.point,
            e2.point
        )

        # e1 comes before e2 if Q -> e1 -> e2 is CCW
        if result == -1:
            return True

        if result == 1:
            return False

        # if same angle, process births first before deaths
        if e1.point.x == e2.point.x and e1.point.y == e2.point.y:
            return e1.is_birth and not e2.is_birth

        return False

    @staticmethod
    def build(Q: Point, segments: List[Segment]) -> "EventsHeap":
        """
        build heap from all segment endpoints
        """
        heap = EventsHeap(Q)

        for s in segments:
            heap.insert(Endpoint(s.A, s, is_birth=True)) #is_birth label negligible until SegmentHeap (bc that's when decide whether to add or remove segment based on it being birth vs. death)
            heap.insert(Endpoint(s.B, s, is_birth=False))

        return heap
 
 
class SegmentHeap(MinHeap):

    def __init__(self, Q: Point):
        self.Q = Q
        super().__init__(self._closer_to_Q)

    def _ray_hits_segment(self, P: Point, seg: Segment) -> bool:
        """
        True if the ray Q->P (extended) passes between seg.A and seg.B,
        i.e. the line QP separates the two endpoints of seg.
        """
        c1 = Geometry.isCCW(self.Q, P, seg.A)
        c2 = Geometry.isCCW(self.Q, P, seg.B)
        return c1 != 0 and c2 != 0 and c1 != c2

    def _closer_to_Q(self, s1: Segment, s2: Segment) -> bool:
        """
        returns True if s1 crosses the ray r closer to Q than s2 does.
        Only valid when both s1 and s2 currently cross r.
        """
        for p in (s1.A, s1.B):
            if self._ray_hits_segment(p, s2):
                side_Q = Geometry.isCCW(s2.A, s2.B, self.Q)
                side_p = Geometry.isCCW(s2.A, s2.B, p)
                return side_Q == side_p  # p hasn't crossed s2's line -> s1 closer

        for p in (s2.A, s2.B):
            if self._ray_hits_segment(p, s1):
                side_Q = Geometry.isCCW(s1.A, s1.B, self.Q)
                side_p = Geometry.isCCW(s1.A, s1.B, p)
                return side_Q != side_p  # p HAS crossed s1's line -> s1 closer

        raise ValueError("segments do not both cross the current ray r")

    def sees_root(self, segment: Segment) -> bool:
        return not self.is_empty() and self._data[0] is segment