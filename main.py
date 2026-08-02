##GUI file (pygame version)
import pygame
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

BACKGROUND = (230, 230, 230)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)


def draw(screen):
    screen.fill(BACKGROUND)

    # unfinished segment
    if startPoint is not None:
        pygame.draw.circle(screen, BLACK, (int(startPoint.x), int(startPoint.y)), 3)

    # finished segments
    for s in segments:

        pygame.draw.line(
            screen, BLACK,
            (s.A.x, s.A.y),
            (s.B.x, s.B.y)
        )

        pygame.draw.circle(screen, BLACK, (int(s.A.x), int(s.A.y)), 3)
        pygame.draw.circle(screen, BLACK, (int(s.B.x), int(s.B.y)), 3)

    # visibility segments (blue dotted lines from Q to each seen endpoint)
    if showVisibility and Q is not None:

        for p in seenPoints:
            _draw_dotted_line(screen, Q.x, Q.y, p.x, p.y)

    # observer
    if Q is not None:
        pygame.draw.circle(screen, RED, (int(Q.x), int(Q.y)), 5)

    pygame.display.flip()


def _draw_dotted_line(screen, x1, y1, x2, y2, dash_len=6, gap_len=4):
##draws a dotted line from (x1,y1) to (x2,y2)
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
            pygame.draw.line(
                screen, BLUE,
                (x1 + dx * travelled, y1 + dy * travelled),
                (x1 + dx * next_travelled, y1 + dy * next_travelled)
            )

        travelled = next_travelled
        drawing = not drawing


def mouse_clicked(mx, my):
##mouse input. if o is clicked --> mouse input becomes point. if Q is clicked --> becomes query point
    global startPoint
    global Q
    global seenPoints

    if insertMode:

        if startPoint is None:

            startPoint = Point(mx, my)

        else:

            endPoint = Point(mx, my)

            segments.append(
                Segment(startPoint, endPoint)
            )

            startPoint = None

            if Q is not None:
                seenPoints = runAlgorithm(Q, segments)

    elif queryMode:

        Q = Point(mx, my)

        seenPoints = runAlgorithm(Q, segments)


def key_pressed(key):
##keyboard input. if o clicked --> enter insertMode. if q clicked --> query mode. if v clicked --> toggle visibility display
    global insertMode
    global queryMode
    global showVisibility
    global seenPoints

    if key == pygame.K_o:

        insertMode = True
        queryMode = False

        print("Obstacle mode")

    elif key == pygame.K_q:

        queryMode = True
        insertMode = False

        print("Query mode")

    elif key == pygame.K_v:

        if Q is not None:
            seenPoints = runAlgorithm(Q, segments)
            showVisibility = True
            print(f"Showing visibility: {len(seenPoints)} endpoint(s) seen")
        else:
            print("Set Q first before viewing visibility")

    elif key == pygame.K_r:

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


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW, WINDOW))
    pygame.display.set_caption("Visibility Sweep")
    clock = pygame.time.Clock()

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                mouse_clicked(mx, my)

            elif event.type == pygame.KEYDOWN:
                key_pressed(event.key)

        draw(screen)
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()