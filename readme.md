# Summary
This is a tower defense game where the player must write the source code which the towers run off.
Towers will not automatically shoot so this allows for you to make your towers shoot whoever they want.

# Installation
Once you have downloaded the .zip there should be only one file of interest. This file is main.py and is what needs to be run to play the game. First, extract the .zip file to a separate folder.
Before you play the game you will need to have Python 3 installed on your computer. You can download Python from the below link

[Python Download](https://www.python.org/downloads/)

To start playing, double click on main.py

# How to Play

This game has two main sections, the main user interface, and the map on the right. To start off you can create a New Tower by clicking on "New Tower: 80" button. This will allow you to click on where on the map you would like to place the tower, it will be beneficial to place it so that the tower can cover as much area of the path as possible. Once that is done you should see that the money in the top right will have subtracted because of this purchase.

For these towers to work it needs to have code associated with it! For this, we will need to create a new file. To do this, click on the New button in the menu above the code editor. Type in a filename, it can be whatever you want however it must be a .py file (.py will automatically be appended to filename if it's missing).

Now you will see that there is some placeholder code there for you, however it has no actual functionality at this point. You can either add your own code or you can paste in some example code pre-written which will make each tower automatically shoot the target that has travelled the furthest that is in its range. This example code can be seen below:

[Example Code](https://github.com/CameronAavik/Programmable-TD/blob/master/Example%20Solutions/furthest_ahead.py)

When you have copied and pasted this into your text window (replacing everything), either press Save or Ctrl+s to save it to the file. Now we can add this code to the tower. Select the tower on the map and click on "Choose File". Then select the code which we just saved and it should be loaded. Notice, that if you buy a second tower and place it, it will automatically have this code loaded. Whenever you create a new tower it checks if there is a file loaded into the Code Editor and uses that if there is.

If you wish to load some code created before without creating a new file, you can simply click on the Load button at the top and select the file you wish to be loaded into the editor. Also, if you start typing code into the code editor without associating it to a file, saving will prompt you for a file name to save it as.

Now, if you look at the information above the play button when you have selected a tower there is three attributes to pay attention to: Damage, Range, and Fire Rate.

Damage: Number of damage dealt to an enemy every shot  
Range: Range around the tower with which it can shoot enemies from (represented by black circle when selected)  
Fire Rate: Number of times per second this tower can shoot

With that done, you can click Play. This will start the round and on Round 1, 12 enemies will spawn with a maximum health of 9.7, this means that each enemy will take 1 - 2 shots from each tower to kill. If you placed the towers in a good location, and you have good code or are using the example, you will be able to get through this round without losing an enemy. Whenever you kill an enemy you will get a small amount of money, you will also get money when you complete a wave. Once that round is done, you should have enough money to spend on something. With that money you have 4 options:

1. Upgrade the damage of one of the towers
2. Upgrade the range of one of the towers
3. Buy a new tower
4. Save money so you can spend it on something worth more (such as fire rate)

Throughout the game you will need to make many decisions like these and after playing this game for a while you will be able to determine which choice is the better investment. Also worth noting, is that all purchases will increase the price of the next purchase. A list of equations which are used for different things is located in the Equations section. Now you can start round 2. Some more useful things to notice is that if you feel that the game is a little slow, you can click on "Fast Forward" which is where the Play button is located during the round. This will enable fast forward for all future rounds. You can disable it again if you wish by clicking it again during a round. Also, you are able to buy new towers and upgrade them as well as modify/switch the code for the tower during the game. Whenever an enemy gets through to the end of the path, it will decrease your number of lives by 1, when the lives gets to 0 it is game over and you must restart

There is no end to this game, the objective is to get as far as possible before you end up with 0 lives. Also, the code you write or load is saved so if you close and reopen it, it will still be there for you to load into the game. On the github for this game (Pops up when you click on Information button), there is a folder called Example Solutions where anyone can upload their own code solutions for others to play around with. Always be wary however though, that you should never run code you don't trust. There is the capability in python to do very bad things such as deleting files or installing viruses/malware onto your computer by downloading it from a site. All the code that is accepted to the github repository will be checked for anything malicious however so they will most likely be safe to run.

Now see if you can make a better solution which has different towers fulfilling different roles! An example could be to have weak towers shoot weakest enemies and stronger towers shoot the strongest enemies, meaning that the strongest tower does not have to worry about enemies that are going to easily be cleaned up later

# API
**You must implement two methods in your code, otherwise it will error. These two are start and update.**

*start(game)*  
*start* must have one argument in its definition. This argument is what contains the methods and functions for you to call in your code. Start will be called at the start of every round and will also be called whenever the user changes the code mid-round.

*update(game, dt)*  
*update* must have two arguments in its definition. The first argument is the same as the game argument from start, the second argument contains the change in time since the last update. This will most likely not be used in many cases, but is included in case anyone needs access to it. Update is called constantly every loop of the game. Also note, that if you make the update method take too long it will hang the game since it waits for the update method to finish before continuing on with the game, so keep performance in mind when writing your code.

**The methods below are what are avaialble from the game argument supplied to start and update**  

*game.get_enemy_list()*  
Returns a list of enemies. These enemies have properties and methods which are mentioned below

*game.get_queue()*  
Returns the queue. The queue is the order of preferences for the next target that the tower will shoot. When the tower is able to shoot (determined by fire rate), it will go through the queue and find the first enemy in the queue which is both in the range of the tower and is not dead. It then shoots this tower.

*game.add_to_queue(enemy, i=int)*  
Adds the enemy, which can be gotten from game.get_enemy_list(), to the queue at index i. i defaults to None so it will be appended to the end of the queue if not specified

*game.remove_from_queue(enemy=Enemy, i=int, full=boolean)*  
This method must take one named argument, and only one. If you set the values for two of them it will fail. If you use the enemy argument, it removes the first instance of that enemy from the queue, if that enemy is not in the queue, it will ignore this call and continue with same list. If you use the i argument, it removes the enemy in index i in the queue, if i is out of range, then it will also raise an error. If you set the full variable to True, then it clears the entire queue.

*game.get_tower()*  
This method returns a tuple of 3 values, the damage, max_range, and rate of the tower. All three values are assumed to be floats, despite possibly being ints.

*game.get_enemies_in_range()*  
Returns a list of enemies that are in range of the tower

*game.on_new_enemy(callback)*  
Will set the method defined in the callback to be called whenever a new enemy is spawned. Example usage can be seen in the default code's start method when pressing New

*game.on_destroy_enemy(callback)*  
Will set the method defined in the callback to be called whenever an enemy is killed or finishes the whole map. Example usage can be seen in the default code's start method when pressing New

**Given an enemy which such as one from game.get_enemy_list(), these are the attributes and methods of the enemy**  

*enemy.x*  
Returns the x position of the enemy on the canvas

*enemy.y*  
Returns the y position of the enemy on the canvas

*enemy.health*  
Returns the health of the enemy

*enemy.speed*  
Returns the speed of the enemy

*enemy.dead*  
Returns boolean value of whether or not the enemy is now dead

*enemy.completion*  
Returns a number between 0 and 1 which indicates how much of the path has been traversed by this enemy. 0.5 means that it is halfway

*enemy.in_range(x, y, max_range)*  
Returns a boolean value stating whether or not the enemy is in the range of the circle denoted with a center at (x, y) and radius of max_range. This can be used to check if an enemy is in the range of a tower with its x, y, and max_range properties

# Equations

In the following three equations, level means the number of times the upgrade/tower has been purchased, a new tower starts at level 1, so the first purchase is level 2

*Cost of damage upgrade*  
60 * level + 20 * level^2

*Cost of range upgrade*  
45 * level + 15 * level^2

*Cost of fire rate upgrade*  
65 * level + 25 * level^2

*Cost of tower*  
80 + 30 * towers_bought^2

*Time between enemy spawns*  
max(0.1, (0.95 ^ round_number))

*Number of enemies spawned per round (The calculated number is rounded to nearest integer)*  
if round_number < 50:  
10 + round_number * 2 + 0.1 * round_number ^ 2 + 0.02 * round_number ^ 3  
if round_number >= 50  
50 * round_number + 150  

*Starting health of enemy*  
max_health = 1.7 + round_number * 8  
rand = random number between 0 and 1  
enemy_health = max((1 - rand ^ 3), 0.4) * max_health  

*Speed of enemy*  
max(46.54, enemy.health * 12)

*Money gained from killing enemy*  
5 + 2 * round_number

*Money gained from winning round (The calculated number is then rounded to nearest integer)*  
50 + 15 * round_number + 0.1 * round_number ^ 2