##GUI file
import py5
import math

from geometry import Point, Segment
from sweep import runAlgorithm

##global variables
WINDOW = 512

segments = []
Q = None

startPoint = None

insertMode = False
queryMode = False

seenPoints = []      # endpoints that Q currently sees, from runAlgorithm()
showVisibility = False  # toggled by 'v'


def setup():
    py5.size(WINDOW, WINDOW)


def draw():
    py5.background(230)

    py5.stroke(0)
    py5.fill(0)

    # unfinished segment
    if startPoint is not None:
        py5.circle(startPoint.x, startPoint.y, 6)

    # finished segments
    for s in segments:

        py5.line(
            s.A.x, s.A.y,
            s.B.x, s.B.y
        )

        py5.circle(s.A.x, s.A.y, 6)
        py5.circle(s.B.x, s.B.y, 6)

    # visibility segments (blue dotted lines from Q to each seen endpoint)
    if showVisibility and Q is not None:

        py5.stroke(0, 0, 255)
        py5.no_fill()

        for p in seenPoints:
            _draw_dotted_line(Q.x, Q.y, p.x, p.y)

        py5.stroke(0)

    # observer
    if Q is not None:

        py5.fill(255, 0, 0)
        py5.circle(Q.x, Q.y, 10)


def _draw_dotted_line(x1, y1, x2, y2, dash_len=6, gap_len=4):
##draws a dotted line from (x1,y1) to (x2,y2), since py5 has no built-in dashed stroke
    dist = math.hypot(x2 - x1, y2 - y1)

    if dist == 0:
        return

    dx = (x2 - x1) / dist
    dy = (y2 - y1) / dist

    travelled = 0.0
    drawing = True

    while travelled < dist:

        seg_len = dash_len if drawing else gap_len
        next_travelled = min(travelled + seg_len, dist)

        if drawing:
            py5.line(
                x1 + dx * travelled, y1 + dy * travelled,
                x1 + dx * next_travelled, y1 + dy * next_travelled
            )

        travelled = next_travelled
        drawing = not drawing


def mouse_clicked():
##mouse input. if o is clicked --> mouse input becomes point. if Q is clicked --> becomes query point
    global startPoint
    global Q
    global seenPoints

    if insertMode:

        if startPoint is None:

            startPoint = Point(
                py5.mouse_x,
                py5.mouse_y
            )

        else:

            endPoint = Point(
                py5.mouse_x,
                py5.mouse_y
            )

            segments.append(
                Segment(startPoint, endPoint)
            )

            startPoint = None

            if Q is not None:
                seenPoints = runAlgorithm(Q, segments)

    elif queryMode:

        Q = Point(
            py5.mouse_x,
            py5.mouse_y
        )

        seenPoints = runAlgorithm(Q, segments)


def key_pressed():
##keyboard input. if o clicked --> enter insertMode. if q clicked --> query mode. if v clicked --> toggle visibility display
    global insertMode
    global queryMode
    global showVisibility
    global seenPoints

    if py5.key == 'o':

        insertMode = True
        queryMode = False

        print("Obstacle mode")

    elif py5.key == 'q':

        queryMode = True
        insertMode = False

        print("Query mode")

    elif py5.key == 'v':

        if Q is not None:
            seenPoints = runAlgorithm(Q, segments)
            showVisibility = True
            print(f"Showing visibility: {len(seenPoints)} endpoint(s) seen")
        else:
            print("Set Q first before viewing visibility")

    elif py5.key == 'r':

        readData("input.txt")


def readData(filename):
##creates Point and Segment objects and then run runAlgorithm()
    global Q
    global seenPoints

    segments.clear()

    with open(filename) as f:
        ##might need to change this so that it takes in h instead of ignoring first line
        first = True

        for line in f:

            if first:
                first = False
                continue

            parts = line.split()

            if parts[0] == "i":

                A = Point(
                    int(parts[1]),
                    int(parts[2])
                )

                B = Point(
                    int(parts[3]),
                    int(parts[4])
                )

                segments.append(
                    Segment(A, B)
                )

            elif parts[0] == "q":

                Q = Point(
                    int(parts[1]),
                    int(parts[2])
                )

    if Q is not None:
        seenPoints = runAlgorithm(Q, segments)


py5.run_sketch()