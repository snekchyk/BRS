import math
from turtle import *

g = 9.8
t = 0
turtle_x = -500
turtle_y = 0
my_turtle = Turtle()
my_turtle.pensize(2)
my_turtle.speed(0)
my_turtle.penup()
my_turtle.goto(turtle_x, turtle_y)
my_turtle.hideturtle()

def get_Sx(v0x, t):
    return (v0x*t)


def get_Sy(v0y, t):
    return (v0y*t - (g*math.pow(t, 2))/2)


def draw(Sx, Sy, t):
    my_turtle.penup()
    my_turtle.goto(turtle_x + Sx, turtle_y + Sy)
    my_turtle.pendown()
    my_turtle.circle(1)
    my_turtle.penup()

v0 = float(input("Enter initial velocity: "))
angle = float(input("Enter angle: "))

x0 = float(input("Enter initial x: "))
y0 = float(input("Enter initial y: "))

full_t = 2 * (v0 * math.sin(math.radians(angle)))/g

v0x = v0 * math.cos(math.radians(angle))
v0y = v0 * math.sin(math.radians(angle))

while t <= full_t:

    Sx = get_Sx(v0x, t)
    Sy = get_Sy(v0y, t)
    draw(Sx, Sy, t)
    t += 0.1

Sx = get_Sx(v0x, t)
Sy = get_Sy(v0y, t)
my_turtle.goto(turtle_x + x0 + Sx, turtle_y + y0 + Sy)

update()
done()