import json, os, threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label

# File to store friends data
DATA_FILE = 'friends.json'

def load_friends():
    """Load friends list from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print("File load mein truti:", e)  # Error loading file
    return []

def save_friends(friends):
    """Save friends list to JSON file using a separate thread"""
    def save():
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(friends, f, indent=4)
        except Exception as e:
            print("File save mein truti:", e)  # Error saving file
    
    # Use thread to prevent UI freezing during save operation
    threading.Thread(target=save).start()

# Kivy UI definition in KV language
KV = '''
<FriendManagerKivy>:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    
    # Search section
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: '120dp'
        Label:
            text: "Mitra Khoj:"  # Friend Search
            size_hint_y: None
            height: '30dp'
        TextInput:
            id: search_input
            multiline: False
            on_text: root.update_filter(self.text)  # Filter list on text change
    
    # Friends list section
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: "Mitra Suchi:"  # Friends List
            size_hint_y: None
            height: '30dp'
        RecycleView:
            id: rv
            viewclass: 'Label'
            RecycleBoxLayout:
                default_size: None, dp(30)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
    
    # Add new friend section
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: '120dp'
        Label:
            text: "Naya Mitra Jodne:"  # Add New Friend
            size_hint_y: None
            height: '30dp'
        TextInput:
            id: add_input
            multiline: False
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            Button:
                text: "Mitra Jodo"  # Add Friend
                on_press: root.add_mitra(add_input.text); add_input.text = ""
            Button:
                text: "Mitra Hatao"  # Remove Friend
                on_press: root.remove_mitra()
'''

class FriendManagerKivy(BoxLayout):
    """Main application class for Friend Manager"""
    friends_list = ListProperty([])  # List property for data binding
    filtered_friends = ListProperty([])  # Filtered list for display
    
    def __init__(self, **kwargs):
        """Initialize the application"""
        super(FriendManagerKivy, self).__init__(**kwargs)
        
        # Load existing friends
        self.friends_list = load_friends()
        self.filtered_friends = self.friends_list.copy()
        
        # Schedule UI update after initialization
        self.refresh_view()
    
    def refresh_view(self):
        """Update the RecycleView with current filtered friends"""
        self.ids.rv.data = [{'text': friend} for friend in self.filtered_friends]
    
    def update_filter(self, query):
        """Filter friends list based on search query"""
        query = query.strip().lower()
        if query:
            self.filtered_friends = [friend for friend in self.friends_list 
                                    if query in friend.lower()]
        else:
            self.filtered_friends = self.friends_list.copy()
        
        self.refresh_view()
    
    def add_mitra(self, name):
        """Add a new friend to the list"""
        name = name.strip()
        if not name:
            # Show error for empty name
            self.show_error("Mitra naam khaali nahin ho sakta!")  # Friend name can't be empty
            return
        
        if name in self.friends_list:
            # Show error for duplicate friend
            self.show_error("Mitra pahle se maujood hai!")  # Friend already exists
            return
        
        # Add friend, save to file and update UI
        self.friends_list.append(name)
        save_friends(self.friends_list)
        self.update_filter(self.ids.search_input.text)
    
    def remove_mitra(self):
        """Remove selected friend from the list"""
        # Get selected index from RecycleView
        layout = self.ids.rv.layout_manager
        selected_index = layout.selected_nodes[0] if layout.selected_nodes else None
        
        if selected_index is not None:
            # Remove friend, save to file and update UI
            friend = self.filtered_friends[selected_index]
            self.friends_list.remove(friend)
            save_friends(self.friends_list)
            self.update_filter(self.ids.search_input.text)
        else:
            # Show error when no friend is selected
            self.show_error("Koi mitra chayan nahin hua hai!")  # No friend selected
    
    def show_error(self, message):
        """Display error message in a popup"""
        popup = Popup(title='Error', 
                     content=Label(text=message),
                     size_hint=(None, None), size=(300, 150))
        popup.open()

class MitraPrabandhakApp(App):
    """Main application class"""
    def build(self):
        """Build and return the root widget"""
        # Load the Kivy string
        Builder.load_string(KV)
        return FriendManagerKivy()

if __name__ == '__main__':
    MitraPrabandhakApp().run()