import asyncio
import aiohttp
from kivy.app import App
from kivy.lang import Builder
import threading

kv = '''
FloatLayout:
    ScrollView:
        pos_hint: {'left': 1, 'top': 1}
        size_hint_y: .8
        do_scroll_x: False
        Label:
            id: debugarea
            size_hint: None, None
            size: self.texture_size
    Button:
        size_hint_y: .1
        text: 'start'
        on_release:
            app.do_print()
            self.text = 'stop' if app.is_printing else 'start'
'''

class MainApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_printing = False
        self.print_thread = None
        self.root_widget = Builder.load_string(kv)

    def build(self):
        return self.root_widget

    async def fetch(self, session, url, i):
        url = url.format(i)
        try:
            async with session.post(url, data='getprinterstatus') as response:
                json_response = await response.json(content_type=None)
                self.root_widget.ids['debugarea'].text += str(i) + "\n"
                self.root_widget.ids['debugarea'].text +="URL: "+ url[:url.find(':80/command')] + '/'+ '\n'


        except asyncio.TimeoutError:
            pass
        except aiohttp.ClientError:
            pass

    def func(self):
        asyncio.run(self.main())


    async def main(self):
        URL = "http://192.168.1.{}:80/command"
        timeout = aiohttp.ClientTimeout(total=1)
        async with aiohttp.ClientSession(timeout=timeout, headers={'Content-Type': 'text/plain'}) as session:
            tasks = [self.fetch(session, URL, i) for i in range(2, 250)]
            await asyncio.gather(*tasks)


    def do_print(self):
        if not self.is_printing:
            self.is_printing = True
            self.print_thread = threading.Thread(target=self.func)
            self.print_thread.start()
        else:
            self.is_printing = False
            self.print_thread.join()
            self.print_thread = None

MainApp().run()








