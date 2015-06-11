from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
import copy
import time
import random
import math
import inspect
import os
import traceback
import webbrowser
import urllib.request
import threading
import subprocess


class Interface():
    def __init__(self, game, cell):
        """The interface class is the layer between the user's code and the game
        and houses the methods which will be called by the user. It sends these
        methods to an instance of a NoReferenceInterface via callbacks

        :param game: Game
        :param cell: Cell
        :return: None
        """
        self._game = game
        self._cell = cell
        self._queue = []
        self.on_enemy_callback = None
        self.on_destroy_callback = None
        cb = lambda x: self.check_faulty_cb(x)
        self.no_reference = NoReferenceInterface(self.get_callbacks(), None,
                                                 self.faulty_code, cb)

    def get_callbacks(self):
        """Inspects the class for all methods which start with cb_ and adds it
        to a dictionary of callbacks. This dictionary is used by the
        NoReferenceInterface

        :return: dict(str:func)
        """
        dictionary = {}
        # Gets a list of methods inside Interface
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for name, callback in members:
            # Loads method callback into dictionary
            if name.startswith('cb_'):
                dictionary[name[3:]] = callback
        return dictionary

    def cb_get_enemy_list(self):
        """Returns a list of EnemyInfo's for all enemies on the board

        :return: list(EnemyInfo)
        """
        info_list = []
        for enemy in self._game.enemy_list:
            info_list.append(enemy.info)
        return info_list

    def cb_add_to_queue(self, enemy, i=None):
        """Adds an enemy to the queue. If i is supplied it inserts it at index i

        :param enemy: EnemyInfo
        :return: None
        """
        if i:
            self._queue.insert(i, enemy)
        else:
            self._queue.append(enemy)

    def cb_remove_from_queue(self, enemy=None, i=None, full=False):
        """Removes enemies from the queue. There are three ways the user can do
        this and they can only do one, else the user's code will error.

        If enemy is supplied, it will remove the first instance of that enemy
        from the queue

        If i is supplied, it will remove the enemy from the queue in index i

        If full is True, it will clear the queue

        :param enemy: EnemyInfo
        :param i: int
        :param full: boolean
        :return: None
        """
        length = len(self._queue)
        if enemy is not None and i is None and not full:
            if enemy in self._queue:
                self._queue.remove(enemy)
        elif enemy is None and i is not None and not full:
            if i < length:
                self._queue.pop(i)
            else:
                if self._cell.code in self._game.faulty_codes:
                    self.faulty_code()
                    return
                alert("Warning!", "Supplied value of i is out of range. The "
                                  "length of the queue is" + str(length) + "and"
                                  " i was set to " + str(i) + ". File: " +
                      self._cell.code)
                self.faulty_code()
        elif enemy is None and i is None and full:
            self._queue = []
        else:
            if self._cell.code in self._game.faulty_codes:
                self.faulty_code()
                return
            alert("Warning!", "Invalid usage of remove_from_queue\nMust only "
                              "contain one set argument. Arguments are enemy, "
                              "i, and full.\n\nFile: " + self._cell.code)
            self.faulty_code()

    def cb_get_queue(self):
        """Returns the queue

        :return: list(EnemyInfo)
        """
        return self._queue

    def cb_get_tower(self):
        """Returns information about the tower

        :return: tuple(float, float, float)
        """
        if self._cell.tower:
            damage, max_range = self._cell.damage, self._cell.max_range
            rate = self._cell.rate
            return damage, max_range, rate

    def cb_get_enemies_in_range(self):
        """Returns a list of EnemyInfo's for all enemies within range of the
        tower

        :return: list(EnemyInfo)
        """
        enemies = self.cb_get_enemy_list()
        in_range_enemies = []
        for enemy in enemies:
            if enemy.in_range(self._cell.x, self._cell.y,
                              self._cell.max_range):
                in_range_enemies.append(enemy)
        return in_range_enemies

    def cb_on_new_enemy(self, callback):
        """Sets the callback self.on_enemy_callback to the supplied callback.
        This allows the user to have an event system so they can have code
        triggered when a new enemy is spawned

        :param callback: func
        :return: None
        """
        args = inspect.getargspec(callback)[0]
        if len(args) == 1:
            self.on_enemy_callback = callback
        else:
            if self._cell.code not in self._game.faulty_codes:
                alert("Warning!", "on_new_enemy callback requires 1 argument")
            self.faulty_code()

    def cb_on_destroy_enemy(self, callback):
        """Sets the callback self.on_destroy_callback to the supplied callback.
        This allows the user to have an event system so they can have code
        triggered when an enemy is killed or completes the map


        :param callback: func
        :return: None
        """
        args = inspect.getargspec(callback)[0]
        if len(args) == 1:
            self.on_destroy_callback = callback
        else:
            if self._cell.code not in self._game.faulty_codes:
                alert("Warning!", "on_destroy_enemy callback requires 1 "
                                  "argument")
            self.faulty_code()

    def update_code(self, code):
        """Will load a new NoReferenceInterface with the code supplied in the
        arguments. Will then call the code's start method if the round is under
        way

        :param code: str
        :return: None
        """
        cb = lambda x: self.check_faulty_cb(x)
        self.no_reference = NoReferenceInterface(self.get_callbacks(), code,
                                                 self.faulty_code, cb)
        start_cb = self.no_reference.code_start
        if self._game.round_started and start_cb is not None:
            try:
                start_cb()
            except Exception:
                if self._cell.code not in self._game.faulty_codes:
                    alert("Warning!", "Error when calling start\n" +
                          traceback.format_exc(1) + "\n\nFile: " +
                          self._cell.code)
                self.faulty_code()

    def check_faulty_cb(self, code):
        """Returns whether or not the code, represented as a file name, is in
        the list of known faulty codes

        :param code: str
        :return: boolean
        """
        return code in self._game.faulty_codes

    def faulty_code(self):
        """Notifies the other parts of the code to not use this tower as it has
        faulty code. This can be undone by fixing the error and loading/saving
        it in the game

        :return: None
        """
        if self._cell.code not in self._game.faulty_codes:
            self._game.faulty_codes.append(self._cell.code)
        if self._game.ui_frame.general_frame.selected_cell == self._cell:
            self._game.ui_frame.general_frame.on_select(self._cell)
        self.on_destroy_callback = None
        self.on_enemy_callback = None
        cb = lambda x: self.check_faulty_cb(x)
        self.no_reference = NoReferenceInterface(self.get_callbacks(), None,
                                                 self.faulty_code, cb)

    def get_next_enemy(self):
        """Returns the enemy that is at the top of the queue which is both in
        range of the tower and not dead. Will also check if the tower is able to
        fire at an enemy with it's fire rate

        :return: Enemy or None
        """
        if self._cell._last_shot is None:
            dt = 1 / self._cell.rate
        else:
            dt = time.time() - self._cell._last_shot
        if self._game.fast_forward:
            dt *= 2
        if dt < 1 / self._cell.rate:
            return
        for enemy in self._queue:
            if not enemy.dead and enemy in self._game.enemy_info_dict.keys():
                if enemy.in_range(self._cell.x, self._cell.y,
                                  self._cell.max_range):
                    self._cell._last_shot = time.time()
                    return enemy
            else:
                self._queue = [e for e in self._queue if e != enemy]


