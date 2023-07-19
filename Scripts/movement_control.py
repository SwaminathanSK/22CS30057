#!/usr/bin/env python3
import os
from time import sleep
from vizdoom import DoomGame
from vizdoom import GameVariable
import vizdoom as vzd
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
            return False
    except AttributeError:
        pass

def achieved(agent_x, agent_y, target_x, target_y):
    if get_distance_to_next(agent_x, agent_y, target_x, target_y) < 20:
        return True
    return False


def get_angle_from_agent(agent_angle_degrees, agent_x, agent_y, target_x, target_y):
    delta_x = target_x - agent_x
    delta_y = target_y - agent_y

    target_angle_radians = math.atan2(delta_y, delta_x)
    target_angle_degrees = math.degrees(target_angle_radians)

    relative_angle_degrees = target_angle_degrees - agent_angle_degrees

    while relative_angle_degrees <= -180:
        relative_angle_degrees += 360
    while relative_angle_degrees > 180:
        relative_angle_degrees -= 360

    return relative_angle_degrees

def get_distance_to_next(agent_x, agent_y, target_x, target_y):
    delta_x = target_x - agent_x
    delta_y = target_y - agent_y

    return (delta_x**2 + delta_y**2)**0.5



if __name__ == "__main__":

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    game = vzd.DoomGame()
    game.set_doom_scenario_path(
        os.path.join(os.path.expanduser('~'), "Documents", "AGVSoftware", "AGVSoftwareTask", "WADFiles", "MAP01.wad"))

    # Sets resolution. Default is 320X240
    game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)

    # Sets the screen buffer format. Not used here but now you can change it. Default is CRCGCB.
    game.set_screen_format(vzd.ScreenFormat.RGB24)

    # Enables depth buffer (turned off by default).
    game.set_depth_buffer_enabled(True)

    # Enables labeling of in-game objects labeling (turned off by default).
    game.set_labels_buffer_enabled(True)

    # Enables buffer with a top-down map of the current episode/level (turned off by default).
    game.set_automap_buffer_enabled(True)

    # Enables information about all objects present in the current episode/level (turned off by default).
    game.set_objects_info_enabled(True)

    # Enables information about all sectors (map layout/geometry, turned off by default).
    game.set_sectors_info_enabled(True)

    # Sets other rendering options (all of these options except crosshair are enabled (set to True) by default)
    game.set_render_hud(False)
    game.set_render_minimal_hud(False)  # If hud is enabled
    game.set_render_crosshair(False)
    game.set_render_weapon(True)
    game.set_render_decals(False)  # Bullet holes and blood on the walls
    game.set_render_particles(False)
    game.set_render_effects_sprites(False)  # Like smoke and blood
    game.set_render_messages(False)  # In-game text messages
    game.set_render_corpses(False)
    game.set_render_screen_flashes(
        True
    )  # Effect upon taking damage or picking up items

    # Adds delta buttons that will be allowed and set the maximum allowed value (optional).
    game.add_available_button(vzd.Button.MOVE_FORWARD_BACKWARD_DELTA, 10)
    game.add_available_button(vzd.Button.MOVE_LEFT_RIGHT_DELTA, 5)
    game.add_available_button(vzd.Button.TURN_LEFT_RIGHT_DELTA, 5)
    game.add_available_button(vzd.Button.LOOK_UP_DOWN_DELTA)

    # Add game variables to the game before starting the episode
    game.add_available_game_variable(GameVariable.POSITION_X)
    game.add_available_game_variable(GameVariable.POSITION_Y)
    game.add_available_game_variable(GameVariable.ANGLE)
    game.add_available_game_variable(GameVariable.POSITION_Z)

    game.set_episode_timeout(9999999)

    # For normal buttons (binary) all values other than 0 are interpreted as pushed.
    # For delta buttons values determine a precision/speed.
    #
    # For TURN_LEFT_RIGHT_DELTA and LOOK_UP_DOWN_DELTA value is the angle (in degrees)
    # of which the viewing angle will change.
    #
    # For MOVE_FORWARD_BACKWARD_DELTA, MOVE_LEFT_RIGHT_DELTA, MOVE_UP_DOWN_DELTA (rarely used)
    # value is the speed of movement in a given direction (100 is close to the maximum speed).
    action = [0, 0, 0, 0]  # floating point values can be used

    path = [(385, 177), (384, 177), (382, 175), (382, 170), (385, 170), (386, 171), (412, 170), (414, 172), (419, 177), (446, 170), (449, 177), (450, 178), (452, 213)]


    path = path[::-1]

    # If button's absolute value > max button's value then value = max value with original value sign.

    # Delta buttons in spectator modes correspond to mouse movements.
    # Maximum allowed values also apply to spectator modes.
    # game.add_game_args("+freelook 1")    # Use this to enable looking around with the mouse.
    # game.set_mode(Mode.SPECTATOR)
    game.add_game_args("+am_backcolor ff0000 +am_gridcolor  ffffff +am_fdwallcolor ffffff +am_efwallcolor ffffff ")
    game.set_window_visible(True)

    game.init()
    pid_controller = PIDController()

    episodes = 10
    sleep_time = 0.028

    i = 3
    flag = 0
    target = (11*path[i][0] - 4939, -11*path[i][1] + 2279)

    while True:
        state = game.get_state()
        if not game.is_episode_finished():  # Check if the episode is still running
            map = state.automap_buffer
            x_position = state.game_variables[0]
            y_position = state.game_variables[1]
            angle_degrees = state.game_variables[2]

            factor = (976/87)

            print(x_position, y_position, angle_degrees)

            reward = game.make_action(action)

            angle_to_next = get_angle_from_agent(angle_degrees, x_position, y_position, target[0], target[1])
            distance_to_next = get_distance_to_next(x_position, y_position, target[0], target[1])

            if achieved(x_position, y_position, target[0], target[1]):
                i += 1
                if i == len(path):
                    flag = 1
                    game.close()
                    break
                target = (11 * path[i][0] - 4939, -11 * path[i][1] + 2279)

            time = game.get_episode_time()

            '''if angle_to_next > 10:
                action[2] = -3
            elif 5 < angle_to_next and angle_to_next < 10:
                action[2] = 0
                if distance_to_next > 20:
                    action[0] = 5
                else:
                    action[0] = 0
            elif -10 < angle_to_next and angle_to_next < 5:
                action[2] = 0
                if distance_to_next > 20:
                    action[0] = 5
                else:
                    action[0] = 0
            elif angle_to_next < -10:
                action[2] = 3'''

            action[2] = -pid_controller.update(abs(angle_to_next))
            if angle_to_next < -10 or angle_to_next > 10:
                action[0] = pid_controller.update(distance_to_next)


            '''if not time % 50:
                action[3] = -action[3]'''

            print("State #" + str(state.number))
            print("Action made: ", action)
            print("=====================")

            if sleep_time > 0:
                sleep(sleep_time)