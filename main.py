import pygame
import math

from geometry import Point, Segment
import sweep
##global variables
CANVAS = 512
BAR_HEIGHT = 50
WINDOW_W = CANVAS
WINDOW_H = CANVAS + BAR_HEIGHT

segments = []
Q = None

startPoint = None

insertMode = False
queryMode = False

seenPoints = []      # endpoints that Q currently sees, from runAlgorithm()
showVisibility = False  # toggled by 'v'

BACKGROUND = (230, 230, 230)
BAR_BG = (200, 200, 200)
BUTTON_BG = (255, 255, 255)
BUTTON_ACTIVE = (180, 210, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

font = None  # set in main() after pygame.init()

##buttons live in the bar below the canvas, each maps to a mode key
buttons = [
    {"rect": pygame.Rect(10, CANVAS + 8, 90, 34), "label": "Obstacle", "key": "o"},
    {"rect": pygame.Rect(110, CANVAS + 8, 90, 34), "label": "Query", "key": "q"},
    {"rect": pygame.Rect(210, CANVAS + 8, 90, 34), "label": "Visibility", "key": "v"},
    {"rect": pygame.Rect(310, CANVAS + 8, 90, 34), "label": "Read File", "key": "r"},
]


def current_mode_text():
##returns a string describing the active mode, for display in the bar
    if insertMode:
        return "Mode: Obstacle"
    elif queryMode:
        return "Mode: Query"
    else:
        return "Mode: None"


def draw(screen):
    screen.fill(BACKGROUND)

    # unfinished segment
    if startPoint is not None:
        pygame.draw.circle(screen, BLACK, (int(startPoint.x), CANVAS - int(startPoint.y)), 3)

    # finished segments
    for s in segments:

        pygame.draw.line(
            screen, BLACK,
            (s.A.x, CANVAS - s.A.y),
            (s.B.x, CANVAS - s.B.y)
        )

        pygame.draw.circle(screen, BLACK, (int(s.A.x), CANVAS - int(s.A.y)), 3)
        pygame.draw.circle(screen, BLACK, (int(s.B.x), CANVAS - int(s.B.y)), 3)

    # visibility segments (blue dotted lines from Q to each seen endpoint)
    if showVisibility and Q is not None:

        for p in seenPoints:
            _draw_dotted_line(screen, Q.x, Q.y, p.x, p.y)

    # observer
    if Q is not None:
        pygame.draw.circle(screen, RED, (int(Q.x), CANVAS - int(Q.y)), 5)

    draw_bar(screen)

    pygame.display.flip()


def draw_bar(screen):
##draws the bottom control bar: buttons + current mode text
    pygame.draw.rect(screen, BAR_BG, (0, CANVAS, WINDOW_W, BAR_HEIGHT))

    for b in buttons:

        active = (
            (b["key"] == "o" and insertMode) or
            (b["key"] == "q" and queryMode) or
            (b["key"] == "v" and showVisibility)
        )

        color = BUTTON_ACTIVE if active else BUTTON_BG

        pygame.draw.rect(screen, color, b["rect"])
        pygame.draw.rect(screen, BLACK, b["rect"], 1)

        label_surf = font.render(b["label"], True, BLACK)
        label_rect = label_surf.get_rect(center=b["rect"].center)
        screen.blit(label_surf, label_rect)

    mode_surf = font.render(current_mode_text(), True, BLACK)
    screen.blit(mode_surf, (410, CANVAS + 17))


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
            # Convert mathematical Y to Pygame Screen Y
            py1 = CANVAS - (y1 + dy * travelled)
            py2 = CANVAS - (y1 + dy * next_travelled)
            
            pygame.draw.line(
                screen, BLUE,
                (x1 + dx * travelled, py1),
                (x1 + dx * next_travelled, py2)
            )

        travelled = next_travelled
        drawing = not drawing


def mouse_clicked(mx, my):
##mouse input. clicks in the bottom bar hit buttons; clicks on the canvas place points
    if my >= CANVAS:
        button_clicked(mx, my)
    else:
        canvas_clicked(mx, my)


def button_clicked(mx, my):
##checks the bar buttons for a hit and dispatches to the same handler as key_pressed
    for b in buttons:

        if b["rect"].collidepoint(mx, my):
            key_pressed(b["key"], from_button=True)
            return


def canvas_clicked(mx, my):
##mouse input on the canvas. if o is active --> mouse input becomes point. if Q is active --> becomes query point
    global startPoint
    global Q
    global seenPoints

    # Convert Pygame Screen Y to Mathematical Y
    cy = CANVAS - my

    if insertMode:

        if startPoint is None:
            startPoint = Point(mx, cy)

        else:
            endPoint = Point(mx, cy)

            segments.append(
                Segment(startPoint, endPoint)
            )

            startPoint = None

            if Q is not None:
                seenPoints = sweep.runAlgorithm(Q, segments)

    elif queryMode:

        Q = Point(mx, cy)

        seenPoints = sweep.runAlgorithm(Q, segments)

def key_pressed(key, from_button=False):
##keyboard (or button) input. if o clicked --> enter insertMode. if q clicked --> query mode. if v clicked --> toggle visibility display
    global insertMode
    global queryMode
    global showVisibility
    global seenPoints

    ##pygame key constants come through for real keypresses, plain strings come through from buttons
    if not from_button:
        key = {
            pygame.K_o: "o",
            pygame.K_q: "q",
            pygame.K_v: "v",
            pygame.K_r: "r",
        }.get(key)

    if key == "o":

        insertMode = True
        queryMode = False

        print("Obstacle mode")

    elif key == "q":

        queryMode = True
        insertMode = False

        print("Query mode")

    elif key == "v":

        if Q is not None:
            seenPoints = sweep.runAlgorithm(Q, segments)
            showVisibility = not showVisibility if from_button else True
            print(f"Showing visibility: {len(seenPoints)} endpoint(s) seen")
        else:
            print("Set Q first before viewing visibility")

    elif key == "r":

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
        seenPoints = sweep.runAlgorithm(Q, segments)


def main():
    global font

    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Visibility Sweep")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 22)

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