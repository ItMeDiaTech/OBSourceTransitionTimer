import itertools
from weakref import WeakValueDictionary
import simpleobsws
import asyncio
import os
import logging
logging.basicConfig(level=logging.INFO)

# change password to password in OBS Websocket settings
password = 'password'

# change port to port in OBS Websocket settings
url = 'ws://127.0.0.1:4455'

# Get the file path of the current working directory (cwd).
# This is the directory of where this file is ran, so this python script must be placed
#   in the same folder as the all_transitions.txt file
file_path = os.getcwd()

# create websocket client
ws = simpleobsws.WebSocketClient(url=url, password=password)


class transition:
    # this is currently unused, but it saves all transition objects created
    _timerinstances = WeakValueDictionary()
    _targetitem = WeakValueDictionary()

    # when initiated, save name, the scene name, the delay transition, and the repeat delay from the file
    def __init__(self, *args):
        self._timerinstances[args[0]] = self
        self.name = str(args[0])
        self.scene_name = str(args[1])
        self.delay_transition = int(args[2])
        self.repeat_delay = int(args[3])
        
    # unused, but will return the timer objects by item name
    @classmethod
    def get_timer(cls, name):
        return cls._instances.get(name, None)

    # if mode is show, then sleep for the delay_transition time and then do the show transition
    async def run_timer_show(self):
        await asyncio.sleep(self.delay_transition/1000)
        self.do_timer_show()

    # if mode is hide, then sleep for the delay_transition time and then do the hide transition
    async def run_timer_hide(self):
        await asyncio.sleep(self.delay_transition/1000)
        await self.do_timer_hide()

    # if mode is repeat, then sleep for the delay_transition time and then do the transition for either show or hide
    async def run_timer_repeat(self):
        print(self.scene_name)
        await asyncio.sleep(self.delay_transition/1000)
        await self.do_repeat()

    # this function isn't needed for the show mode, but added to match setup of repeat timer
    async def do_timer_show(self):
        await self.set_visible()

    # this function isn't needed for the hide mode, but added to match setup of repeat timer
    async def do_timer_hide(self):
        await self.set_not_visible()

    async def do_repeat(self):
        await self.toggle_visible()

    # below functions set the visibility of the scene item depending on what we want
    async def set_visible(self):
        set_visible_request = simpleobsws.Request('SetSceneItemEnabled', {
            'sceneName': self.scene_name, 'sceneItemId': await self.get_id(), 'sceneItemEnabled': True})
        set_visible_return = await ws.call(set_visible_request)
        if set_visible_return.ok():
            print('Successfully changed visibility of sceneitem ' +
                  self.name + ' to True')
        else:
            print('set_not_visible was not sucessful')
        return True

    async def set_not_visible(self):
        set_not_visible_request = simpleobsws.Request('SetSceneItemEnabled', {
            'sceneName': self.scene_name, 'sceneItemId': await self.get_id(), 'sceneItemEnabled': False})
        set_not_visible_return = await ws.call(set_not_visible_request)
        if set_not_visible_return.ok():
            print('Successfully changed visibility of sceneitem ' +
                  self.name + ' to False')
        else:
            print('set_not_visible was not sucessful')
        return True

    async def toggle_visible(self):
        set_toggle_request = simpleobsws.Request('SetSceneItemEnabled', {
            'sceneName': self.scene_name, 'sceneItemId': await self.get_id() , 'sceneItemEnabled': not await self.is_visible()})
        set_toggle_return = await ws.call(set_toggle_request)
        if set_toggle_return.ok():
            print('Successfully toggled visibility of sceneitem ' +
                  self.name)
            await asyncio.create_task(asyncio.sleep(self.repeat_delay/1000))
            await self.do_repeat()
        else:
            print('set_not_visible was not sucessful')
        return True

    async def is_visible(self):
        
        is_visible_request = simpleobsws.Request(
            'GetSceneItemEnabled', {'sceneName': str(self.scene_name), 'sceneItemId': await self.get_id()})
        is_visible_return = await ws.call(is_visible_request)
        if is_visible_return.ok():
            print(is_visible_return.responseData)
            return is_visible_return.responseData['sceneItemEnabled']
        else:
            print(is_visible_return.responseData)
            return None

    async def get_id(self):
        sceneitem_id_request = simpleobsws.Request(
            'GetSceneItemId', {'sceneName': self.scene_name, 'sourceName': self.name})
        sceneitem_id_return = await ws.call(sceneitem_id_request)
        if sceneitem_id_return.ok():
            self.id = sceneitem_id_return.responseData['sceneItemId']
            return self.id
        else:
            return None
# was having difficulty with asyncio and running multiple timers, so just split this into its own function
async def read_file():
    with open(file_path + '/all_transitions.txt', 'r') as f:
        return f.readlines()

# main function, connects and gets all needed things
async def main():
    loop = asyncio.get_running_loop()
    await ws.connect()
    await ws.wait_until_identified()
    logging.info('Connected and identified')

    dict_scenes = None
    all_scenes_request = simpleobsws.Request('GetSceneList')
    ret = await ws.call(all_scenes_request)
    if ret.ok():
        dict_scenes = ret.responseData
    else:
        print('not ok')
    print(dict_scenes)

    with open(file_path + '/all_transitions.txt', 'r') as f:
        results = []
        target_item = None
        for line in itertools.zip_longest(*[f]*1):
            item_name = str(line).split(',')[0].split('\'')[1]
            mode = str(line).split(',')[10]
            delay_transition = int(str(line).split(',')[12])
            repeat_delay = int(str(line).split(',')[13])
            results.append(start(item_name, mode, delay_transition, repeat_delay, dict_scenes))

        # waiting till the loop is complete 
        await asyncio.gather(*results)



# now starting the timers for everything
async def start(item_name, mode, delay_transition, repeat_delay, dict_scenes):
    print(item_name)
    results = []
    if item_name is not type(None):
        for scene in dict_scenes['scenes']:
            print(scene['sceneName'])
            all_items_request = simpleobsws.Request('GetSceneItemList', scene)
            all_items_return = await ws.call(all_items_request)
            item_list = all_items_return.responseData
            for item in item_list['sceneItems']:
                print(item['sourceName'])
                if str(item['sourceName']) in item_name:
                    target_name = str(item['sourceName'])
                
                    if 'show' in mode:
                        print('Running timer show for item ' + target_name)
                        timer = transition(item_name,
                                        scene['sceneName'], delay_transition, repeat_delay)
                        return timer.run_timer_show()
                    if 'hide' in mode:
                        timer = transition(item_name,
                                           scene['sceneName'], delay_transition, repeat_delay)
                        print('Running timer hide for item ' + target_name)
                        return timer.run_timer_hide()
                    elif 'repeat' in mode:
                        timer = transition(item_name,
                                           scene['sceneName'], delay_transition, repeat_delay)
                        print('Running timer repeat for item ' + target_name)
                        return await timer.run_timer_repeat()
                    else:
                        print('Error, no mode')

# starts the script
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
