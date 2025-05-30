from kivy.app import App 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.image import AsyncImage
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.popup import Popup
import json

try:
    with open('books.json', 'r') as f:
        book_data = json.load(f)
except:
    from book_data import book_data

Window.size = (360, 640)
Window.clearcolor = (0.341, 0.561, 0.792, 1)

class RatingWidget(BoxLayout):
    def __init__(self, rating=0, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.rating = rating
        self.stars = []
        
        for i in range(1, 6):
            star = AsyncImage(
                source="https://cdn-icons-png.flaticon.com/512/1828/1828884.png" if i <= rating 
                       else "https://cdn-icons-png.flaticon.com/512/1828/1828970.png",
                size_hint=(None, None),
                size=(dp(30), dp(30)),
                allow_stretch=True
            )
            star.bind(on_touch_down=lambda _, touch, idx=i: self.update_rating(idx) 
                     if star.collide_point(*touch.pos) else False)
            self.stars.append(star)
            self.add_widget(star)
    
    def update_rating(self, rating):
        self.rating = rating
        for i, star in enumerate(self.stars, 1):
            star.source = ("https://cdn-icons-png.flaticon.com/512/1828/1828884.png" 
                          if i <= rating 
                          else "https://cdn-icons-png.flaticon.com/512/1828/1828970.png")

class BookCard(BoxLayout):
    def __init__(self, book, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(300)
        self.padding = dp(10)
        self.spacing = dp(10)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
        
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        img = AsyncImage(
            source=book['image'],
            size_hint_y=None,
            height=dp(150),
            allow_stretch=True
        )
        
        title = Label(
            text=book['title'],
            size_hint_y=None,
            height=dp(30),
            bold=True,
            color=(0, 0, 0, 1)
        )
        
        author = Label(
            text=f"by {book['author']}",
            size_hint_y=None,
            height=dp(25),
            color=(0.4, 0.4, 0.4, 1)
        )
        
        price = Label(
            text=book['price'],
            size_hint_y=None,
            height=dp(25),
            color=(0.153, 0.267, 0.365, 1)
        )
        
        rating_box = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(5))
        for i in range(1, 6):
            star = AsyncImage(
                source="https://cdn-icons-png.flaticon.com/512/1828/1828884.png" if i <= book.get('rating', 0) \
                       else "https://cdn-icons-png.flaticon.com/512/1828/1828970.png",
                size_hint=(None, None),
                size=(dp(24), dp(24)),
                allow_stretch=True
            )
            rating_box.add_widget(star)
        
        self.add_widget(img)
        self.add_widget(title)
        self.add_widget(author)
        self.add_widget(price)
        self.add_widget(rating_box)
    
    def _update_rect(self, instance, value):
        instance.rect.size = instance.size
        instance.rect.pos = instance.pos

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        with self.canvas.before:
            Color(0.341, 0.561, 0.792, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_rect)
        
        layout = AnchorLayout(anchor_x='center', anchor_y='center')
        content = BoxLayout(orientation='vertical', spacing=dp(20), size_hint=(0.8, None))
        content.bind(minimum_height=content.setter('height'))
        
        lbl_title = Label(
            text='Bookstore App',
            font_size=24,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        
        btn_books = Button(
            text='Available Books',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.153, 0.267, 0.365, 1),
            background_normal=''
        )
        btn_books.bind(on_press=self.go_to_books)
        
        content.add_widget(lbl_title)
        content.add_widget(btn_books)
        layout.add_widget(content)
        self.add_widget(layout)
    
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def go_to_books(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'category'
        self.manager.get_screen('category').show_books(book_data)

class CategoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.setup_ui()
    
    def setup_ui(self):
        search_box = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(5))
        self.search_input = TextInput(
            hint_text='Search by title or author...',
            multiline=False,
            size_hint_x=0.7
        )
        btn_search = Button(
            text='Search',
            size_hint_x=0.3,
            background_color=(0.153, 0.267, 0.365, 1)
        )
        btn_search.bind(on_press=self.search_books)
        
        search_box.add_widget(self.search_input)
        search_box.add_widget(btn_search)
        
        scroll = ScrollView()
        self.grid = GridLayout(cols=2, spacing=dp(15), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        
        btn_back = Button(
            text='Back to Menu',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.153, 0.267, 0.365, 1)
        )
        btn_back.bind(on_press=self.go_back)
        
        request_text = """
        [b]Can't find what you're looking for?[/b]
        Email us at [color=191970][ref=email]bookstore@example.com[/ref][/color]
        or visit our store in Calinan, Davao City
        """
        
        request_label = Label(
            text=request_text,
            size_hint_y=None,
            height=dp(80),
            markup=True,
            halign='center',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1)  
        )
        
        def show_click_effect(*args):
            request_label.color = (0.1, 0.1, 0.44, 1)  
            Clock.schedule_once(lambda dt: setattr(request_label, 'color', (0.2, 0.2, 0.2, 1)), 0.3)
        
        request_label.bind(on_ref_press=show_click_effect)
        
        self.layout.add_widget(search_box)
        self.layout.add_widget(scroll)
        self.layout.add_widget(btn_back)
        self.layout.add_widget(request_label)
        self.add_widget(self.layout)
    
    def search_books(self, instance):
        query = self.search_input.text.lower()
        if not query:
            self.show_books(book_data)
            return
        
        results = [
            book for book in book_data
            if query in book['title'].lower() or query in book['author'].lower()
        ]
        
        if not results: 
            self.show_not_found_popup()
        else:
            self.show_books(results)

    def show_not_found_popup(self):
        popup = Popup(
            title="No Results Found",
            content=Label(
                text="No matches found.\nKindly check spelling or\nrequest this book",  
                halign="center",
                line_height=1.2 
            ),
            size_hint=(0.7, 0.35), 
        )
        popup.open()

    def show_books(self, books):
        self.grid.clear_widgets()
        for book in books:
            card = BookCard(book)
            card.bind(on_touch_down=lambda x, y, b=book: self.show_details(b) if x.collide_point(*y.pos) else False)
            self.grid.add_widget(card)
    
    def show_details(self, book):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'details'
        self.manager.get_screen('details').show_book(book)
    
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

class DetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(20))
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        self.add_widget(self.scroll)
    
    def show_book(self, book):
        self.content.clear_widgets()
        
        img = AsyncImage(
            source=book['image'],
            size_hint_y=None,
            height=dp(250),
            allow_stretch=True
        )
        
        title = Label(
            text=book['title'],
            size_hint_y=None,
            height=dp(40),
            font_size=22,
            bold=True,
            halign='center'
        )
        
        author = Label(
            text=f"by {book['author']}",
            size_hint_y=None,
            height=dp(30),
            font_size=18,
            halign='center'
        )
        
        price_layout = BoxLayout(size_hint_y=None, height=dp(40))
        price = Label(
            text=book['price'],
            font_size=20,
            bold=True,
            color=(0.153, 0.267, 0.365, 1)
        )
        book_format = Label(
            text=book['format'],
            font_size=16,
            color=(0.4, 0.4, 0.4, 1)
        )
        price_layout.add_widget(price)
        price_layout.add_widget(book_format)
        
        rating = RatingWidget(rating=book.get('rating', 0), size_hint_y=None, height=dp(40))
        
        desc = Label(
            text=book['description'],
            size_hint_y=None,
            text_size=(Window.width - dp(40), None),
            halign='left',
            valign='top',
            padding=(0, 10)
        )
        desc.bind(texture_size=desc.setter('size'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50))
        btn_back = Button(
            text='Back',
            background_color=(0.153, 0.267, 0.365, 1)
        )
        btn_back.bind(on_press=self.go_back)
        btn_layout.add_widget(btn_back)
        
        self.content.add_widget(img)
        self.content.add_widget(title)
        self.content.add_widget(author)
        self.content.add_widget(price_layout)
        self.content.add_widget(rating)
        self.content.add_widget(desc)
        self.content.add_widget(btn_layout)
    
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'category'

class BookstoreApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main'))
        sm.add_widget(CategoryScreen(name='category'))
        sm.add_widget(DetailsScreen(name='details'))
        return sm

if __name__ == '__main__':
    BookstoreApp().run()
