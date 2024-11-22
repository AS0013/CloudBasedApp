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
        # Add username box
        username_label = toga.Label(
            text="Username:",
            style=Pack(padding=(0, 5)),
        )
        self.username_input = toga.TextInput(style=Pack(flex=1))

        username_box = toga.Box(style=Pack(direction=ROW, padding=5))
        username_box.add(username_label)
        username_box.add(self.username_input)

        # Add password box
        password_label = toga.Label(
            text="Password:",
            style=Pack(padding=(0, 5)),
        )
        self.password_input = toga.PasswordInput(style=Pack(flex=1))

        password_box = toga.Box(style=Pack(direction=ROW, padding=5))
        password_box.add(password_label)
        password_box.add(self.password_input)

        # Add login button
        button = toga.Button(
            text="Login",
            on_press=self.login_button,
            style=Pack(padding=5),
        )

        login_box.add(username_box)
        login_box.add(password_box)
        login_box.add(button)


        all_instances_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        # TODO add Containers and Widgets to your all_instances_box --- ATTA
        instance_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        # TODO add Containers and Widgets to your instance_box --- TOBIAS

        logout_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        # Add logout button
        button = toga.Button(
            text="Logout",
            on_press=self.print_message,
            style=Pack(padding=5),
        )

        logout_box.add(button)

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

    # Add login button handler
    async def login_button(self, widget):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://jsonplaceholder.typicode.com/posts/42")

        payload = response.json()

        self.main_window.info_dialog(
            login_greeting(self.username_input.value),
            payload["body"],
        )
    # Add message for logout button
    async def print_message(self,widget):
        print("You want to logout!")

def greeting(name):
    if name:
        return f"Hello, {name}"
    else:
        return "Hello, stranger"

# Add gretting for login button
def login_greeting(username):
    if username:
        return f"Hello, {username}"

def main():
    return HelloWorld()