class NoReferenceInterface():
    def __init__(self, callbacks, code, error_cb, check_faulty_cb):
        """This class is where the user's code is loaded and executed. It only
        has access to the callbacks supplied so the user will not be able to
        edit game variables such as lives, money etc.

        :param callbacks: dict(str:func)
        :param code: str
        :param error_cb: func
        :param check_faulty_cb: func
        :return: None
        """
        # will execute self.name=callback for all callbacks in the dictionary
        for name, callback in callbacks.items():
            exec("self."+name+"=callback")
        self.code_start, self.code_update = None, None
        if check_faulty_cb(code):
            error_cb()
        elif code is not None:
            file = open(code, 'r')
            code_string = file.read()
            file.close()
            scope = {}
            try:
                # Executes the user's code with an empty globals scope. It still
                # has a local scope however
                exec(code_string, scope)
                if 'update' in scope.keys() and 'start' in scope.keys():
                    start_args = inspect.getargspec(scope['start'])[0]
                    update_args = inspect.getargspec(scope['update'])[0]
                    if len(start_args) == 1 and len(update_args) == 2:
                        self.code_start = (lambda s=self:
                                           scope['start'](s))
                        self.code_update = (lambda dt, s=self:
                                            scope['update'](s, dt))
                    else:
                        alert("Warning!", "Start requires one argument and Up"
                                          "date requires two arguments: " +
                              code)
                        error_cb()
                else:
                    alert("Warning!", "Missing update or start method: " + code)
                    error_cb()
            except:
                alert("Warning!", "Error compiling file\n" +
                      traceback.format_exc(1) + "\n\nFile: " + code)
                error_cb()


class Cell():
    def __init__(self, i, j, is_path, game):
        """This class acts as the cell object. On each tile of the board, there
        is a corresponding cell object loaded. This class will handle addition
        of new towers to a specific cell, and keeping data about the tower if
        it is loaded such as damage, range, and the code which the tower runs on

        :param i: int
        :param j: int
        :param is_path: boolean
        :param game: Game
        :return: None
        """
        self.x = j
        self.y = i
        self.is_path = is_path
        self._game = game
        self.tower = False
        self.damage = None
        self.max_range = None
        self.rate = None
        self.rectangle = None
        self._last_shot = None
        self.code = None
        self.interface = Interface(game, self)

    def add_tower(self, damage, max_range, rate):
        """Sets this cell to contain a tower with the supplied damage, range and
        fire rate. Will then set the code of this tower to be the code loaded
        in the editor

        :param damage: float
        :param max_range: float
        :param rate: float
        :return: None
        """
        if self.is_path:
            return
        self.tower = True
        self.damage = damage
        self.max_range = max_range
        self.rate = rate
        filename = self._game.ui_frame.file_being_edited
        if filename:
            self.update_code(filename)

    def get_colour(self):
        """Returns the colour of the cell for when it is being drawn on the
        canvas

        :return: str
        """
        return "brown" if self.is_path else "forest green"

    def update_code(self, code):
        """Updates the code of the tower and the Interface

        :param code: str
        :return: None
        """
        self.code = code
        self.interface.update_code(code)

    def get_code(self):
        """Returns a name for the code for displaying to the user underneath the
        upgrade purchasing section when the tower is selected

        :return: str
        """
        if self.code is None:
            return "No Selected File"
        else:
            return os.path.basename(self.code)

    def bonus(self, upgrade_type):
        """Returns the string to describe the purchase for the upgrade_type
        supplied

        :param upgrade_type: str
        :return: str
        """
        if upgrade_type == "damage":
            return "+1 " + str(self.get_bonus_cost("damage"))
        elif upgrade_type == "range":
            return "+20 " + str(self.get_bonus_cost("range"))
        elif upgrade_type == "rate":
            return "+0.25 " + str(self.get_bonus_cost("rate"))

    def get_bonus_cost(self, upgrade_type):
        """Returns the cost of the upgrade_type supplied given it's current
        value

        :param upgrade_type: str
        :return: int
        """
        if self.tower:
            if upgrade_type == "damage":
                level = self.damage - 3
                return int(60*level + 20*(level**2))
            elif upgrade_type == "range":
                level = (self.max_range - 100) / 20
                return int(45*level + 15*(level**2))
            elif upgrade_type == "rate":
                level = 4 * self.rate - 2
                return int(65*level + 25*(level**2))

    def upgrade(self, upgrade_type):
        """Will update the corresponding value for the upgrade_type after the
        user has purchased it

        :param upgrade_type: str
        :return: None
        """
        cost = self.get_bonus_cost(upgrade_type)
        if cost <= self._game.money:
            self._game.money -= cost
            if upgrade_type == "damage":
                self.damage += 1
            elif upgrade_type == "range":
                self.max_range += 20
            elif upgrade_type == "rate":
                self.rate += 0.25


