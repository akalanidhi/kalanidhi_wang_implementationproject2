# Point, Segment, Endpoint classes. Helper functions Intersect() and isCCW().

from typing import Optional ##not necessary, just for self-documenting code below so can delete if we'd like

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
 
    def __repr__(self):
        return f"({self.x:.2f}, {self.y:.2f})"

class Segment:
    """
    s_i = segment
    A = first-clicked endpoint
    B = second-clicked endpoint
    Q -> A -> B -> Q traces a CCW loop
    """
    _next_id = 0
 
    def __init__(self, A: Point, B: Point):
        self.A = A
        self.B = B
        self.id = Segment._next_id
        Segment._next_id += 1
 
    def other_endpoint(self, p: Point) -> Point:
        """Given one endpoint of this segment, return the other one."""
        return self.B if p is self.A else self.A
 
    def __repr__(self):
        return f"s{self.id}[{self.A} -> {self.B}]"

class Endpoint:
    """
    endpoint = one event in the sweep, either a birth (A) or death (B) of a segment
    """
    def __init__(self, point: Point, segment: Segment, is_birth: bool):
        self.point = point
        self.segment = segment
        self.is_birth = is_birth
 
    def __repr__(self):
        kind = "birth" if self.is_birth else "death"
        return f"Endpoint({self.point}, {self.segment}, {kind})"

    def _det(a, b) -> float:
    """ returns cross product of vectors a and b, given as (x, y) tuples."""
    return a[0] * b[1] - a[1] * b[0]
 
 
    def _subtract(a, b):
    """returns vector between 2 points, given as (x, y) tuples."""
    return (a[0] - b[0], a[1] - b[1])

class Geometry:
    """helper functions (imported from the course template)."""
 
    @staticmethod
    def is_ccw(p1: Point, p2: Point, p3: Point) -> int:
        """
        returns 0 if p1, p2, p3 are collinear,
                -1 if p1 -> p2 -> p3 -> p1 is CCW,
                +1 if p1 -> p2 -> p3 -> p1 is CW.
        """
        val = (p2.x - p1.x) * (p3.y - p2.y) - (p2.y - p1.y) * (p3.x - p2.x)
        if val == 0:
            return 0
        return -1 if val > 0 else 1
 
    @staticmethod
    def intersect(s1: Segment, s2: Segment) -> Point:
        """
        returns the intersection point of two segments, or Point(-1, -1) if
        none exists (i.e. the segments are parallel or don't actually cross
        within their endpoints). 
        uses parametric-line-intersection formula. 
        """
        p = (s1.A.x, s1.A.y)
        r = _subtract((s1.B.x, s1.B.y), p)
 
        q = (s2.A.x, s2.A.y)
        s = _subtract((s2.B.x, s2.B.y), q)
 
        r_cross_s = _det(r, s)
        q_minus_p = _subtract(q, p)
 
        if r_cross_s == 0:  # parallel lines -- no unique intersection
            return Point(-1, -1)

        #any point on segment 1 written as p + t * r
            #p is s1.A, r is direction vector
            # when t = 0, you're at start (p). when t = 1, you're at end(p+r). so t is any point on segment between 0 and 1
        #any point of segment 2 written as p + u * s
        #their intersection point (t, u) is: p + t * r = q + u * s
 
        t = _det(q_minus_p, s) / r_cross_s #t = det(q-p, s) / det(r, s)
        u = _det(q_minus_p, r) / r_cross_s
 
        if 0 <= t <= 1 and 0 <= u <= 1:
            return Point(p[0] + t * r[0], p[1] + t * r[1])
        return Point(-1, -1)