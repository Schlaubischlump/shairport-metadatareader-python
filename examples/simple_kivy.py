from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from shairportmetadatareader import AirplayListener, DEFAULT_SOCKET

Builder.load_string("""

#:import AirplayCommand shairportmetadatareader.AirplayCommand

<RootLayout>:
    artist: "artist"
    title: "title"
    album: "album"
    artwork: "artwork"#"http://tracks.arte.tv/sites/default/files/styles/jscrop_1007x566/public/rickastley_2.jpg?itok=0CxpqgPL"

    orientation: 'vertical'

    BoxLayout:
        size_hint_y: 0.8
        orientation: 'horizontal'
        
        AsyncImage:
            source: root.artwork
        
        BoxLayout:
            orientation: 'vertical'
            
            Label:
                text: root.title
            Label:
                text: root.artist
            Label:
                text: root.album               

    BoxLayout:
        size_hint_y: 0.2
        orientation: 'horizontal'
    
        Button:
            text: 'Play'
            disabled: root.remote is None
            on_press: root.remote.send_command(AirplayCommand.PLAY)
        Button:
            text: 'Pause'
            disabled: root.remote is None
            on_press: root.remote.send_command(AirplayCommand.PAUSE)
        Button:
            text: 'Stop'
            disabled: root.remote is None
            on_press: root.remote.send_command(AirplayCommand.STOP)
        Button:
            text: '<<'
            disabled: root.remote is None
            on_press: root.remote.send_command(AirplayCommand.PREVIOUS_SONG)
        Button:
            text: '>>'
            disabled: root.remote is None
            on_press: root.remote.send_command(AirplayCommand.NEXT_SONG)
""")


class RootLayout(BoxLayout):
    # metadata information
    title = StringProperty("")
    artist = StringProperty("")
    album = StringProperty("")
    artwork = StringProperty("")

    # remote to control airplay playback
    remote = ObjectProperty(None, allownone=True)

    def on_track_info(self, listener, info):
        self.title = info["itemname"] if "itemname" in info else "title"
        self.album = info["songalbum"] if "songalbum" in info else "album"
        self.artist = info["songartist"] if "songartist" in info else "artist"

    def on_artwork(self, listener, artwork):
        self.artwork = artwork

    def on_has_remote(self, listener, has_remote):
        if has_remote:
            self.remote = listener.get_remote(timeout=5)
        else:
            self.remote = None


class MusicPlayer(App):
    listener = ObjectProperty(None)

    def build(self):
        self.root = RootLayout()

        # listen for airplay events
        self.listener = AirplayListener()
        self.listener.bind(track_info=self.root.on_track_info,
                           artwork=self.root.on_artwork,
                           has_remote_data=self.root.on_has_remote)
        self.listener.start_listening(socket_addr=DEFAULT_SOCKET)

        return self.root


if __name__ == '__main__':
    MusicPlayer().run()