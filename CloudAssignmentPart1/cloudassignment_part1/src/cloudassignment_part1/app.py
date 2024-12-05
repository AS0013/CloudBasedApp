import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from services.dcr_active_repository import check_login_from_dcr, DcrActiveRepository, EventsFilter, DcrUser


class HelloWorld(toga.App):
    graph_id = "1986619"
    dcr_ar = None
    
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


        all_instances_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
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
        instances = [{'id': 1, 'name': 'Atta',},
                     {'id': 2, 'name': 'Caroline',}, 
                     {'id': 3, 'name': 'Tobias',},
                     {'id': 4, 'name': 'Instance 4',},
                     {'id': 5, 'name': 'Instance 5',}]
        for instance in instances:
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
        all_instances_box.add(instances_label)
        all_instances_box.add(create_delete_box)
        all_instances_box.add(all_instances_containner)


        self.instance_box = toga.Box(style=Pack(direction=COLUMN,flex=1))

        logout_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        # Add logout button
        button = toga.Button(
            text="Logout",
            on_press=self.print_message,
            style=Pack(padding=5),
        )

        logout_box.add(button)

        self.option_container = toga.OptionContainer(
            content=[
                toga.OptionItem("Login", login_box),
                toga.OptionItem("All instances", all_instances_box),
                toga.OptionItem("Instance run", self.instance_box),
                toga.OptionItem("Logout", logout_box),
                ],
            on_select = self.option_item_changed,
            style=Pack(direction=COLUMN))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.option_container
        self.main_window.show()


    def role_changed(self,widget):
        print(f'[i] You changed the role to {widget.value}!')

        self.user.role = widget.value
        self.show_instance_box()

    def execute_event(self, widget):
        print (f'[i] You want to execute event: {widget.id}')

        self.current_instance_id = self.dcr_ar.get_instances(self.graph_id)[0]
        self.dcr_ar.execute_event(self.graph_id,self.current_instance_id,widget.id)
        self.show_instance_box()
        
    async def option_item_changed(self,widget):
        print('[i] You have selected another Option Item!')

        if widget.current_tab.text == 'Instance run':
            self.show_instance_box()

    async def delete_all_instances(self,widget):
        print('[i] Deleting all instances')
    async def create_new_instances(self,widget):
        print('[i] Creating new instances')

        await self.dcr_ar.create_new_instance(self.graph_id)
        self.show_instance_box()


    async def show_instance(self,widget):
        print(f'[i] You want to show: {widget.id}')

        self.current_instance_id = await self.dcr_ar.get_instances(self.graph_id)[0]

        self.show_instance_box()

    async def delete_instance_by_id(self,widget):
        print(f'[i] You want to delete: {widget.id}')
    
    # Add login button handler
    async def login_button(self, widget):
        connected = await check_login_from_dcr(self.username_input.value,self.password_input.value)

        if connected:
            self.user = DcrUser(self.username_input.value,self.password_input.value)
            self.dcr_ar = DcrActiveRepository(self.user)

            self.option_container.content['All instances'].enabled = True   

            self.option_container.current_tab = 'All instances'

            self.option_container.content['Instance run'].enabled = True
            self.option_container.content['Logout'].enabled = True
            self.option_container.content['Login'].enabled = False

            print("current tab", self.option_container.current_tab)


            self.main_window.info_dialog('Login', 'You are connected!')
        else:
            self.main_window.info_dialog('Login', 'Failed to connect!')

    async def show_instance_box(self):
        print('Show instance box')
        self.instance_box.clear()

        events = await self.dcr_ar.get_events(self.graph_id,self.current_instance_id,EventsFilter.ALL)
        role_items = []

        each_instance = toga.Label(
            text = "Each instance will appear here"
        )

        if self.user.role:
            role_items.append(self.user.role)
        for event in events:
            event_role = event.role
            if event_role not in role_items:
                role_items.append(event_role)
        
        self.role_selection = toga.Selection(
            items = role_items,
            on_change = self.role_changed,
            style=Pack(padding=(0, 5)),
        )
        if len(role_items) > 0:
            self.role_selection.value = role_items[0]
            self.user.role = self.role_selection.value

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
            color = None
            btn_enabled = True
            text = event.label
            if event.enabled:
                color = 'green'
            if event.pending:
                color = 'blue'
                text = text + " !"
            if len(event.role) > 0:
                if event.role != self.user.role:
                    btn_enabled = False
                text = text + f" (role: {event.role})"
            if event.enables:
                event_button = toga.Button(
                    text =  text,
                    style = Pack(padding = 5, color = color),
                    id = event.id,
                    on_press = self.execute_event,
                    enabled = btn_enabled
                )
                event_box.add(event_button)
            

        scroll.content = event_box

        self.instance_box.add(each_instance)
        self.instance_box.add(main1_box)
        self.instance_box.add(scroll)

        self.instance_box.refresh()

        self.option_container.content['Instance run'] = self.instance_box


    # Add message for logout button
    async def print_message(self,widget):
        print("You want to logout!")

# Add gretting for login button
def login_greeting(username):
    if username:
        return f"Hello, {username}"

def main():
    return HelloWorld()
