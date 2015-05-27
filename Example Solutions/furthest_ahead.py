def update(game, dt):
    # Clears the queue for the tower
    game.remove_from_queue(full=True)
    # Gets the list of enemies 
    enemies = game.get_enemy_list()
    # Gets list of enemies sorted by their completion in descending order
    sorted_list = sorted(enemies, key=lambda x: x.completion, reverse=True)
    for enemy in sorted_list:
        # Adds that enemy to the queue
        game.add_to_queue(enemy)
    # At this point the queue will have the enemy that is furthest ahead
    # on the map. When the tower is able to shoot again it will shoot the
    # enemy that is the highest up the list that is in range of the tower.


def start(game):
    # Sets the callbacks which will be called when new enemies are
    # spawned or destroyed
    game.on_new_enemy(on_new_enemy)
    game.on_destroy_enemy(on_destroy_enemy)


def on_new_enemy(enemy):
    # This is called when a new enemy is loaded
    pass


def on_destroy_enemy(enemy):
    # This is called when an enemy is killed or makes it to the end
    pass









