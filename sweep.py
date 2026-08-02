#VisibilitySweep to glue eventsHeap and segmentHeap together

# sweep.py
# Glues EventsHeap and SegmentHeap together to run the O(n log n)
# visibility-graph sweep described in Section 3 of the assignment.

from typing import List
from geometry import Point, Segment, Geometry
from heaps import EventsHeap, SegmentHeap 


def _check_assumptions(Q: Point, segments: List[Segment]) -> None:
   
    for s in segments:
        if s.A.y <= Q.y or s.B.y <= Q.y:
            print(f"Warning: {s} has an endpoint not above Q.")

        # Q -> A -> B -> Q should trace a CCW loop, i.e. isCCW(Q, A, B) == -1
        if Geometry.isCCW(Q, s.A, s.B) != -1:
            print(f"Warning: {s} was not entered in CCW order relative to Q "
                  f"(expected Q -> A -> B -> Q to be CCW).")


def runAlgorithm(Q: Point, segments: List[Segment]) -> List[Point]:
    
    if Q is None or not segments:
        return []

    _check_assumptions(Q, segments)

    events = EventsHeap.build(Q, segments)
    active = SegmentHeap(Q)

    seen: List[Point] = []

    while not events.is_empty():
        event = events.extract_min()
        seg = event.segment

        if event.is_birth:
            active.insert(seg)
            if active.sees_root(seg):
                seen.append(event.point)
        else:
            # check visibility BEFORE removing -- sees_root needs seg
            # still in the heap to know if it's currently at the top
            if active.sees_root(seg):
                seen.append(event.point)
            active.remove(seg)

    print(f"Q sees {len(seen)} endpoint(s):")
    for p in seen:
        print(f"  {p}")

    return seen