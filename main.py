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

    # observer
    if Q is not None:

        py5.fill(255,0,0)
        py5.circle(Q.x,Q.y,10)

def mouse_clicked():
##mouse input. if o is clicked --> mouse input becomes point. if Q is clicked --> becomes query point
    global startPoint
    global Q

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
                Segment(startPoint,endPoint)
            )

            startPoint = None

            if Q is not None:
                runAlgorithm(Q,segments)

    elif queryMode:

        Q = Point(
            py5.mouse_x,
            py5.mouse_y
        )

        runAlgorithm(Q,segments)

def key_pressed():
##keyboard input. if o clicked --> enter insertMode. if q clicked --> query mode
    global insertMode
    global queryMode

    if py5.key == 'o':

        insertMode = True
        queryMode = False

        print("Obstacle mode")

    elif py5.key == 'q':

        queryMode = True
        insertMode = False

        print("Query mode")

    elif py5.key == 'r':

        readData("input.txt")

def readData(filename):
##creates Point and Segment objects and then run runAlgorithm()
    global Q

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
                    Segment(A,B)
                )

            elif parts[0] == "q":

                Q = Point(
                    int(parts[1]),
                    int(parts[2])
                )

    if Q is not None:
        runAlgorithm(Q,segments)


py5.run_sketch()