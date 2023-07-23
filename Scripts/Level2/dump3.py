from argparse import ArgumentParser
import os
from random import choice
import vizdoom as vzd
import numpy as np
import cv2
import math
from vizdoom import GameVariable
from pynput import keyboard

class PIDController:
    def __init__(self, kp=0.001, ki=0.001, kd=0.2):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def update(self, error):
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative

def on_press(key):
    try:
        if key.char == 'q':
            cv2.destroyAllWindows()
            game.close()
            return False  # Stop the listener
    except AttributeError:
        pass

def achieved(agent_x, agent_y, target_x, target_y):
    if get_distance_to_next(agent_x, agent_y, target_x, target_y) < 100:
        return True
    return False


def get_angle_from_agent(agent_angle_degrees, agent_x, agent_y, target_x, target_y):
    # Calculate the relative x and y distance from the agent to the target point
    delta_x = target_x - agent_x
    delta_y = target_y - agent_y

    # Calculate the angle between the agent's facing direction and the target point
    target_angle_radians = math.atan2(delta_y, delta_x)
    target_angle_degrees = math.degrees(target_angle_radians)

    # Adjust the angle to be relative to the agent's facing direction
    relative_angle_degrees = target_angle_degrees - agent_angle_degrees

    # Ensure the angle is within the range of -180 to 180 degrees
    while relative_angle_degrees <= -180:
        relative_angle_degrees += 360
    while relative_angle_degrees > 180:
        relative_angle_degrees -= 360

    return relative_angle_degrees

def get_distance_to_next(agent_x, agent_y, target_x, target_y):
    # Calculate the relative x and y distance from the agent to the target point
    delta_x = target_x - agent_x
    delta_y = target_y - agent_y

    return (delta_x**2 + delta_y**2)**0.5

def graph(node, parent, graph):
    graph[node] = [0, parent]
    return graph

def position_update(current_positon, angle_degrees):
    if angle_degrees == 270:
        return ((current_positon[0], current_positon[1] - 20))
    elif angle_degrees == 180:
        return ((current_positon[0] - 20, current_positon[1]))
    elif angle_degrees == 90:
        return ((current_positon[0], current_positon[1] + 20))
    elif angle_degrees == 0:
        return ((current_positon[0] + 20, current_positon[1]))



