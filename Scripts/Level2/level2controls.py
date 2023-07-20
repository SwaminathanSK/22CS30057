from argparse import ArgumentParser
import os
from random import choice
import vizdoom as vzd
import numpy as np
import cv2
import math
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

# DEFAULT_CONFIG = os.path.join(vzd.scenarios_path, "deadly_corridor.cfg")
DEFAULT_CONFIG = "../../scenarios/level1.cfg"

import cv2

if __name__ == "__main__":

    """
    ############################################################################################################################################################
    These are pre-set configurations for level2 of the task, please dont change them

    ############################################################################################################################################################
    """

    parser = ArgumentParser("ViZDoom example showing different buffers (screen, depth, labels).")
    parser.add_argument(dest="config",
                        default=DEFAULT_CONFIG,
                        nargs="?",
                        help="Path to the configuration file of the scenario."
                             " Please see "
                             "../../scenarios/*cfg for more scenarios.")

    args = parser.parse_args()

    game = vzd.DoomGame()

    # Use other config file if you wish.
    game.load_config(args.config)

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

    # The buttons you can use to make actionns currently are:
    # MOVE_LEFT, MOVE_RIGHT, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT_RIGHT_DELTA
    # setting available buttons here:
    game.set_available_buttons(
        [vzd.Button.MOVE_LEFT, vzd.Button.MOVE_RIGHT, vzd.Button.MOVE_FORWARD, vzd.Button.MOVE_BACKWARD,
         vzd.Button.TURN_LEFT_RIGHT_DELTA])

    # check this link for all available buttons, use any you find useful: https://github.com/mwydmuch/ViZDoom/blob/master/doc/Types.md#button

    # The state variables which you get from the game currently are:
    # POSITION_X, POSITION_Y, ANGLE
    # setting available game variables here:
    game.set_available_game_variables(
        [vzd.GameVariable.POSITION_X, vzd.GameVariable.POSITION_Y, vzd.GameVariable.ANGLE])

    # check this link for all available game variables, use any you find useful: https://github.com/mwydmuch/ViZDoom/blob/master/doc/Types.md#gamevariable

    game.init()

    # action to the game is given through a list of values for each of the buttons available, given below are a list of possible actions you could give to the
    # game currently
    actions = [[True, False, True, False, 1], [False, True, False, True, 1], [False, True, True, False, -1],
               [True, False, False, True, -1]]

    episodes = 10
    sleep_time = 0.028

    for i in range(episodes):
        print("Episode #" + str(i + 1))

        # Not needed for the first episode but the loop is nicer.
        game.new_episode()

        # episode ends after you reach the key(end of game) or after a given time(300 seconds fixed in the config file)
        while not game.is_episode_finished():

            # Gets the state and possibly do something with it
            state = game.get_state()

            # Shows the depth map of the current episode/level.
            depthmap = state.depth_buffer
            if depthmap is not None:
                cv2.imshow('ViZDoom Depth Buffer', depthmap)

            # shows the segmented areas of any objects in the map
            labelsmap = state.labels_buffer
            if labelsmap is not None:
                cv2.imshow('ViZDoom Labels Buffer', labelsmap)

            cv2.waitKey(int(sleep_time * 1000))

            # currently choosing a random action from the list of actions below as a demo, remove this and input actions as required
            game.make_action(choice(actions))

            """
            ---------------------------------------------------------PUT YOUR CODE HERE------------------------------------------------------------------------

            """

            print("State #" + str(state.number))
            print(state.game_variables)
            print("=====================")

        print("Episode finished!")
        print("************************")

    cv2.destroyAllWindows()