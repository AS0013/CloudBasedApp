import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class HelloWorld(toga.App):
    
    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN))

        name_label = toga.Label(
            text="Your name: ",
            style=Pack(padding=(0, 5)),
        )
        self.name_input = toga.TextInput(style=Pack(flex=1))

        name_box = toga.Box(style=Pack(direction=ROW, padding=5))
        name_box.add(name_label)
        name_box.add(self.name_input)

        button = toga.Button(
            text="Say Hello!",
            on_press=self.say_hello,
            style=Pack(padding=5),
        )

        main_box.add(name_box)
        main_box.add(button)

        login_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        # TODO add Containers and Widgets to your login_box --- CAROLINE
        all_instances_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        # TODO add Containers and Widgets to your all_instances_box --- ATTA
        instance_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        # TODO add Containers and Widgets to your instance_box --- TOBIAS
        logout_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        # TODO add Containers and Widgets to your logout_box --- CAROLINE

        option_container = toga.OptionContainer(
            content=[
                toga.OptionItem("Main box", main_box),
                toga.OptionItem("Login", login_box),
                toga.OptionItem("All instances", all_instances_box),
                toga.OptionItem("Instance run", instance_box),
                toga.OptionItem("Logout", logout_box),
                ],
            on_select = self.option_item_changed,
            style=Pack(direction=COLUMN))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = option_container
        self.main_window.show()
        
    async def option_item_changed(self,widget):
        print('[i] You have selected another Option Item!')

    async def say_hello(self, widget):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://jsonplaceholder.typicode.com/posts/42")

        payload = response.json()

        self.main_window.info_dialog(
            greeting(self.name_input.value),
            payload["body"],
        )

def greeting(name):
    if name:
        return f"Hello, {name}"
    else:
        return "Hello, stranger"

def main():
    return HelloWorld()