class Board():
    SQUARE_NUM = 10

    def __init__(self, game, path_map=None, start=None, end=None):
        """This class keeps track of all the cells in the game, and will also
        generate a list of directions which the enemies will have to traverse.

        :param game: Game
        :param path_map: list(list(boolean))
        :param start: tuple(int, int)
        :param end: tuple(int, int)
        :return: None
        """
        self._path_map = None
        self.start = None
        self.end = None
        if path_map is not None and start is not None and end is not None:
            if len(path_map) == self.SQUARE_NUM:
                invalid_lists = [x for x in path_map if
                                 len(path_map[x]) != self.SQUARE_NUM]
                if len(invalid_lists) == 0:
                    self._path_map = copy.deepcopy(path_map)
                    self.start = start
                    self.end = end
        if self._path_map is None:
            self._path_map = [
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 1, 0, 1, 1, 1, 1, 0],
                [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 1, 1, 0, 0, 0],
                [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
            ]
            self.start = 9, 1
            self.end = 0, 1
        # every grid is split into 4 cells where towers can be placed
        self.cells = [[Cell(i, j, self._path_map[i//2][j//2], game)
                       for i in range(20)] for j in range(20)]

    def calculate_path(self):
        """Returns a list of directions given a 10x10 grid of boolean values
        that represent the path displayed in the game

        :return: list(tuple(float, float))
        """
        path = []
        cur_row, cur_col = self.start
        while True:
            if (cur_row, cur_col) == self.end:
                break
            prev_pos = None
            if len(path) > 0:
                prev_pos = (-1 * path[-1][0], -1 * path[-1][1])
            # Checks all directions around current tile for next adjacent tile
            # excluding the tile that it just came from
            for row, col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if prev_pos != (row, col):
                    if 0 <= cur_row + row < 10 and 0 <= cur_col + col < 10:
                        if self._path_map[cur_row + row][cur_col + col]:
                            path.append((row, col))
                            cur_row, cur_col = cur_row + row, cur_col + col
                            break
        return path


class Enemy():
    def __init__(self, rand, path, start_grid, end_grid, speed, health, game):
        """This class represents an enemy which contains information about its
        position, speed, health etc. It also handles loading the coordinates
        which the enemy will have to pass through and contains an instance
        of EnemyInfo which is what is referenced in the user's code.

        :param rand: float
        :param path: list(tuple(float, float))
        :param start_grid: tuple(int, int)
        :param end_grid: tuple(int, int)
        :param speed: float
        :param health: float
        :param game: Game
        :return:
        """
        self._rand = rand
        self._dir_path = path
        self._start, self._end = start_grid, end_grid
        self._speed = speed
        self._health = health
        self._game = game
        self._enemy_path = None
        self._path_index = 1
        self.dead = False
        self.canvas_element = None
        self._dist_travelled = 0
        self.x, self.y = (self._start[1] + rand) * 80, (self._start[0] + 1) * 80
        self._dir_row, self._dir_col = self._dir_path[0]
        self._rgb_frame = Frame()
        self.calculate_enemy_path()
        self.colour = self.get_colour()
        self.info = EnemyInfo(self.update_info_callback)
        self._game.enemy_info_dict[self.info] = self
        self.info.update()

    def calculate_enemy_path(self):
        """Will turn a list of directions, start and end point, and a random
        start value to calculate a list of x and y coordinates that the enemy
        will pass through

        :return: None
        """
        path = self._dir_path
        row, col = self._start
        enemy_path = [((row + self._rand) * 80, (col + self._rand) * 80)]
        rand_x, rand_y = self._rand, self._rand
        for x in range(len(path) - 1):
            row_dir, col_dir = path[x]
            row, col = row + row_dir, col + col_dir
            # Checks whether or not there is a turn next tile and whether it is
            # right or left
            if ((row_dir == path[x+1][1] and row_dir != 0) or
                    (col_dir == -1 * path[x+1][0] and col_dir != 0)):
                right = False
            elif ((row_dir == -1 * path[x+1][1] and row_dir != 0) or
                  (col_dir == path[x+1][0] and col_dir != 0)):
                right = True
            else:
                enemy_path.append(((row + rand_x) * 80, (col + rand_y) * 80))
                continue
            is_row_dir = row_dir != 0
            forward = (path[x][not is_row_dir] + 1) // 2
            # Uses some logic which was attained from a Karnaugh Map to
            # determine which place in the cell the enemy will visit
            inv_x = ((not is_row_dir and not forward) or
                     (not forward and not right) or
                     (is_row_dir and forward and right))
            inv_y = ((forward and right) or
                     (is_row_dir and forward) or
                     (not is_row_dir and not forward and not right))
            rand_x = self._rand if not inv_x else 1 - self._rand
            rand_y = self._rand if not inv_y else 1 - self._rand
            enemy_path.append(((row + rand_x) * 80, (col + rand_y) * 80))
        enemy_path.append((0, (self._end[1] + self._rand) * 80))
        self._enemy_path = enemy_path

    def move(self, dt):
        """Given a change in time, dt, determines where the enemy should end up
        based on their speed after that change in time. Will also check if the
        enemy has reached the end of the map and will subtract a life and set
        it to dead

        :param dt: float
        :return: None
        """
        if self.dead:
            return
        # Gets the distance that the enemy would have travelled over the time
        # dt. distance = velocity * time
        dist = self._speed * dt
        self._dist_travelled += dist
        if self._dir_row != 0:
            d_left = math.fabs(self._enemy_path[self._path_index][0] - self.y)
        else:
            d_left = math.fabs(self._enemy_path[self._path_index][1] - self.x)
        # checks if the distance will make it go into a new tile, if not. Then
        # continue in same direction with distance specified
        if dist < d_left:
            self.x, self.y = (self.x + (dist * self._dir_col),
                              self.y + (dist * self._dir_row))
        else:
            if len(self._dir_path) == self._path_index + 1:
                self._dir_row, self._dir_col = -1, 0
                self.x = self._enemy_path[self._path_index][1]
                self.y = self._enemy_path[self._path_index][0]
                self._path_index += 1
                self.info.update()
                return
            elif len(self._enemy_path) == self._path_index + 1:
                self.dead = True
                self.x = self._enemy_path[self._path_index][1]
                self.y = self._enemy_path[self._path_index][0]
                self._game.lives -= 1
                self.info.update()
                return
            dist_overshot = dist - d_left
            if len(self._dir_path) >= self._path_index + 1:
                self._dir_row, self._dir_col = self._dir_path[self._path_index]
            self.x = self._enemy_path[self._path_index][1]
            self.y = self._enemy_path[self._path_index][0]
            self._path_index += 1
            self.move(dist_overshot/self._speed)
        self.info.update()

    def update_info_callback(self):
        """Returns information about the enemy which will be called in EnemyInfo
        to get updated data

        :return: tuple(float, float, float, boolean, float, float)
        """
        dist = self.get_distance()
        return self.x, self.y, self._speed, self.dead, self._health, dist

    def get_distance(self):
        """Returns a percentage of completion of the map of this enemy

        :return: float
        """
        return self._dist_travelled / 3200

    def get_colour(self):
        """Returns a colour value which corresponds to the enemies health

        :return: str
        """
        colours = ["Red", "Orange", "Yellow", "Green", "Blue",
                   "Purple", "Pink", "White", "grey66", "grey33", "Black"]
        base = min(math.floor(self._health/15), 10)
        if base == 10:
            return colours[10]
        r1, g1, b1 = self._rgb_frame.winfo_rgb(colours[base])
        r2, g2, b2 = self._rgb_frame.winfo_rgb(colours[base+1])
        scale = (self._health - 15 * base) / 15
        rd, gd, bd = r2 - r1, g2 - g1, b2 - b1
        r3, g3, b3 = r1 + scale * rd, g1 + scale * gd, b1 + scale * bd
        # Converts 16 bit colour into 8 bit colour
        return '#%02x%02x%02x' % (r3 / 256, g3 / 256, b3 / 256)

    def damage(self, damage):
        """Damages this enemy with the damage provided in the arguments. Will
        reduce the health correspondingly, recalculate the speed and colour, and
        will check if health is below 0. At that point it will set it to dead
        and award the player with money

        :param damage: float
        :return: None
        """
        self._health = self._health - damage
        self._speed = max(9.7 * 0.4 * 12, self._health * 12)
        if self._health <= 0:
            self.dead = True
            self._game.money += 5 + self._game.round * 2
        self.colour = self.get_colour()
        self.info.update()


class EnemyInfo():
    def __init__(self, update_callback):
        """This class is the way in which the user will be able to view
        information about enemies inside their code. It comes with a callback
        which when called will update the information.

        :param update_callback: func
        :return: None
        """
        self.callback = update_callback
        self.x, self.y = None, None
        self.speed, self.dead, self.health = None, None, None
        self.completion = None

    def update(self):
        """Update the information inside this EnemyInfo class

        :return: None
        """
        cb = self.callback()
        self.x, self.y, self.speed, self.dead, self.health, self.completion = cb

    def in_range(self, x, y, max_range):
        """Checks if this enemy is inside the range supplied from the x and y
        coordinates. This x, y coordinates and max_range corresponds with a
        tower and is used to check whether the enemy is shoot-able.

        :param x: float
        :param y: float
        :param max_range: float
        :return: boolean
        """
        self.update()
        x1, y1, x2, y2 = self.x, self.y, (x*40)+20, (y*40)+20
        return (max_range ** 2) > ((x1 - x2) ** 2 + (y1 - y2) ** 2)


class CodeFrame(Frame):
    def __init__(self, parent):
        """This class is the frame which houses the code editor

        :param parent: Frame
        :return: None
        """
        Frame.__init__(self, parent)
        self._ui_frame = parent
        self._code_label = None
        self.code_input = None
        self._code_scroll = None
        self.init_widgets()

    def init_widgets(self):
        """Loads code editor into frame and binds tab button to insert_tab

        :return: None
        """
        self._code_label = Label(self, text="Code Editor")
        self.code_input = Text(self, width=60, height=25)
        self.code_input.bind("<Tab>", self.insert_tab)

        self._code_scroll = Scrollbar(self)
        self._code_scroll.config(command=self.code_input.yview)
        self.code_input.config(yscrollcommand=self._code_scroll.set)

        self._code_label.pack(fill=X)
        self._code_scroll.pack(side=RIGHT, fill=Y, expand=False)
        self.code_input.pack(side=LEFT, fill=BOTH, expand=True)

    def insert_tab(self, event):
        """Changes tab button to use 4 spaces rather than /t character

        :param event: event
        :return: str
        """
        self.code_input.insert(INSERT, "    ")
        return "break"


class GeneralFrame(Frame):
    def __init__(self, parent):
        """This frame houses the information about a selected tower

        :param parent: Frame
        :return: None
        """
        Frame.__init__(self, parent, bg='grey94')
        self.ui_frame = parent
        self._game = self.ui_frame.game
        self.selected_cell = None
        self._purchase_frame = None
        self._empty_frame = None
        self._new_tower = None
        self._info_frame = None
        self.init_widgets()

    def init_widgets(self):
        """Initialises and packs various frames

        :return: None
        """
        self._purchase_frame = Frame(self, bg="grey94")
        self._purchase_frame.pack(fill=X)

        self._empty_frame = Frame(self._purchase_frame, height=5)
        self._empty_frame.pack()

        self._new_tower = Button(self._purchase_frame, text="New Tower: 80",
                                 height=2, bg="grey94", fg="Blue",
                                 command=self.on_purchase)
        self._new_tower.pack(fill=X)

        self._info_frame = Frame(self, bg="grey94")
        self._info_frame.pack(fill=BOTH, expand=YES)

    def on_purchase(self):
        """Handles clicking on New Tower button

        :return: None
        """
        cost = 80 + 30 * self._game.towers_bought ** 2
        if self._game.money >= cost and self._new_tower["fg"] == "Blue":
            self._new_tower.config(text="Tower Purchased. Please place tower on"
                                        " the map.\nRight Click on canvas to "
                                        "cancel.",
                                   fg="Black")
            self._game.placing_tower = True

    def on_purchase_placed(self, cancel=False):
        """Handles when the user has placed a purchased tower or cancelled it

        :param cancel: boolean
        :return: None
        """
        cost = 80 + 30 * self._game.towers_bought ** 2
        if not cancel:
            self._game.money -= cost
            self._game.towers_bought += 1
        cost = 80 + 30 * self._game.towers_bought ** 2
        self._new_tower.config(text="New Tower: " + str(cost), fg="Blue")
        self._game.placing_tower = False

    def on_select(self, cell):
        """Fills information about selected tower when it is selected. This
        also includes buttons for purchasing upgrades and selecting the code

        :param cell: Cell
        :return: None
        """
        if cell.tower:
            self.on_deselect()
            self.selected_cell = cell
            damage_frame = Frame(self._info_frame)
            range_frame = Frame(self._info_frame)
            rate_frame = Frame(self._info_frame)
            file_selection_frame = Frame(self._info_frame)

            damage_frame.pack(fill=X)
            range_frame.pack(fill=X)
            rate_frame.pack(fill=X)
            file_selection_frame.pack(fill=X)

            damage_label = Label(damage_frame,
                                 text="Damage: " + str(cell.damage))
            range_label = Label(range_frame,
                                text="Range: " + str(cell.max_range))
            rate_label = Label(rate_frame,
                               text="Fire Rate: " + str(cell.rate))
            file_selection_label = Label(file_selection_frame,
                                         text="File Name: " + cell.get_code())

            if cell.get_code() == "No Selected File":
                file_selection_label.config(fg='red')

            damage_label.pack(side=LEFT)
            range_label.pack(side=LEFT)
            rate_label.pack(side=LEFT)
            file_selection_label.pack(side=LEFT)

            command = lambda c=cell: self.on_purchase_upgrade("damage", c)
            damage_button = Button(damage_frame, command=command, fg="blue",
                                   text="Upgrade: " + cell.bonus("damage"))
            command = lambda c=cell: self.on_purchase_upgrade("range", c)
            range_button = Button(range_frame, command=command, fg="blue",
                                  text="Upgrade: " + cell.bonus("range"))
            command = lambda c=cell: self.on_purchase_upgrade("rate", c)
            rate_button = Button(rate_frame, command=command, fg="blue",
                                 text="Upgrade: " + cell.bonus("rate"))
            command = lambda c=cell: self.choose_file(c)
            file_selection_button = Button(file_selection_frame, fg="blue",
                                           text="Choose File",
                                           command=command)

            damage_button.pack(side=RIGHT)
            range_button.pack(side=RIGHT)
            rate_button.pack(side=RIGHT)
            file_selection_button.pack(side=RIGHT)

            if cell.code in self._game.faulty_codes:
                text = "Error In Code! Click save to view error"
            else:
                text = ""
            label = Label(self._info_frame, fg="red", height=3, text=text)
            label.pack()

            self._game.game_canvas.draw_range_circle(cell)

    def on_deselect(self):
        """Removes all widgets inside info_frame which has upgrade information
        and buttons

        :return: None
        """
        self.selected_cell = None
        for widget in self._info_frame.winfo_children():
            widget.destroy()

    def choose_file(self, cell):
        """Lets user choose file for selected tower

        :param cell: Cell
        :return: None
        """
        options = {'filetypes': [('Python Files', '.py')], 'initialdir': 'code'}
        filename = tkinter.filedialog.askopenfilename(**options)
        if filename.endswith(".txt") or filename.endswith(".py"):
            cell.update_code(filename)
        self.on_deselect()
        self.on_select(cell)

    def on_purchase_upgrade(self, upgrade_type, cell):
        """Refreshes info frame when an upgrade is purchased

        :param upgrade_type: str
        :param cell: Cell
        :return: None
        """
        cell.upgrade(upgrade_type)
        self.on_deselect()
        self.on_select(cell)


class UIFrame(Frame):
    def __init__(self, parent):
        """This Frame houses the CodeFrame, GeneralFrame, menu and play button

        :param parent: Frame
        :return: None
        """
        Frame.__init__(self, parent, background="grey94", bd=2, relief=RIDGE)
        self.game = parent
        self._code_frame = None
        self.general_frame = None
        self._play_button = None
        self.file_being_edited = None
        self.init_widgets()
        if not os.path.exists("code"):
            os.makedirs("code")

    def init_widgets(self):
        """Loads Menu, CodeFrame, GeneralFrame and play_button and packs them

        :return: None
        """

        # Opens on_info in separate thread because it halts the game while it
        # executed. Using a thread will make it run side by side with the game
        command = lambda: threading.Thread(target=self.on_info).start()

        menu_frame = Frame(self)
        menu_frame.pack()
        info_button = Button(menu_frame, text="Information", 
                             command=command, bd=0)
        new_button = Button(menu_frame, text="New", 
                            command=self.on_new, bd=0)
        load_button = Button(menu_frame, text="Load", 
                             command=self.on_load, bd=0)
        save_button = Button(menu_frame, text="Save", 
                             command=self.on_save, bd=0)
        info_button.pack(side=LEFT)
        new_button.pack(side=LEFT)
        load_button.pack(side=LEFT)
        save_button.pack(side=LEFT)

        self._code_frame = CodeFrame(self)
        self.general_frame = GeneralFrame(self)
        self._play_button = Button(self, text="Play", fg="green", height=2,
                                   command=self.on_play)

        self._code_frame.pack(fill=BOTH, expand=YES)
        self.general_frame.pack(fill=BOTH, expand=YES)
        self._play_button.pack(fill=X)

    @staticmethod
    def on_info():
        """Opens documentation. Checks whether there is an internet connection,
        if there is. Open github, else open readme.txt file locally

        :return: None
        """
        try:
            url = 'https://github.com/CameronAavik/Programmable-TD'
            # Checks connection to url
            urllib.request.urlopen(url, timeout=1)
            # Opens it
            webbrowser.open(url)
        except urllib.request.URLError:
            # If connection failed, open local file readme.txt. This is a
            # OS-independent method of opening files
            filename = "readme.txt"
            if sys.platform == "win32":
                os.startfile(filename)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, filename])

    def on_new(self):
        """Creates new file, asks for file name, and fills it with default code
        containing essentials to start writing solution

        :return: None
        """
        default_text = ("def update(game, dt):\n"
                        "    pass\n\n\n"
                        "def start(game):\n"
                        "    game.on_new_enemy(on_new_enemy)\n"
                        "    game.on_destroy_enemy(on_destroy_enemy)\n\n\n"
                        "def on_new_enemy(enemy):\n"
                        "    # called when a new enemy is spawned\n"
                        "    pass\n\n\n"
                        "def on_destroy_enemy(enemy):\n"
                        "    # called when an enemy is killed or finishes\n"
                        "    pass")
        options = {'filetypes': [('Python Files', '.py')],
                   'initialdir': 'code', 'defaultextension': '.py'}
        filename = tkinter.filedialog.asksaveasfilename(**options)
        if filename:
            self.on_save()
            self.file_being_edited = filename
            file = open(filename, 'w')
            file.close()
            self._code_frame.code_input.delete(1.0, END)
            self._code_frame.code_input.insert(INSERT, default_text)

    def on_load(self):
        """Asks user for filename to load into code editor. Will also update
        any towers that use that code in case it was edited outside the game

        :return: None
        """
        options = {'filetypes': [('Python Files', '.py')],
                   'initialdir': 'code'}
        filename = tkinter.filedialog.askopenfilename(**options)
        if filename:
            self.file_being_edited = filename
            file = open(filename, 'r')
            self._code_frame.code_input.delete(1.0, END)
            self._code_frame.code_input.insert(INSERT, file.read())
            file.close()
            if self.file_being_edited in self.game.faulty_codes:
                self.game.faulty_codes.remove(self.file_being_edited)
            for tower in self.game.towers:
                if tower.code == filename:
                    tower.update_code(filename)
        if self.general_frame.selected_cell:
            self.general_frame.on_select(self.general_frame.selected_cell)

    def on_save(self):
        """Will save the file written in the code editor when save button is
        pressed or ctrl+s is used. Checks if a file has been associated with
        the code editor and will ask for a file name if there isn't. Then
        updates the code for all towers that use this code

        :return: None
        """
        if self.file_being_edited is None:
            options = {'filetypes': [('Python Files', '.py')],
                       'initialdir': 'code', 'defaultextension': '.py'}
            filename = tkinter.filedialog.asksaveasfilename(**options)
            if filename:
                self.file_being_edited = filename
                file = open(filename, 'w')
                file.close()
        if self.file_being_edited:
            file = open(self.file_being_edited, 'w')
            file.write(self._code_frame.code_input.get(1.0, END))
            file.close()
            if self.file_being_edited in self.game.faulty_codes:
                self.game.faulty_codes.remove(self.file_being_edited)
            for tower in self.game.towers:
                if tower.code == self.file_being_edited:
                    tower.update_code(self.file_being_edited)
        if self.general_frame.selected_cell:
            self.general_frame.on_select(self.general_frame.selected_cell)

    def on_play(self):
        """Starts round if the round isn't started. If round is on, toggles
        fast forward

        :return: None
        """
        status = ["Off", "On"]
        if self._play_button["text"] == "Play":
            self.game.start_round()
            self._play_button.config(text="Fast Forward: " +
                                          status[self.game.fast_forward])
        else:
            self.game.fast_forward = not self.game.fast_forward
            self._play_button.config(text="Fast Forward: " +
                                          status[self.game.fast_forward])

    def round_finished(self):
        """Changes play button text back to 'Play' once round has finished

        :return: None
        """
        self._play_button.config(fg="green", text="Play")


