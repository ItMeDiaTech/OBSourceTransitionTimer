import obspython as obs
from asyncio import *

# Script created by DiaTech
# This was just a project so I could get a better familiarity of obspython scripting
#   while also hopefully creating something that people will use. Therefore, the code
#   written below isn't supposed to be the best option. If there are any questions,
#   features you would like added, or if you see a way to better optimize the code,
#   don't hesitate to reach out!
#
# Discord: DiaTech#2363
# Github Link:
# OBS Forum Link:
# Email: mail@diatech.tv
# 
# Special thanks to everyone that helped me learn how to create this project.


def script_description():
  return """
   Allows user to pick a source to apply transitions
    -After 'Run'
        -If command 'Wipe Transitions' is chosen
            -It will wipe the contents of the transition file
            -There is no undoing this
        -If command 'Save Transition' is chosen
            -It will save the show/hide transitions chosen for the source
        -If a transition is already saved for source, it 
            will overwrite it.
    -Once you save the transitions you want timers for:
        -Edit the TransitionTimerWithWebsocket.py with any text editor
        -Change the value of the password / port you are using in OBS

    Support Forum: To be added
  """

# Properties for script
def script_properties():
    global props
    # create properties
    props = obs.obs_properties_create()

    # create field in script so user can select path to save file needed
    obs.obs_properties_add_path(props, 'path_selection', 'Path to folder to save settings: ', obs.OBS_PATH_DIRECTORY, None, None)

    # mode selection for source / scene item
    mode_properties = obs.obs_properties_add_list(
        props, 'mode_type', 'Mode: ', obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(mode_properties, 'None', 'None')
    obs.obs_property_list_add_string(
        mode_properties, 'Start with item visible', 'mode_show')
    obs.obs_property_list_add_string(
        mode_properties, 'Start with item hidden', 'mode_hide')
    obs.obs_property_list_add_string(
        mode_properties, 'Alternate visibility (repeat)', 'mode_repeat')

    # get all scene items / sources and put them in a list for user to select
    sceneitem_selection = obs.obs_properties_add_list(
        props, 'sceneitem_selection', 'Select Scene Item (source): ', obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    scene_list = obs.obs_frontend_get_scenes()

    obs.obs_property_list_add_string(sceneitem_selection, 'None', 'None')
    for scene in scene_list:
        scene_source = obs.obs_scene_from_source(scene)
        scene_items = obs.obs_scene_enum_items(scene_source)
        for item in scene_items:
            item_source = obs.obs_sceneitem_get_source(item)
            item_name = obs.obs_source_get_name(item_source)
            obs.obs_property_list_add_string(
                sceneitem_selection, item_name, item_name)

    # allow user to select which transition for the show animation
    sceneitem_transition_show_property = obs.obs_properties_add_list(
        props, 'transition_type_show', 'Transition type for showing: ', obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(
        sceneitem_transition_show_property, 'None', 'None')
    obs.obs_property_list_add_string(
        sceneitem_transition_show_property, 'Cut', 'Cut')
    obs.obs_property_list_add_string(
        sceneitem_transition_show_property, 'Fade', 'Fade')
    obs.obs_property_list_add_string(
        sceneitem_transition_show_property, 'Swipe', 'Swipe')
    obs.obs_property_list_add_string(
        sceneitem_transition_show_property, 'Slide', 'Slide')
    # Not added yet:
    # obs.obs_property_list_add_string(sceneitem_transition_show, 'Stinger', 'Stinger')
    # obs.obs_property_list_add_string(sceneitem_transition_show, 'Fade to Color', 'fade_to_color')

    # allow user to select which transition for the hide animation
    sceneitem_transition_hide_property = obs.obs_properties_add_list(
        props, 'transition_type_hide', 'Transition type for hiding: ', obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(
        sceneitem_transition_hide_property, 'None', 'None')
    obs.obs_property_list_add_string(
        sceneitem_transition_hide_property, 'Cut', 'Cut')
    obs.obs_property_list_add_string(
        sceneitem_transition_hide_property, 'Fade', 'Fade')
    obs.obs_property_list_add_string(
        sceneitem_transition_hide_property, 'Swipe', 'Swipe')
    obs.obs_property_list_add_string(
        sceneitem_transition_hide_property, 'Slide', 'Slide')

    # Not added yet:
    # obs.obs_property_list_add_string(sceneitem_transition_hide, 'Stinger', 'Stinger')
    # obs.obs_property_list_add_string(sceneitem_transition_hide, 'Fade to Color', 'fade_to_color')

    # add slider for visibility duration, aka transition duration
    obs.obs_properties_add_int_slider(props, 'visibility_duration', 'Duration of Transition', 1, 20, 1)

    # add slider for how long to delay initial timer
    obs.obs_properties_add_int_slider(props, 'delay_transition', 'Delay Timer Activation', 0, 60, 1)

    # for mode repeat, allow user to select how often to toggle the visibility / transition for a source
    obs.obs_properties_add_int_slider(props, 'repeat_delay', '(Mode: Repeat) Time between visibility change', 1, 300, 1)

    # if swipe mode is select for show / hide transition, will show the following settings for user to change
    swipe_direction_show_property = obs.obs_properties_add_list(
        props, 'swipe_direction_show', 'Direction of Swipe (Show Transition)', obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(
        swipe_direction_show_property, 'None', 'None')
    obs.obs_property_list_add_string(swipe_direction_show_property, 'Up', 'Up')
    obs.obs_property_list_add_string(
        swipe_direction_show_property, 'Down', 'Down')
    obs.obs_property_list_add_string(
        swipe_direction_show_property, 'Left', 'Left')
    obs.obs_property_list_add_string(
        swipe_direction_show_property, 'Right', 'Right')
    swipe_direction_hide_property = obs.obs_properties_add_list(
        props, 'swipe_direction_hide', 'Direction of Swipe (Hide Transition)', obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(
        swipe_direction_hide_property, 'None', 'None')
    obs.obs_property_list_add_string(swipe_direction_hide_property, 'Up', 'Up')
    obs.obs_property_list_add_string(
        swipe_direction_hide_property, 'Down', 'Down')
    obs.obs_property_list_add_string(
        swipe_direction_hide_property, 'Left', 'Left')
    obs.obs_property_list_add_string(
        swipe_direction_hide_property, 'Right', 'Right')

    # if slide mode is select for show / hide transition, will show the following settings for user to change
    slide_direction_show_property = obs.obs_properties_add_list(
        props, 'slide_direction_show', 'Direction of Slide (Show Transition)', obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(
        slide_direction_show_property, 'None', 'None')
    obs.obs_property_list_add_string(slide_direction_show_property, 'Up', 'Up')
    obs.obs_property_list_add_string(
        slide_direction_show_property, 'Down', 'Down')
    obs.obs_property_list_add_string(
        slide_direction_show_property, 'Left', 'Left')
    obs.obs_property_list_add_string(
        slide_direction_show_property, 'Right', 'Right')
    slide_direction_hide_property = obs.obs_properties_add_list(
        props, 'slide_direction_hide', 'Direction of Slide (Hide Transition)', obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(
        slide_direction_hide_property, 'None', 'None')
    obs.obs_property_list_add_string(slide_direction_hide_property, 'Up', 'Up')
    obs.obs_property_list_add_string(
        slide_direction_hide_property, 'Down', 'Down')
    obs.obs_property_list_add_string(
        slide_direction_hide_property, 'Left', 'Left')
    obs.obs_property_list_add_string(
        slide_direction_hide_property, 'Right', 'Right')

    # add buton for user to start the script
    start_timer_property = obs.obs_properties_add_list(
        props, 'start_saved_timers', 'Select command to execute', obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(start_timer_property, 'None', 'None')
    obs.obs_property_list_add_string(
        start_timer_property, 'Save Transition', 'only_save')
    obs.obs_property_list_add_string(
        start_timer_property, 'Wipe Saved Transitions', 'delete_all')

    obs.obs_properties_add_button(
        props, "apply_settings", "Run", apply_user_values)

    # set initial visibility of these items to false so they show up only when requirements are med
    #   requirements: slide / swipe settings needed, replay_delay needed

    set_visibility_show_transition(props)
    set_visibility_hide_transition(props)
    set_visibility_replay_delay(props)

    # set callback to properties that need to have visibility changed to the user based on mode selected
    obs.obs_property_set_modified_callback(
        sceneitem_transition_show_property, script_update)
    obs.obs_property_set_modified_callback(
        sceneitem_transition_hide_property, script_update)

    obs.obs_property_set_modified_callback(
        sceneitem_transition_show_property, set_visibility_show_transition)
    obs.obs_property_set_modified_callback(
        sceneitem_transition_hide_property, set_visibility_hide_transition)

    obs.obs_property_set_modified_callback(
        mode_properties, set_visibility_replay_delay)

    return props

# applies user selected values for transitions to sources
def apply_user_values(props, prop, *args, **kwargs):
    print('Applying all transition settings and saving to file')
    global mode_type
    global sceneitem_selection_name
    global transition_type_show
    global transition_type_hide
    global swipe_direction_show
    global swipe_direction_hide
    global slide_direction_show
    global slide_direction_hide
    global transition_id_show
    global transition_id_hide
    global start_saved_timers
    global file_path
    global visibility_duration
    global delay_transition
    global repeat_delay
    global start_saved_timers

    get_line = ""

    # if command selected is wipe, will just delete contents of file
    if 'Wipe' in start_saved_timers:
        with open(file_path + '/all_transitions.txt', 'w') as f:
            f.write('')

    # Otherwise add new transition to file.
    # The format / position of each variable are located below in this code, right above 'def apply_transitions()'
    else:
        if 'None' not in transition_id_show:
            print('Saving ' + transition_id_show +
                ' Transition to file for item ' + sceneitem_selection_name)
            get_line += str(sceneitem_selection_name)
            get_line += str(',' + str(transition_id_show))

            transition_name = str(sceneitem_selection_name +
                                ' ' + transition_type_show + ' Transition')
            get_line += str(',' + str(transition_name))

            if 'swipe_transition' in transition_id_show:
                if 'None' not in swipe_direction_show:
                    get_line += str(',' + str(swipe_direction_show).lower())
                else:
                    print(
                        'Error: swipe_direction_show was set to None - no direction selected')
                    print('Defaulting direction to \'up\'')
                    get_line += str(', p')
            else:
                get_line += (',None')

            if 'slide_transition' in transition_id_show:
                if 'None' not in slide_direction_show:
                    get_line += str(',' + str(slide_direction_show).lower())
                else:
                    print(
                        'Error: slide_direction_show was set to None - no direction selected')
                    print('Defaulting direction to \'up\'')
                    get_line += str(',up')
            else:
                get_line += str(',None')
        else:
            get_line += str('None,None,None')

        if 'None' not in transition_id_hide:
            print('Saving ' + transition_id_hide +
                ' Transition to file for item ' + sceneitem_selection_name)
            get_line += str(',' + str(sceneitem_selection_name))
            get_line += str(',' + str(transition_id_hide))

            transition_name = str(sceneitem_selection_name +
                                ' ' + transition_type_hide + ' Transition')
            get_line += str(',' + str(transition_name))

            if 'swipe_transition' in transition_id_hide:
                if 'None' not in swipe_direction_hide:
                    get_line += str(',' + str(swipe_direction_hide))
                else:
                    print(
                        'Error: swipe_direction_hide was set to None - no direction selected')
                    print('Defaulting direction to \'up\'')
                    get_line += str(',up')
            else:
                get_line += str(',None')

            if 'slide_transition' in transition_id_hide:
                if 'None' not in slide_direction_hide:
                    get_line += str(',' + slide_direction_hide)
                else:
                    print(
                        'Error: slide_direction_hide was set to None - no direction selected')
                    print('Defaulting direction to \'up\'')
                    get_line += str(',up')
            else:
                get_line += (',None')
        else:
            get_line += (',None,None,None')

        get_line += str(',' + str(mode_type))
        get_line += str(',' + str(visibility_duration))
        get_line += str(',' + str(delay_transition))
        get_line += str(',' + str(repeat_delay))
        get_line += str(',\n')

        new_string = ""
        # saving to file
        with open(file_path + '/all_transitions.txt', 'r') as writing_file:
            all_lines = writing_file.readlines()
            for line in all_lines:
                print(str(line).split(',')[0])
                print(str(get_line).split(',')[0])
                # if the name of the source selected is not in the line of the file, append transition to string variable
                if str(line).split(',')[0] != str(get_line).split(',')[0]:
                    new_string += str(line)
            # lastly, append selected transition to string variable knowing for sure there are no duplicates now
            new_string += str(get_line)

        # write the string variable to the text document, deleting all contents (since they have been added to string variable)
        with open(file_path + '/all_transitions.txt', 'w') as writing_file:
            writing_file.write(new_string)

        # these two following lines probably arne't needed, just being cautious by setting them to ''
        new_string = ""
        get_line = ""
        apply_transitions()


# taking all values in the all_transition.txt file and applying them
# File should be in the format of:
#   (0)item_name_show, (1)transition_id_show, (2)transition_name_show, (3)swipe_direction_show, (4)slide_direction_show,
#   (5)item_name_show, (6)transition_id_show, (7)transition_name, (8)swipe_direction_show, (9)slide_direction_show,
#   (10)mode_type, (11)visibility_duration, (12)delay_transition, (13)repeat_delay + \n
#       -This is in one consecutive line
def apply_transitions():
    global file_path

    print('Applying transition')

    # open file as read only
    # for line in file, call the change_base_settings function
    with open(file_path + '/all_transitions.txt', 'r') as f:

        for line in f.readlines():
            print(str(line))
            change_base_settings(props, line)

# change settings of sources in OBS 
def change_base_settings(props, line):
    # match name in file to scene item name in OBS
    scenes = obs.obs_frontend_get_scenes()
    for scene in scenes:
        items = obs.obs_scene_enum_items(obs.obs_scene_from_source(scene))
        for item in items:
            print(str(line).split(',')[0])
            item_source = obs.obs_sceneitem_get_source(item)
            item_name = obs.obs_source_get_name(item_source)
            file_item_name = str(line).split(',')[0]
            print(file_item_name)

            # if name in file matches the scene item name in OBS, assign values to variables
            if item_name in file_item_name:
                file_transition_id_show = str(line).split(',')[1]
                file_transition_name_show = str(line).split(',')[2]
                file_swipe_direction_show = str(line).split(',')[3]
                file_slide_direction_show = str(line).split(',')[4]
                file_item_name_hide = str(line).split(',')[5]
                file_transition_id_hide = str(line).split(',')[6]
                file_transition_name_hide = str(line).split(',')[7]
                file_swipe_direction_hide = str(line).split(',')[8]
                file_slide_direction_hide = str(line).split(',')[9]
                file_mode = str(line).split(',')[10]
                file_visibility_duration = int(str(line).split(',')[11])
                file_delay_transition = int(str(line).split(',')[12])
                file_repeat_delay = int(str(line).split(',')[13])

                # if user selected a show transition, do stuff
                if 'None' not in file_transition_id_show:
                    print('None not in transition_id_show')

                    # check to make sure item found is valid just in case
                    if not item:
                        print('Error: target_item is not an item')
                    else:
                        print('Looks like something is in target_item')

                    # create show transition settings
                    settings_show_transition = obs.obs_data_create()

                    # apply transition id to settings_show_transition
                    obs.obs_data_set_string(settings_show_transition, 'id', file_transition_id_show)

                    # apply duration of the transition to settings_show_transition
                    obs.obs_data_set_int(settings_show_transition, 'duration', file_visibility_duration)

                    # if the transition is either a swipe or slide, add those settings too
                    if 'None' not in file_swipe_direction_show:
                        obs.obs_data_set_string(
                            settings_show_transition, 'direction', file_swipe_direction_show)

                    if 'None' not in file_slide_direction_show:
                        obs.obs_data_set_string(
                            settings_show_transition, 'direction', file_slide_direction_show)

                    # create private source for the transition to be added to scene item
                    # this must be private to work
                    transition_source_show = obs.obs_source_create_private(
                        file_transition_id_show, file_transition_name_show, settings_show_transition)
                    
                    # force update the transition source to make sure settings we applied are saved
                    obs.obs_source_update(
                        transition_source_show, settings_show_transition)

                    # If the mode selected for this scene item was show, then the visibility of scene item should be false.
                    # To make sure the transition animation doesn't play when making sure visibility is off for the source, we are also
                    # going to set the hide animation to None so that it clears any previously set values.
                    if 'mode_show' in file_mode:
                        obs.obs_sceneitem_set_hide_transition(item, None)
                        obs.obs_sceneitem_set_visible(item, False)
                    
                    # Applying the show transition created to the scene item
                    obs.obs_sceneitem_set_show_transition(item, transition_source_show)
                    obs.obs_sceneitem_set_show_transition_duration(item, file_visibility_duration)

                # does all the things we did listed above for the show transition, but this time for the hide transition
                if 'None' not in file_transition_id_hide:
                    print('None not in transition_id_hide')
                    settings_hide_transition = obs.obs_data_create()
                    obs.obs_data_set_string(
                        settings_hide_transition, 'id', file_transition_id_hide)
                    obs.obs_data_set_int(
                        settings_hide_transition, 'duration', file_visibility_duration)

                    if 'None' not in file_swipe_direction_hide:
                        obs.obs_data_set_string(
                            settings_hide_transition, 'direction', file_swipe_direction_hide)

                    if 'None' not in file_slide_direction_hide:
                        obs.obs_data_set_string(
                            settings_hide_transition, 'direction', file_slide_direction_hide)

                    transition_source_hide = obs.obs_source_create_private(
                        file_transition_id_hide, file_transition_name_hide, settings_hide_transition)

                    if 'mode_hide' in file_mode:
                        obs.obs_sceneitem_set_show_transition(
                            item, None)
                        obs.obs_sceneitem_set_visible(
                            item, True)
                    obs.obs_sceneitem_set_hide_transition(
                        item, transition_source_hide)
                    obs.obs_sceneitem_set_hide_transition_duration(
                        item, file_visibility_duration)
                

    print('Transition settings applied and saved to file')
    return True

# sets the visibility of the swipe / slide show transition settings the user sees in the script settings in OBS
def set_visibility_show_transition(props, *args, **kwargs):
    print('Changing visibility of properties for show transition')
    global transition_id_show

    swipe_direction_show_properties = obs.obs_properties_get(
        props, 'swipe_direction_show')
    slide_direction_show_properites = obs.obs_properties_get(
        props, 'slide_direction_show')
    if 'None' in transition_type_show:
        print('No show transition type selected')
        obs.obs_property_set_visible(swipe_direction_show_properties, False)
        obs.obs_property_set_visible(slide_direction_show_properites, False)
        transition_id_show = 'None'
        return True
    elif 'Cut' in transition_type_show:
        print('Cut transition type for show selected')
        obs.obs_property_set_visible(swipe_direction_show_properties, False)
        obs.obs_property_set_visible(slide_direction_show_properites, False)
        transition_id_show = 'cut_transition'
        return True
    elif 'Fade' in transition_type_show:
        print('Fade transition type for show selected')
        obs.obs_property_set_visible(swipe_direction_show_properties, False)
        obs.obs_property_set_visible(slide_direction_show_properites, False)
        transition_id_show = 'fade_transition'
        return True
    elif 'Swipe' in transition_type_show:
        print('Swipe transition type for show selected')
        obs.obs_property_set_visible(swipe_direction_show_properties, True)
        obs.obs_property_set_visible(slide_direction_show_properites, False)
        transition_id_show = 'swipe_transition'
        return True
    elif 'Slide' in transition_type_show:
        print('Slide transition type for show selected')
        obs.obs_property_set_visible(swipe_direction_show_properties, False)
        obs.obs_property_set_visible(slide_direction_show_properites, True)
        transition_id_show = 'slide_transition'
        return True
    else:
        print('Somethin\' weird happened, definitely an error')
    return True

# sets the visibility of the swipe / slide hide transition settings the user sees in the script settings in OBS
def set_visibility_hide_transition(props, *args, **kwargs):
    print('Changing visibility of properties for hide transition')
    global transition_id_hide

    swipe_direction_hide_properties = obs.obs_properties_get(
        props, 'swipe_direction_hide')
    slide_direction_hide_properites = obs.obs_properties_get(
        props, 'slide_direction_hide')
    if 'None' in transition_type_hide:
        print('No hide transition type selected')
        obs.obs_property_set_visible(swipe_direction_hide_properties, False)
        obs.obs_property_set_visible(slide_direction_hide_properites, False)
        transition_id_hide = 'None'
        return True
    elif 'Cut' in transition_type_hide:
        print('Cut transition type for hide selected')
        obs.obs_property_set_visible(swipe_direction_hide_properties, False)
        obs.obs_property_set_visible(slide_direction_hide_properites, False)
        transition_id_hide = 'cut_transition'
        return True
    elif 'Fade' in transition_type_hide:
        print('Fade transition type for hide selected')
        obs.obs_property_set_visible(swipe_direction_hide_properties, False)
        obs.obs_property_set_visible(slide_direction_hide_properites, False)
        transition_id_hide = 'fade_transition'
        return True
    elif 'Swipe' in transition_type_hide:
        print('Fade transition type for hide selected')
        obs.obs_property_set_visible(swipe_direction_hide_properties, True)
        obs.obs_property_set_visible(slide_direction_hide_properites, False)
        transition_id_hide = 'swipe_transition'
        return True
    elif 'Slide' in transition_type_hide:
        print('Slide transition type for hide selected')
        obs.obs_property_set_visible(swipe_direction_hide_properties, False)
        obs.obs_property_set_visible(slide_direction_hide_properites, True)
        transition_id_hide = 'slide_transition'
        return True
    else:
        print('Somethin\' weird happened, definitely an error')
    # must return True to change visibility of property
    return True

# if mode is replay delay, shows the user additional settings in OBS script's settings
def set_visibility_replay_delay(props, *args, **kwargs):
    print('Changing visibility of replay_delay')

    repeat_delay_property = obs.obs_properties_get(props, 'repeat_delay')
    mode = obs.obs_data_get_string(my_settings, 'mode_type')

    if 'repeat' in mode:
        obs.obs_property_set_visible(repeat_delay_property, True)
        print('true')
    else:
        obs.obs_property_set_visible(repeat_delay_property, False)
        print('false')
    # must return True to change visibility of property
    return True

# when script is updated, create global variables to be used, update those variables
def script_update(settings):
    global mode_type
    global sceneitem_selection_name
    global transition_type_show
    global transition_type_hide
    global swipe_direction_show
    global swipe_direction_hide
    global slide_direction_show
    global slide_direction_hide
    global start_saved_timers
    global my_settings
    global file_path
    global visibility_duration
    global delay_transition
    global repeat_delay
    global props

    file_path = obs.obs_data_get_string(settings, 'path_selection')

    my_settings = settings

    start_saved_timers = obs.obs_data_get_string(
        settings, 'start_saved_timers')
    swipe_direction_show = obs.obs_data_get_string(
        settings, 'swipe_direction_show')
    swipe_direction_hide = obs.obs_data_get_string(
        settings, 'swipe_direction_hide')
    slide_direction_show = obs.obs_data_get_string(
        settings, 'slide_direction_show')
    slide_direction_hide = obs.obs_data_get_string(
        settings, 'slide_direction_hide')

    transition_type_show = obs.obs_data_get_string(
        settings, 'transition_type_show')
    transition_type_hide = obs.obs_data_get_string(
        settings, 'transition_type_hide')

    mode_type = obs.obs_data_get_string(settings, 'mode_type')
    sceneitem_selection_name = obs.obs_data_get_string(
        settings, 'sceneitem_selection')

    # all values that are seconds need to be multipled by 1,000 since it has to be in ms
    visibility_duration = int(obs.obs_data_get_int(
        settings, 'visibility_duration')*1000)
    delay_transition = int(obs.obs_data_get_int(
        settings, 'delay_transition')*1000)
    repeat_delay = int(obs.obs_data_get_int(settings, 'repeat_delay')*1000)
