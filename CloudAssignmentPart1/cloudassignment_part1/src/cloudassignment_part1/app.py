import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from services.dcr_active_repository import check_login_from_dcr, DcrActiveRepository, EventsFilter, DcrUser

class CloudApp(toga.App):
    graph_id = "1986619"
    drc_ar = None


class HelloWorld(toga.App):

    
    def startup(self):

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
        # Add logout button
        button = toga.Button(
            text="Logout",
            on_press=self.print_message,
            style=Pack(padding=5),
        )

        logout_box.add(button)

        option_container = toga.OptionContainer(
            content=[
                #toga.OptionItem("Main box", main_box),
                toga.OptionItem("Login", login_box),
                toga.OptionItem("All instances", self.all_instances_box),
                toga.OptionItem("Instance run", instance_box),
                toga.OptionItem("Logout", logout_box),
                ],
            on_select = self.option_item_changed,
            style=Pack(direction=COLUMN))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = option_container
        self.main_window.show()

        self.option_container.content['Logout'].enabled = False
        self.option_container.content['All instances'].enabled = False
        self.option_container.content['Instance run'].enabled = False



    async def show_instances_box(self):
        self.all_instance_box.clear()

        self.all_instances_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        # TODO add Containers and Widgets to your all_instances_box --- ATTA
        all_instances_containner = toga.ScrollContainer(horizontal=False,style=Pack(flex=1))

        instances_label = toga.Label(
            text = "All instances will be listed here",
            style=Pack(padding=(0, 5))
        )

        create_delete_box= toga.Box(style=Pack(direction=COLUMN))

        create_button = toga.Button(
            text="Create new instances",
            on_press=self.create_new_instances,
            style=Pack(padding=5),
        )
        delete_button = toga.Button(
            text="Delete all instances",
            on_press=self.delete_all_instances,
            style=Pack(padding=5,color='red'),
        )

        create_delete_box.add(create_button)
        create_delete_box.add(delete_button)

        instances_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        self.instances = {}
        dcr_ar_instances = await self.dcr_ar.get_instances(self.graph_id)
        if len(dcr_ar_instances)>0:
            self.instances = dcr_ar_instances
            
        for instance in self.instances:
            buttons_box = toga.Box(style=Pack(direction=ROW))
            instance_button = toga.Button(
                instance['name'],
                on_press=self.show_instance,
                style=Pack(padding=5),
                id=instance['id']
            )
            buttons_box.add(instance_button)
            del_button = toga.Button(
                "X",
                on_press=self.delete_instance_by_id,
                style=Pack(padding=5,color='red'),
                id= f'X_{instance["id"]}'
            )
            buttons_box.add(del_button)
            instances_box.add(buttons_box)


        all_instances_containner.content = instances_box
        self.all_instances_box.add(instances_label)
        self.all_instances_box.add(create_delete_box)
        self.all_instances_box.add(all_instances_containner)

        self.all_instance_box.refresh()



    def role_changed(self,widget):
        print(f'[i] You changed the role to {widget.value}!')

    def execute_event(self, widget):
        print (f'[i] You want to execute event: {widget.id}')
        
    async def option_item_changed(self,widget):
        print('[i] You have selected another Option Item!')
        if widget.current_tab.text == 'All instances':
            await self.show_instances_box()

    async def delete_all_instances(self,widget):
        print('[i] Deleting all instances')
    async def create_new_instances(self,widget):
        print('[i] Creating new instances')
    async def show_instance(self,widget):
        print(f'[i] You want to show: {widget.id}')
    async def delete_instance_by_id(self,widget):
        print(f'[i] You want to delete: {widget.id}')
        

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

# Add gretting for login button
def login_greeting(username):
    if username:
        return f"Hello, {username}"

def main():
    return HelloWorld()