class GameCanvas(Canvas):
    # Canvases and Cells are square
    CANVAS_SIZE = 800
    CELL_SIZE = 40

    def __init__(self, game):
        """This class is the canvas which displays the map and handles clicking

        :param game:
        :return: None
        """
        Canvas.__init__(self, game, bg="grey94",
                        width=self.CANVAS_SIZE, height=self.CANVAS_SIZE)
        self._game = game
        self.bind('<Button-1>', self.on_canvas_click)
        self.bind('<Button-3>', self.on_canvas_right_click)
        self.bind('<Motion>', self.on_canvas_motion)
        self.bind('<Leave>', self.on_canvas_leave)
        self._hover_cell = None
        self._hover_rectangle = None
        self._range_display_select = None
        self._round_label = self.create_text(0, 0, text="Round: 0")
        self._lives_label = self.create_text(0, 0, text="Lives: 100")
        self._money_label = self.create_text(0, 0, text="Money: 250")
        self._towers = []
        self._bullets = {}

    def draw_tile(self, row, column, colour):
        """Draws a cell at the given row and column with the specified colour

        :param row: int
        :param column: int
        :param colour: str
        :return: Rectangle
        """
        x1, y1 = row * self.CELL_SIZE, column * self.CELL_SIZE
        x2, y2 = x1 + self.CELL_SIZE, y1 + self.CELL_SIZE
        return self.create_rectangle(x1, y1, x2, y2, 
                                     fill=colour, outline=colour)

    def update_all(self, dt):
        """Calls update methods of the canvas

        :param dt: float
        :return: None
        """
        self.update_enemies(dt)
        self.update_info()
        self.update_bullets()

    def update_enemies(self, dt):
        """Updates the positions of enemies and checks if they are dead to
        remove them from the canvas

        :param dt: float
        :return: None
        """
        for enemy in self._game.enemy_list:
            enemy.move(dt)
            if enemy.dead:
                self._game.dead_enemies.append(enemy)
                continue
            x1, y1 = enemy.x - 8, enemy.y - 8
            x2, y2 = x1 + 16, y1 + 16
            self.coords(enemy.canvas_element, x1, y1, x2, y2)
            self.itemconfig(enemy.canvas_element, fill=enemy.colour)
        for dead_enemy in self._game.dead_enemies:
            self.destroy_enemy(dead_enemy)
        self._game.dead_enemies = []

    def update_bullets(self):
        """Checks if any bullets need to be removed from the screen if they have
        been there for a period of time and removes them

        :return: None
        """
        bullets_to_remove = []
        for bullet, timestamp in self._bullets.items():
            val = 0.125 if self._game.fast_forward else 0.25
            if time.time() - timestamp >= val:
                bullets_to_remove.append(bullet)
        for bullet in bullets_to_remove:
            self.delete(bullet)
            del self._bullets[bullet]

    def update_info(self):
        """Updates the statistics in the top right corner

        :return: None
        """
        wave, lives, money = (self._game.round, self._game.lives,
                              self._game.money)
        width = self.winfo_width()
        self.delete(self._round_label)
        self.delete(self._lives_label)
        self.delete(self._money_label)
        self._round_label = self.create_text(width-5, 10, anchor=E,
                                             text="Round: " + str(wave))
        self._lives_label = self.create_text(width-5, 25, anchor=E,
                                             text="Lives Left: " + str(lives))
        self._money_label = self.create_text(width-5, 40, anchor=E,
                                             text="Money: " + str(money))

    def destroy_enemy(self, enemy):
        """When an enemy is killed it removes it's footprint from all places in
        the code. Then calls on_destroy_enemy callback from all tower's codes'

        :param enemy: Enemy
        :return: None
        """
        if enemy in self._game.enemy_list:
            self._game.enemy_list.remove(enemy)
        if enemy.info in self._game.enemy_info_dict.keys():
            del self._game.enemy_info_dict[enemy.info]
        self.delete(enemy.canvas_element)
        for tower in self._game.towers:
            cb = tower.interface.on_destroy_callback
            if cb is not None:
                try:
                    cb(enemy.info)
                except:
                    if tower.code not in self._game.faulty_codes:
                        alert("Warning!", "Error with on_new_enemy callback\n" +
                              traceback.format_exc(1))
                    tower.interface.faulty_code()

    def on_canvas_click(self, event):
        """Selects the cell that the user clicked on

        :param event: Event
        :return: None
        """
        self.select_cell(self.get_cell(event.x, event.y))

    def on_canvas_right_click(self, event):
        """Cancels placement of tower if one was bought but not placed yet

        :param event: Event
        :return: None
        """
        if self._game.placing_tower:
            self._game.ui_frame.general_frame.on_purchase_placed(cancel=True)

    def on_canvas_motion(self, event):
        """Draws a rectangle that hovers over the cell that the mouse is above
        and highlights it a colour that associates whether a tower is able to
        be placed there or not

        :param event: Event
        :return: None
        """
        cell = self.get_cell(event.x, event.y)
        if cell == self._hover_cell:
            self._hover_cell = cell
            return
        if self._hover_cell is not None and self._hover_rectangle is not None:
            self.delete(self._hover_rectangle)
            self._hover_rectangle = None
        if cell is not None:
            x1, y1 = cell.x * self.CELL_SIZE, cell.y * self.CELL_SIZE
            x2, y2 = x1 + self.CELL_SIZE, y1 + self.CELL_SIZE
            colour = "green"
            if cell.is_path or cell.tower:
                colour = "red"
            self._hover_rectangle = self.create_rectangle(x1, y1, x2, y2,
                                                          fill=colour,
                                                          stipple='gray50')
        self._hover_cell = cell

    def on_canvas_leave(self, event):
        """Removes the rectangle that hovers the map if the mouse leaves the
        canvas

        :param event: Event
        :return: None
        """
        self.delete(self._hover_rectangle)
        self._hover_rectangle = None

    def get_cell(self, x, y):
        """Given an x, y coordinate on the canvas, returns the corresponding
        Cell

        :param x: float
        :param y: float
        :return: Cell
        """
        if self.CANVAS_SIZE > y >= 0 and self.CANVAS_SIZE > x >= 0:
            return self._game.board.cells[x//self.CELL_SIZE][y//self.CELL_SIZE]

    def draw_tower(self, tower):
        """Draws grey square when a tower is purchased and placed on the tower
        provided in the argument

        :param tower: Cell
        :return: None
        """
        x1, y1 = tower.x * 40 + 5, tower.y * 40 + 5
        x2, y2 = x1 + 30, y1 + 30
        self._towers.append(self.create_rectangle(x1, y1, x2, y2,
                                                  fill="grey"))
        self._game.towers.append(tower)

    def spawn_bullet(self, cell, enemy):
        """Draws a line from the cell/tower to the enemy and adds it to a
        dictionary of bullets that keeps track of line and time it was placed

        :param cell: Cell
        :param enemy: Enemy
        :return: None
        """
        x1, y1 = cell.x * 40 + 20, cell.y * 40 + 20
        x2, y2 = enemy.x, enemy.y
        self._bullets[self.create_line(x1, y1, x2, y2)] = time.time()

    def draw_range_circle(self, tower):
        """Draws circle around the selected tower to indicate its range

        :param tower: Cell
        :return: None
        """
        if self._range_display_select is not None:
            self.delete(self._range_display_select)
        max_range = tower.max_range
        x, y = 40 * (tower.x + 0.5), 40 * (tower.y + 0.5)
        x1, y1 = x - max_range, y - max_range
        x2, y2 = x + max_range, y + max_range
        self._range_display_select = self.create_oval(x1, y1, x2, y2)

    def select_cell(self, cell):
        """Places tower if one was purchased but not placed yet, and then tells
        the ui frame to display info if the cell selected was a tower

        :param cell: Cell
        :return: None
        """
        if self._game.placing_tower and not cell.is_path and not cell.tower:
            cell.add_tower(5, 140, 1)
            self.draw_tower(cell)
            self._game.ui_frame.general_frame.on_purchase_placed()
            self.draw_range_circle(cell)
        if cell.tower:
            self._game.ui_frame.general_frame.on_select(cell)
            self.draw_range_circle(cell)
        elif not self._game.placing_tower:
            self._game.ui_frame.general_frame.on_deselect()
            if self._range_display_select is not None:
                self.delete(self._range_display_select)
                self._range_display_select = None

    def spawn_enemy(self, enemy):
        """Spawns enemy on the map and sets the canvas element to a property
        of the enemy

        :param enemy: Enemy
        :return: None
        """
        x1, y1 = enemy.x - 8, enemy.y + 8
        x2, y2 = x1 + 16, y1 + 16
        colour = enemy.colour
        enemy.canvas_element = self.create_oval(x1, y1, x2, y2, fill=colour)


class Game(Frame):
    def __init__(self, parent):
        """Class which ties all parts of the code together and initialises
        the various data structures

        :param parent: Tk
        :return: None
        """
        Frame.__init__(self, parent, background="grey94")
        self._parent = parent
        self._parent.title("Programmable Tower Defense")
        self.pack(fill=BOTH, expand=YES)
        self._parent.bind("<Control-s>", lambda event: self.ui_frame.on_save())

        self._divisions = 20

        self.enemy_list = []
        self.dead_enemies = []
        self.round = 0
        self.lives = 100
        self.money = 250
        self.round_started = False
        self.time_between_enemies = None
        self.enemy_spawn_queue = []
        self.last_enemy_time = None
        self.placing_tower = False
        self.towers = []
        self.enemy_info_dict = {}
        self.towers_bought = 0
        self.fast_forward = False
        self.faulty_codes = []
        self.board = None
        self.enemy_path = None
        self._last_time = None
        
        self.init_game()
        
        self.ui_frame = None
        self.game_canvas = None
        
        self.init_widgets()
        self.init_map()

    def init_game(self):
        """Sets some initial values for the game

        :return: None
        """
        self.board = Board(self)
        self.enemy_path = self.board.calculate_path()
        self._last_time = time.time()

    def init_widgets(self):
        """Initialises and packs the UI Frame and the Game Canvas

        :return: None
        """
        self.ui_frame = UIFrame(self)
        self.game_canvas = GameCanvas(self)

        self.ui_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        self.game_canvas.pack(side=LEFT)

    def init_map(self):
        """Draws the tiles for each cell on the canvas

        :return: None
        """
        for row in range(self._divisions):
            for column in range(self._divisions):
                cell = self.board.cells[row][column]
                colour = cell.get_colour()
                cell.rectangle = self.game_canvas.draw_tile(row, column, colour)

    def game_loop(self):
        """Part of the code that is constantly called, it keeps track of the
        time elapsed between each loop to be sent to the parts of the code that
        need it. Will also check if lives is 0 and call game over, as well as
        call handle_round if there is a round under way

        :return: None
        """
        if self.lives == 0:
            self.game_over()
        cur_time = time.time()
        dt = cur_time - self._last_time
        if self.fast_forward:
            dt *= 2
        if self.round_started:
            self.handle_round(dt)
        self._last_time = cur_time
        self.game_canvas.update_all(dt)
        # executes self.game_loop again 1 ms after this call
        self._parent.after(1, self.game_loop)

    def handle_round(self, game_dt):
        """Spawns enemy if it is ready to spawn, ends wave if it is finished,
        calls the update method of each tower and the on_new_enemy callback for
        each tower if there was an enemy spawned. It also goes through and
        shoots the enemy that is pulled from the queue for each tower if it
        returns one

        :param game_dt: float
        :return: None
        """
        if self.last_enemy_time is None:
            dt = self.time_between_enemies + 1
        else:
            dt = time.time()-self.last_enemy_time
        if self.fast_forward:
            dt *= 2
        if len(self.enemy_list) == 0 and len(self.enemy_spawn_queue) == 0:
            self.end_round()
            return
        if dt >= self.time_between_enemies and len(self.enemy_spawn_queue) > 0:
            self.enemy_list.append(self.enemy_spawn_queue[0])
            for tower in self.towers:
                cb = tower.interface.on_enemy_callback
                if cb is not None:
                    try:
                        cb(self.enemy_spawn_queue[0].info)
                    except:
                        alert("Warning!", "Error with on_destroy_enemy callback"
                                          "\n" + traceback.format_exc(1))
                        tower.interface.faulty_code()
            self.last_enemy_time = time.time()
            self.enemy_spawn_queue.pop(0)
        for tower in self.towers:
            no_ref_int = tower.interface.no_reference
            if no_ref_int.code_update is not None:
                try:
                    no_ref_int.code_update(game_dt)
                except:
                    alert("Warning!", "Error when calling update\n" +
                          traceback.format_exc(1))
                    tower.interface.faulty_code()
            next_in_queue = tower.interface.get_next_enemy()
            if next_in_queue is not None:
                enemy = self.enemy_info_dict[next_in_queue]
                enemy.damage(tower.damage)
                self.game_canvas.spawn_bullet(tower, enemy)

    def start_round(self):
        """Sets variables to signify a new round has started, generates the list
         of enemies that will be spawned in the round, and calls the start
         method for each tower

        :return: None
        """
        self.round_started = True
        self.round += 1
        # This will get to 0.1 at approximately round 50
        self.time_between_enemies = max(0.1, (0.95 ** self.round))
        if self.round < 50:
            num_enemies = round(10 + self.round*2 + 0.1 * self.round ** 2 + 
                                0.02 * self.round ** 3)
        else:
            num_enemies = round(50 * self.round + 150)
        max_health = 1.7 * self.round + 8
        for i in range(num_enemies):
            health = max((1 - random.random()**3), 0.4) * max_health
            speed = health * 12
            path, start, end = (self.enemy_path,
                                self.board.start, self.board.end)
            enemy = Enemy(random.random(), path, start, end, 
                          speed, health, self)
            self.game_canvas.spawn_enemy(enemy)
            self.enemy_spawn_queue.append(enemy)
        for tower in self.towers:
            no_ref_int = tower.interface.no_reference
            if no_ref_int.code_start is not None:
                try:
                    no_ref_int.code_start()
                except:
                    alert("Warning!", "Error when calling start\n" +
                          traceback.format_exc(1))
                    tower.interface.faulty_code()

    def end_round(self):
        """Tells game that round is over and awards the player with money for
        completing it

        :return: None
        """
        self.round_started = False
        self.enemy_spawn_queue = []
        self.ui_frame.round_finished()
        self.money += round(50 + 15 * self.round + 0.1 * self.round ** 2)

    def game_over(self):
        """Pops up with a message box notifying the user they lost, then resets
        all the variables to what they were at the beginning of the game

        :return: None
        """
        # Using messagebox instead of alert will halt the game until OK is
        # pressed
        tkinter.messagebox.showinfo(message="You lost at round: " +
                                            str(self.round) +
                                            ". Close this message box to retry")
        self.ui_frame.destroy()
        self.game_canvas.destroy()
        self.enemy_list = []
        self.dead_enemies = []
        self.round = 0
        self.lives = 100
        self.money = 250
        self.round_started = False
        self.time_between_enemies = None
        self.enemy_spawn_queue = []
        self.last_enemy_time = None
        self.placing_tower = False
        self.towers = []
        self.enemy_info_dict = {}
        self.towers_bought = 0
        self.fast_forward = False
        self.faulty_codes = []
        self.board = None
        self.enemy_path = None
        self._last_time = None
        self.init_game()
        self.init_widgets()
        self.init_map()


def alert(title, message):
    """Displays alert in window in separate thread so it doesn't halt execution
    of the game. Will have title and message supplied in arguments

    :param title: str
    :param message: str
    :return: None
    """
    # Creates new Tk instance so it is in separate thread
    m_box = Tk()
    m_box.title(title)
    m_box.geometry('300x300')
    l = Label(m_box, text=message, bg='grey94', wraplength=300, justify=LEFT)
    l.pack(padx=1, pady=1)
    b = Button(m_box, text="Close", command=m_box.destroy)
    b.pack(side=BOTTOM)


def main():
    root = Tk()
    game = Game(root)
    root.after(1, game.game_loop())
    root.mainloop()

if __name__ == '__main__':
    main()