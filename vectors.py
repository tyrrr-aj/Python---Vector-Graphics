import sys
import optparse
import json
import pygame
from PIL import Image, ImageDraw

class Figure():
    def display(self):
        print (self.__class__, self.__dict__, self.color)
    def setColor(self, f_description, palette): # possibly needs adjustment of html color format to RGB palette
        try:
            self.color = color_format(f_description['color'], palette)
        except: # in case of KeyError - meaning figure's color has not been specified separatly
            pass
    
class Rectangle(Figure):
    def __init__(self, f_description, palette):
        self.center = {'x' : f_description['x'], 'y' : f_description['y']}
        self.width = f_description['width']
        self.height = f_description['height']
        self.setColor(f_description, palette)
    def draw_on_screen(self, screen):
        pot_x = self.center['x'] - (self.width / 2)
        pot_y = self.center['y'] - (self.height / 2)
        x = max(0, pot_x) # coordinates of the upper left corner
        y = max(0, pot_y) # if less then zero, move to zero and adjust width/height
        width = self.width - (x - pot_x)
        height = self.height - (y - pot_y)
        pygame.draw.rect(screen, self.color, (x, y, width, height))
    def draw_in_file(self, file):
        file.rectangle([(self.center['x'] - (self.width / 2), self.center['y'] - (self.height / 2)), (self.center['x'] + (self.width / 2), \
                                                                             self.center['y'] + (self.height / 2))], self.color, self.color)
        
class Square(Rectangle):
    def __init__(self, f_description, palette):
        f_description['width'] = f_description['height'] = f_description['size']
        Rectangle.__init__(self, f_description, palette)
        
class Circle(Figure):
    def __init__(self, f_description, palette):
        self.center = {'x' : f_description['x'], 'y' : f_description['y']}
        self.radius = f_description['radius']
        self.setColor(f_description, palette)
    def draw_on_screen(self, screen):
        pygame.draw.circle(screen, self.color, (self.center['x'], self.center['y']), self.radius)
    def draw_in_file(self, file):
        file.pieslice([(self.center['x'] - self.radius, self.center['y'] - self.radius), (self.center['x'] + self.radius, self.center['y'] + self.radius)],\
                                                                                                                                0, 360, self.color, self.color)
    
class Polygon(Figure):
    def __init__(self, f_description, palette):
        self.vertexes = [tuple(e) for e in f_description['points']]
        self.setColor(f_description, palette)
    def draw_on_screen(self, screen):
        pygame.draw.polygon(screen, self.color, self.vertexes)
    def draw_in_file(self, file):
        file.polygon(self.vertexes, self.color, self.color)
    
class Point(Figure):
    def __init__(self, f_description, palette):
        self.x = f_description['x']
        self.y = f_description['y']
        self.setColor(f_description, palette)
    def draw_on_screen(self, screen):
        pygame.Surface.set_at(screen, (self.x, self.y), self.color)
    def draw_in_file(self, file):
        file.point((self.x, self.y), self.color)
    
def color_format(color, palette): # translates color specified by word from palette or html-style number to standard RGB 3-tuple
    if color in palette.keys(): # if color is specified by word from palette
        color = palette[color] # it may still be written as html-style number, depending on palette, so further processing is necessary anyway
    if len(color[1:len(color) - 1].split(',')) == 1: # it's a single html-style number, not an RGB 3-tuple
        return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:], 16)) # translating hexadecimal number into RGB 3-tuple
    else:
        return tuple([int(e) for e in color[1:len(color) - 1].split(',')]) # string needs to be translated into actual 3-tuple
        
def save(file, figures, screen, plaette): # saves graphic to png file using Pillow library
    im = Image.new('RGB', (screen['width'], screen['height']), screen['bg_color'])
    draw = ImageDraw.Draw(im) # initializing object to draw an image in
    for fig in figures:
        fig.draw_in_file(draw)
    del draw
    im.save(file, 'PNG')
    
def display(figures, screen_param, palette): # displays graphic on screen using PyGame library
    pygame.init()
    screen = pygame.display.set_mode([screen_param['width'], screen_param['height']]) # creates object to draw in
    screen.fill(color_format(screen_param['bg_color'], palette))
    for fig in figures:
        fig.draw_on_screen(screen)
    pygame.display.flip() # displays prepared screen object
    done = False
    while not done: # wait for user to close the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
    
def json_parse(file): # reds info from json, writing it into two dicts: screen and palette, and list of figures
    figures = []
    screen = file['Screen'] # separating two of main dicts from file: Screen and Palette
    palette = file['Palette']
    Figure.color = color_format(screen['fg_color'], palette)
    obj_creator = {'point' : Point, 'polygon' : Polygon, 'rectangle' : Rectangle, 'square' : Square, 'circle' : Circle} # name of figure : corresponding class
    for fig in file['Figures']:
        figures.append(obj_creator[fig['type']](fig, palette)) # produces list of instances of cartain figures
    return (figures, screen, palette)
    
def main():
    # Aim of the program is to read vector graphic file in json, display it on the screen, and (if told to) save it to file in png
    # Program must get one argument specifying input file, and accepts a second (optional) argument as -o (--output) option, specifying output file
    # Program does save a graphic to png only if -o argument is given - if no, graphic is only displayed on screen
    parser = optparse.OptionParser()
    parser.add_option("-o", "--output", dest = "outFile", help = "file to save graphic in (if saving is necessary)")
    (options, args) = parser.parse_args()
    if args: # checks if input file has been specified
        with open(args[0]) as in_file:
            file = json.load(in_file) # file becomes a dict with dicts from which a JSON file is constructed
    else:
        print('Input file not specified')
        exit()
    (figures, screen, palette) = json_parse(file)
    display(figures, screen, palette)
    if options.outFile:
        save(options.outFile, figures, screen, palette)
    
if __name__ == '__main__':
    main()