import httpx
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from services.dcr_active_repository import check_login_from_dcr, DcrActiveRepository, EventsFilter, DcrUser
from services import database_connection as dbc

class CloudApp(toga.App):
    graph_id = "1986619"
    dcr_ar = None
    current_instance_id = None
    
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

        self.all_instances_box = toga.Box(style=Pack(direction=COLUMN,flex=1))
        self.instance_box = toga.Box(style=Pack(direction=COLUMN,flex=1))

        logout_box = toga.Box(style=Pack(direction=COLUMN,flex=1))

        button = toga.Button(
            text="Logout",
            on_press=self.logout_handler,
            style=Pack(padding=5),
        )

        logout_box.add(button)

        self.option_container = toga.OptionContainer(
            content=[
                toga.OptionItem("Login", login_box),
                toga.OptionItem("All instances", self.all_instances_box),
                toga.OptionItem("Instance run", self.instance_box),
                toga.OptionItem("Logout", logout_box),
                ],
            on_select = self.option_item_changed,
            style=Pack(direction=COLUMN))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.option_container
        self.main_window.show()

        self.option_container.content['Logout'].enabled = False
        self.option_container.content['All instances'].enabled = False
        self.option_container.content['Instance run'].enabled = False



    async def role_changed(self,widget):
        print(f'[i] You changed the role to {widget.value}!')

        self.user.role = widget.value
        dbc.update_dcr_role(email=self.user.email,role=self.user.role)
        await self.show_instance_box()

    async def execute_event(self, widget):
        print (f'[i] You want to execute event: {widget.id}')
        events = await self.dcr_ar.execute_event(self.graph_id,self.current_instance_id,widget.id)

        is_valid_state = all(not event.pending for event in events)

        try:
            dbc.update_instance_state(instance_id=self.current_instance_id, valid_state=is_valid_state)
            print(f'[✓] Valid state updated in the database for instance {self.current_instance_id}')
        except Exception as ex:
            print(f'[x] Error updating instance valid state in the database: {ex}')

        await self.show_instance_box()
        
    async def option_item_changed(self,widget):
        print('[i] You have selected another Option Item!')
        if widget.current_tab.text == 'All instances':
            await self.show_instances_box()
        if widget.current_tab.text == 'Instance run':
            if not self.current_instance_id:
                instances = await self.dcr_ar.create_new_instance(self.graph_id)
                if instances:
                    self.current_instance_id = instances
                else:
                    self.current_instance_id = None  
            await self.show_instance_box()
        

    async def delete_all_instances(self, widget):
        print('[i] Deleting all instances')
        
        dcr_ar_instances = await self.dcr_ar.get_instances(self.graph_id)
        self.instances = dcr_ar_instances

        valid_instances = []
        
        for instance_id, _ in self.instances.items():
            instance_details = dbc.get_all_instances()
            if instance_details:
                for instance in instance_details:
                    if instance[0] == int(instance_id) and instance[1]:
                        valid_instances.append(instance_id)

        for instance_id in valid_instances:
            try:
                await self.dcr_ar.delete_instance(self.graph_id,instance_id)
            except Exception as ex:
                print(f'[x] error delete_instance! {ex}')
        
        
        await self.show_instances_box()
    
        self.current_instance_id = None

    


    async def create_new_instances(self,widget):
        print('[i] Creating new instances')
        self.option_container.current_tab = 'Instance run'
        new_instance_id = await self.dcr_ar.create_new_instance(self.graph_id)
        # await self.show_instance_box() #this is a comment
        if new_instance_id:
            events = await self.dcr_ar.get_events(self.graph_id, new_instance_id, EventsFilter.ALL)

            is_valid_state = all(not event.pending for event in events)

            try:
                dbc.insert_instance(new_instance_id, is_valid_state, self.user.email)
                print(f'[i] Inserted new instance {new_instance_id} with valid state: {is_valid_state}')
            except Exception as ex:
                print(f'[x] Error inserting instance into the database: {ex}')
            await self.show_instance_box()
        else:
            print('[x] Failed to create a new instance')


    async def show_instance(self,widget):
        print(f'[i] You want to show: {widget.id}')
        self.option_container.current_tab = 'Instance run'
        self.current_instance_id = widget.id

        self.show_instance_box()

    async def delete_instance_by_id(self,widget):
        print(f'[i] You want to delete: {widget.id}')
        instance_id_to_delete = widget.id.split('_')[1] 
        await self.dcr_ar.delete_instance(self.graph_id,instance_id_to_delete)
        await self.show_instances_box()
                

    # Add login button handler
    async def login_button(self, widget):
        connected = await check_login_from_dcr(self.username_input.value,self.password_input.value)

        if connected:
            self.user = DcrUser(self.username_input.value,self.password_input.value)
            self.user.role = dbc.get_dcr_role(email=self.user.email)
            print(f'[i] Role: {self.user.role}')
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

    async def show_instances_box(self):
        self.all_instances_box.clear()

        instances_label = toga.Label(
            text="All instances will be listed here",
            style=Pack(padding=(0, 5))
        )

        create_delete_box = toga.Box(style=Pack(direction=COLUMN))

        create_button = toga.Button(
            text="Create new instances",
            on_press=self.create_new_instances,
            style=Pack(padding=5),
        )
        delete_button = toga.Button(
            text="Delete all instances",
            on_press=self.delete_all_instances,
            style=Pack(padding=5, color='red'),
        )

        create_delete_box.add(create_button)
        create_delete_box.add(delete_button)

        instances_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        dcr_ar_instances = await self.dcr_ar.get_instances(self.graph_id)
        self.instances = dcr_ar_instances

        print("dcr_ar_instances", dcr_ar_instances)

        if dcr_ar_instances:
            for instance_id, instance_name in self.instances.items():
                buttons_box = toga.Box(style=Pack(direction=ROW))

                instance_button = toga.Button(
                    text=instance_name,
                    on_press=self.show_instance,
                    style=Pack(padding=5),
                    id=instance_id
                )
                buttons_box.add(instance_button)

                del_button = toga.Button(
                    "X",
                    on_press=self.delete_instance_by_id,
                    style=Pack(padding=5, color='red'),
                    id=f'X_{instance_id}'
                )
                buttons_box.add(del_button)

                instances_box.add(buttons_box)
        else:
            no_instances_label = toga.Label(
            text="No instances available",
            style=Pack(padding=(0, 5))
            )
            instances_box.add(no_instances_label)


        all_instances_container = toga.ScrollContainer(horizontal=False, style=Pack(flex=1))
        all_instances_container.content = instances_box

        self.all_instances_box.add(instances_label)
        self.all_instances_box.add(create_delete_box)
        self.all_instances_box.add(all_instances_container)

        self.all_instances_box.refresh()

    

    async def show_instance_box(self):
        self.instance_box.clear()
        scroll = toga.ScrollContainer(horizontal=False,style=Pack(flex=1))
        event_box = toga.Box(style=Pack(direction=COLUMN, padding = 5))

        events = []

        print("current_instance_id", self.current_instance_id)

        events = await self.dcr_ar.get_events(self.graph_id, self.current_instance_id, EventsFilter.ALL)
        
        role_items = []


        each_instance = toga.Label(
            text = "Each instance will appear here"
        )

        if self.user.role:
            role_items.append(self.user.role)
        print("events", events)
        for event in events:
            color = None
            btn_enabled = True
            text = event.label
            event_role = event.role
            if event_role not in role_items:
                role_items.append(event_role)
            if event.enabled:
                color = 'green'
                print("text", text)
            if event.pending:
                color = 'blue'
                text = text + " !"
            if len(event.role) > 0:
                if event.role != self.user.role:
                    btn_enabled = False
                text = text + f" (role: {event.role})"
            if event.enabled:
                event_button = toga.Button(
                    text =  text,
                    style = Pack(padding = 5, color = color),
                    id = event.id,
                    on_press = self.execute_event,
                    enabled = btn_enabled
                )
                event_box.add(event_button)
        
        self.role_selection = toga.Selection(
            items = role_items,
            on_change = self.role_changed,
            style=Pack(padding=5),
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
        role_box.add(role_label)
        role_box.add(select_role)
        role_box.add(self.role_selection)
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
    

        scroll.content = event_box

        self.instance_box.add(each_instance)
        self.instance_box.add(main1_box)
        self.instance_box.add(scroll)

        self.instance_box.refresh()


    # Add message for logout button
    async def print_message(self,widget):
        print("You want to logout!")


    async def logout_handler(self,widget):
         self.option_container.content['Login'].enabled = True
         self.option_container.current_tab = 'Login'

         self.option_container.content['All instances'].enabled = False
         self.option_container.content['Instance run'].enabled = False
         self.option_container.content['Logout'].enabled = False

         self.username_input.value = None
         self.password_input.value = None
def main():
    return CloudApp()