if __name__ == "__main__":

    """
    ############################################################################################################################################################
    These are pre-set configurations for level2 of the task, please dont change them

    ############################################################################################################################################################
    """

    game = vzd.DoomGame()

    game.set_doom_scenario_path(
        os.path.join(os.path.expanduser('~'), "Documents", "AGVSoftware", "AGVSoftwareTask", "WADFiles", "MAP01.wad"))

    # OpenCV uses a BGR colorspace by default.
    game.set_screen_format(vzd.ScreenFormat.BGR24)

    # Sets resolution for all buffers.
    game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)

    # Enables depth buffer.
    game.set_depth_buffer_enabled(True)

    # Enables labeling of in game objects labeling.
    game.set_labels_buffer_enabled(True)

    # Disables buffer with top down map of he current episode/level .
    game.set_automap_buffer_enabled(False)
    game.set_automap_mode(vzd.AutomapMode.OBJECTS)
    game.set_automap_rotate(False)
    game.set_automap_render_textures(False)

    # game.set_render_hud(True)
    game.set_render_hud(False)
    game.set_render_minimal_hud(False)

    """
    ##############################################################################################################################################################
    Feel free to change anything after this
    ##############################################################################################################################################################
    """
    # uncomment this if you want to play the game with keyboard controls
    # game.set_mode(vzd.Mode.SPECTATOR)
    game.set_episode_timeout(9999999)
    # Adds delta buttons that will be allowed and set the maximum allowed value (optional).
    '''game.add_available_button(vzd.Button.MOVE_FORWARD_BACKWARD_DELTA, 10)
    game.add_available_button(vzd.Button.MOVE_LEFT_RIGHT_DELTA, 5)
    game.add_available_button(vzd.Button.TURN_LEFT_RIGHT_DELTA, 5)
    game.add_available_button(vzd.Button.LOOK_UP_DOWN_DELTA)'''

    game.add_available_button(vzd.Button.MOVE_FORWARD_BACKWARD_DELTA, 10)
    game.add_available_button(vzd.Button.MOVE_LEFT_RIGHT_DELTA, 5)
    game.add_available_button(vzd.Button.TURN_LEFT_RIGHT_DELTA, 90)
    game.add_available_button(vzd.Button.LOOK_UP_DOWN_DELTA)

    # Add game variables to the game before starting the episode
    game.add_available_game_variable(GameVariable.POSITION_X)
    game.add_available_game_variable(GameVariable.POSITION_Y)
    game.add_available_game_variable(GameVariable.ANGLE)
    game.add_available_game_variable(GameVariable.POSITION_Z)
    # For normal buttons (binary) all values other than 0 are interpreted as pushed.
    # For delta buttons values determine a precision/speed.
    #
    # For TURN_LEFT_RIGHT_DELTA and LOOK_UP_DOWN_DELTA value is the angle (in degrees)
    # of which the viewing angle will change.
    #
    # For MOVE_FORWARD_BACKWARD_DELTA, MOVE_LEFT_RIGHT_DELTA, MOVE_UP_DOWN_DELTA (rarely used)
    # value is the speed of movement in a given direction (100 is close to the maximum speed).
    action = [0, 0, 0, 0] # floating point values can be used

    # check this link for all available game variables, use any you find useful: https://github.com/mwydmuch/ViZDoom/blob/master/doc/Types.md#gamevariable
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    game.init()

    episodes = 10
    sleep_time = 0.028



    while True:
        count = 0
        graph_nodes = {}
        parent = -1
        node = -1

        explored_max = None
        not_explored = 4

        abandoned = []

        # episode ends after you reach the key(end of game) or after a given time(300 seconds fixed in the config file)
        while not game.is_episode_finished():
            # Gets the state and possibly do something with it
            state = game.get_state()

            x_position = state.game_variables[0]
            y_position = state.game_variables[1]
            angle_degrees = state.game_variables[2]

            current_positon = (x_position, y_position)

            # Shows the depth map of the current episode/level.
            depthmap = state.depth_buffer
            if depthmap is not None:
                cv2.imshow('ViZDoom Depth Buffer', depthmap)

            cv2.waitKey(int(sleep_time * 1000))


            '''# shows the segmented areas of any objects in the map
            labelsmap = state.labels_buffer
            if labelsmap is not None:
                cv2.imshow('ViZDoom Labels Buffer', labelsmap)'''

            # EXPLORE THE BLOCK:
            if not_explored == 4:

                node = current_positon
                if (position_update(node, int(angle_degrees))) not in abandoned:
                        explored_max = (depthmap.argmax(), int(angle_degrees))
                        graph_nodes[node] = [(position_update(node, int(angle_degrees)), 0)]
                not_explored -= 1

            elif not_explored > 0:
                graph_nodes[node].append((position_update(node, int(angle_degrees)), 0))
                action[0] = 0
                action[2] = 90
                not_explored -= 1
                if explored_max[0] > depthmap.argmax() and position_update(node, int(angle_degrees)) not in abandoned:
                    explored_max = (depthmap.argmax(), int(angle_degrees))
                game.make_action(action)

            else:
                current = current_positon
                target_angle = explored_max[1]
                if depthmap.argmax() == 0 or position_update(position_update(node, int(angle_degrees)), int(angle_degrees)) in abandoned:
                    explored_max = (255, 360)
                    not_explored = 4
                    abandoned.append(position_update(node, int(angle_degrees)))
                elif int(angle_degrees) < target_angle:
                    action[0] = 0
                    action[2] = -90
                    game.make_action(action)
                elif int(angle_degrees) > target_angle:
                    action[0] = 0
                    action[2] = 90
                    game.make_action(action)
                elif int(angle_degrees) == target_angle:
                    if get_distance_to_next(node[0], node[1], current[0], current[1]) < 20:
                        action[0] = 10
                        action[2] = 0
                        game.make_action(action)
                    else:
                        not_explored = 4



            '''if max > 10:
                current = (x_position, y_position)
                for i in graph_nodes:
                    if get_distance_to_next(i[0], i[1], current[0], current[1]) < 18 and i != parent:
                        action[0] = 0
                        action[2] = 1
                        game.make_action(action)
                        break
                else:
                    if get_distance_to_next(node[0], node[1], current[0], current[1]) < 20:
                        if direction[1] * 2 > depthmap.shape[1] + 30:
                            print("Right")
                            action[0] = 5
                            action[2] = 1
                            game.make_action(action)
                        elif direction[1] * 2 < depthmap.shape[1] - 30:
                            print("Left")
                            action[0] = 5
                            action[2] = -1
                            game.make_action(action)
                        else:
                            print("Straight")
                            action[0] = 10
                            action[2] = 0
                            game.make_action(action)

                    elif get_distance_to_next(node[0], node[1], current[0], current[1]) > 20:
                        flag = 1
                        count = 50'''



            print("State #" + str(state.number))
            print(state.game_variables)
            print("=====================")

    cv2.destroyAllWindows()