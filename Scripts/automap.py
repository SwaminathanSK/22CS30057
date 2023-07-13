from argparse import ArgumentParser
from random import choice
import os
import cv2

import vizdoom as vzd

if __name__ == "__main__":
	
	
    # Create DoomGame instance. It will run the game and communicate with you.
    game = vzd.DoomGame()

    # Now it's time for configuration!
    # load_config could be used to load configuration instead of doing it here with code.
    # If load_config is used in-code configuration will also work - most recent changes will add to previous ones.
    # game.load_config("../../scenarios/basic.cfg")

    # Sets path to additional resources wad file which is basically your scenario wad.
    # If not specified default maps will be used and it's pretty much useless... unless you want to play good old Doom.
    game.set_doom_scenario_path(os.path.join(os.path.expanduser('~'), "Documents", "AGVSoftware", "AGVSoftwareTask", "WADFiles", "MAP01.wad"))

    # Sets map to start (scenario .wad files can contain many maps).
    # game.set_doom_map("map01")

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

    # Adds buttons that will be allowed to use.
    # This can be done by adding buttons one by one:
    # game.clear_available_buttons()
    # game.add_available_button(vzd.Button.MOVE_LEFT)
    # game.add_available_button(vzd.Button.MOVE_RIGHT)
    # game.add_available_button(vzd.Button.ATTACK)
    # Or by setting them all at once:
    game.set_available_buttons(
        [vzd.Button.MOVE_LEFT, vzd.Button.MOVE_RIGHT, vzd.Button.ATTACK]
    )
    # Buttons that will be used can be also checked by:
    print("Available buttons:", [b.name for b in game.get_available_buttons()])

    # Adds game variables that will be included in state.
    # Similarly to buttons, they can be added one by one:
    # game.clear_available_game_variables()
    # game.add_available_game_variable(vzd.GameVariable.AMMO2)
    # Or:
    game.set_available_game_variables([vzd.GameVariable.AMMO2])
    print(
        "Available game variables:",
        [v.name for v in game.get_available_game_variables()],
    )

    # Causes episodes to finish after 200 tics (actions)
    game.set_episode_timeout(2000)

    # Makes episodes start after 10 tics (~after raising the weapon)
    game.set_episode_start_time(10)

    # Makes the window appear (turned on by default)
    game.set_window_visible(True)

    # Turns on the sound. (turned off by default)
    # game.set_sound_enabled(True)
    # Because of some problems with OpenAL on Ubuntu 20.04, we keep this line commented,
    # the sound is only useful for humans watching the game.

    # Turns on the audio buffer. (turned off by default)
    # If this is switched on, the audio will stop playing on device, even with game.set_sound_enabled(True)
    # Setting game.set_sound_enabled(True) is not required for audio buffer to work.
    # game.set_audio_buffer_enabled(True)

    # Sets the living reward (for each move) to -1
    game.set_living_reward(-1)

    # Set cv2 friendly format.
    game.set_screen_format(vzd.ScreenFormat.BGR24)

    # Enables rendering of automap.
    game.set_automap_buffer_enabled(True)

    # All map's geometry and objects will be displayed.
    game.set_automap_mode(vzd.AutomapMode.OBJECTS_WITH_SIZE)

    game.add_available_game_variable(vzd.GameVariable.POSITION_X)
    game.add_available_game_variable(vzd.GameVariable.POSITION_Y)
    game.add_available_game_variable(vzd.GameVariable.POSITION_Z)

    # Disables game window (FPP view), we just want to see the automap.
    game.set_window_visible(False)

    # This CVAR can be used to make a map follow a player.
    game.add_game_args("+am_followplayer 1")

    # This CVAR controls scale of rendered map (higher valuer means bigger zoom).
    game.add_game_args("+viz_am_scale 10")

    # This CVAR shows the whole map centered (overrides am_followplayer and viz_am_scale).
    game.add_game_args("+viz_am_center 1")

    # Map's colors can be changed using CVARs, full list is available here: https://zdoom.org/wiki/CVARs:Automap#am_backcolor
    game.add_game_args("+am_backcolor ff0000 +am_gridcolor  ffffff +am_fdwallcolor ffffff +am_efwallcolor ffffff ")
    # +am_yourcolor 00ff00
    game.init()

    seen_in_this_episode = set()
    game.new_episode()

    state = game.get_state()
    map = state.automap_buffer

    for i in range(map.shape[0]):
        for j in range(map.shape[1]):
            if (map[i][j] == (255, 0, 0)).all():
                continue
            elif (map[i][j] == (255, 255, 255)).all():
                continue
            elif (map[i][j] != (0, 0, 255)).any():
                map[i][j] = (0, 0, 0)
    if map is not None:
        cv2.imshow("ViZDoom Automap Buffer", map)
    cv2.waitKey(10000)
    cv2.imwrite("processed_map.png", map)
    cv2.destroyAllWindows()
