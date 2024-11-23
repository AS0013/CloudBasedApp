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

        all_instances = toga.Label(
            text = "Each instance will appear here"
        )

        role_items = list([' ', 'Doctor', 'Nurse', 'Patient'])
        selected_role_item = 'Doctor'
        events = [
            {'id': 'Diagnose', 'label': 'Diagnose', 'role': 'Doctor'},
            {'id': 'Operate', 'label': 'Operate', 'role': 'Doctor'},
            {'id': 'Give treatment', 'label': 'Give treatment', 'role': 'Nurse'},
            {'id': 'Take treatment', 'label': 'Take treatment', 'role': 'Patient'}]
        
        main1_box = toga.Box(style = Pack(direction = ROW))

        role_box = toga.Box(style = Pack(direction = COLUMN,  flex = 1))
        role_label = toga.Label(
            text = "Current Role:",
            style=Pack(padding=(0, 5)),
        )
        select_role = toga.Label(
            text = "Select other role:",
            style=Pack(padding=(0, 5)),
        )
        self.selections = toga.Selection(items = role_items, 
                                    value = role_items[0], 
                                    on_change = self.role_changed,
                                    style=Pack(padding=(0, 5)),
                                    )
        
        role_box.add(role_label)
        role_box.add(select_role)
        role_box.add(self.selections)
        main1_box.add(role_box)
    

        
        instance_box_inner = toga.Box(style = Pack(direction = COLUMN, flex = 1))
        instance_label = toga.Label(
            text = "Current Instance:",
            style=Pack(padding=(0, 5)),
        )

        added = toga.Label(
            text = "Not added yet!",
            style=Pack(padding=(0, 5)),
        )

        instance_box_inner.add(instance_label)
        instance_box_inner.add(added)
        main1_box.add(instance_box_inner)
        


        scroll = toga.ScrollContainer(horizontal=False,style=Pack(flex=1))
        event_box = toga.Box(style=Pack(direction=COLUMN, padding = 5))
        for event in events:
            event_button = toga.Button(text =  f"{event['label']} (role: {event['role']})",
                                       id = event['id'],
                                       style=Pack( color='green'),
                                       on_press = self.execute_event,)
            event_box.add(event_button)
        scroll.content = event_box

        instance_box.add(all_instances)
        instance_box.add(main1_box)
        instance_box.add(scroll)
        

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


    def role_changed(self,widget):
        print(f'[i] You changed the role to {widget.value}!')

    def execute_event(self, widget):
        print (f'[i] You want to execute event: {widget.id}')
        
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
