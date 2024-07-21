from gi.repository import GObject
from gi.repository import Gtk
from gramps.gen.plug import Gramplet
from gramps.gui.editors.editevent import EditEvent
from templatehandler import HandleTemplate
from eventmenu import EventMenuWidget
from form import Form
import os
import json

class GuiBuilder():
    def __init__(self, dbstate):
        self.dbstate = dbstate
        # Instantiate Template Handling
        self.TemplateHandler = HandleTemplate()
    
    # Build Tree Selector for Forms
    def formid_selector_builder(self, form_files, adaptive_height):
        self.stacked_options = Gtk.Stack()
        self.stacked_options.set_hhomogeneous(False)

        model = Gtk.TreeStore(str)

        form_mappings = {}

        # List of forms in form files
        for filename in form_files:

            # Load form module
            self.formReader = Form([filename])
            form_ids = self.formReader.get_form_ids()

            # Record total # of elements
            adaptive_height += len(form_ids)

            parent_node = model.append(None, [filename])

            # List of form definitions
            for form_id in list(form_ids):

                form_mappings[form_id] = filename

                # Build folders for templates if they do not exist
                self.setup_template_directories(form_id)

                # Add each form's custom interface to tree selector
                model.append(parent_node, [form_id])
                hbox = self.add_menu_from_form(form_id)

                scroll_forms = Gtk.ScrolledWindow()
                scroll_forms.add(hbox)
                scroll_forms.set_policy(Gtk.PolicyType.NEVER, 
                                        Gtk.PolicyType.AUTOMATIC)
                scroll_forms.set_propagate_natural_height(True)
                
                self.stacked_options.add_named(child=scroll_forms, name=form_id)
            
        tree_view = Gtk.TreeView(model=model)

        # Record the parent file of each form_id
        mappings_path = os.path.join(os.path.dirname(__file__), "form-mappings.json")
        with open(mappings_path, 'w') as f:
            form_mappings = json.dumps(form_mappings, indent=4)
            f.write(form_mappings)

        return tree_view, adaptive_height, self.stacked_options

    # Dynamically create each menu based on xml tags
    def add_menu_from_form(self, form_id):
        hbox = Gtk.Box()
        hbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        hbox.set_spacing(5)

        # Add title of form
        form_title = self.formReader.get_title(form_id)

        # Add internal frame to box
        settings_container = Gtk.Frame()
        settings_container.set_label(form_title)

        # Add box to frame
        sections_container = Gtk.Box()
        sections_container.set_orientation(Gtk.Orientation.VERTICAL)
        sections_container.set_spacing(5)
        sections_container.set_margin_start(10)
        sections_container.set_margin_end(10)

        """
        Add section content
        """
        sections = self.formReader.get_sections(form_id)
        section_titles = [self.formReader.get_section_title(form_id, i) for i in sections]

        # Iterate through sections
        for n, section in enumerate(sections):
            section_frame = Gtk.Frame()

            # Labels and Entries Grid boxes
            form_label_entry_grid = Gtk.Grid()
            form_label_entry_grid.insert_row(0)
            form_label_entry_grid.insert_row(1)

            # Add column names
            form_columns = self.formReader.get_section_columns(form_id, section)

            for placement, column in enumerate(form_columns):

                column_name = column[0]
                column_label = Gtk.Label()
                column_label.set_text(column_name)
                
                form_label_entry_grid.attach(column_label, left=placement, top=0, width=1, height=1)

                # Add + buttons
                image = Gtk.Image()
                image.set_from_icon_name('list-add', Gtk.IconSize.BUTTON)
                add_btn = Gtk.Button()
                add_btn.set_relief(Gtk.ReliefStyle.NONE)
                add_btn.add(image)
                add_btn.connect('clicked', self.add_event_dropdown)
                form_label_entry_grid.attach(add_btn, left=placement, top=1, width=1, height=1)

            # Add settings for section
            row_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

            row_container.pack_start(form_label_entry_grid, False, False, 0)

            section_frame.pack_start(row_container, False, False, 0)

            # Title exists
            if len(section_titles[n]) > 0:
                section_frame.set_label(section_titles[n])
                sections_container.pack_start(section_frame, False, False, 0)

            # Title doesn't exist
            else:
                section_frame.set_label(section)
                sections_container.pack_start(section_frame, False, False, 0)                

        # Add each section to the settings
        settings_container.pack_start(sections_container, False, False, 0)

        hbox.pack_start(settings_container, False, False, 0)

        return hbox

    # Dynamically create each menu based on xml tags
    def add_menu_from_form(self, form_id):
        hbox = Gtk.Box()
        hbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        hbox.set_spacing(5)

        # Add title of form
        form_title = self.formReader.get_title(form_id)

        # Add internal frame to box
        settings_container = Gtk.Frame()
        settings_container.set_label(form_title)

        # Add box to frame
        sections_container = Gtk.Box()
        sections_container.set_orientation(Gtk.Orientation.VERTICAL)

        """
        Add section content
        """
        sections = self.formReader.get_sections(form_id)
        section_titles = [self.formReader.get_section_title(form_id, i) for i in sections]

        # Iterate through sections
        for n, section in enumerate(sections):
            section_frame = Gtk.Frame()

            # Labels and Entries Grid boxes
            form_label_entry_grid = Gtk.Grid()
            form_label_entry_grid.insert_row(0)
            form_label_entry_grid.insert_row(1)

            # Add column names
            form_columns = self.formReader.get_section_columns(form_id, section)

            for placement, column in enumerate(form_columns):

                column_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                
                column_name = column[0]
                column_label = Gtk.Label(margin=5)
                column_label.set_text(column_name)
                column_container.pack_start(column_label, False, False, 0)

                # Add + buttons
                image = Gtk.Image()
                image.set_from_icon_name('list-add', Gtk.IconSize.BUTTON)
                add_btn = Gtk.Button()
                add_btn.set_relief(Gtk.ReliefStyle.NONE)
                add_btn.add(image)
                add_btn.connect('clicked', self.add_event_dropdown)
                column_container.pack_start(add_btn, False, False, 0)
                form_label_entry_grid.attach(column_container, left=placement, top=0, width=1, height=1)

            # Add settings for section
            row_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

            row_container.pack_start(form_label_entry_grid, False, False, 0)

            section_frame.add(row_container)

            # Title exists
            if len(section_titles[n]) > 0:
                section_frame.set_label(section_titles[n])
                sections_container.pack_start(section_frame, False, False, 0)

            # Title doesn't exist
            else:
                section_frame.set_label(section)
                sections_container.pack_start(section_frame, False, False, 0)                

        # Add each section to the settings
        settings_container.add(sections_container)

        hbox.pack_start(settings_container, False, False, 0)

        return hbox

    def add_event_dropdown(self, add_btn):

        column_dropdown = Gtk.ComboBox(has_entry=True, 
                                       margin=3)
        
        column_dropdown_events = EventMenuWidget(obj=column_dropdown,
                                                custom_values=self.get_custom_events()).obj
        
        # Select containing box
        form_label_entry_box = add_btn.get_ancestor(Gtk.Box())

        form_label_entry_box.pack_start(column_dropdown_events, False, False, 0)
        form_label_entry_box.show_all()

    def load_event_dropdown(self, form_label_entry_box, stored_value):

        column_dropdown = Gtk.ComboBox(has_entry=True, 
                                       margin=3)
        
        column_dropdown_events = EventMenuWidget(obj=column_dropdown,
                                                 custom_values=self.get_custom_events()).obj
        
        entry = column_dropdown_events.get_children()[0]
        entry.set_text(stored_value)

        form_label_entry_box.pack_start(column_dropdown_events, False, False, 0)
        form_label_entry_box.show_all()

    def get_custom_events(self):
        return sorted(self.dbstate.db.get_event_types(), key=lambda s: s.lower())

    def get_grid_rows_for_column(self, grid, col):
        rows = 0
        for child in grid.get_children():
            if grid.child_get_property(child, 'left-attach') == col:
                y = grid.child_get_property(child, 'top-attach')
                rows = max(rows, y)
        return rows
    
    def get_grid_rows(self, grid):
        rows = 0
        for child in grid.get_children():
            y = grid.child_get_property(child, 'top-attach')
            rows = max(rows, y)
        return rows

    # Create directories for each form if they don't already exist
    def setup_template_directories(self, form_id):
        template_path = os.path.join(os.path.dirname(__file__), "Forms", "Templates")
        master_form_path = os.path.join(template_path, form_id)
        if not os.path.exists(master_form_path):
            os.makedirs(master_form_path)

    def load_template_file(self, form_id, template_name, settings_window, template_builder):
        template_folder = os.path.join(os.path.dirname(__file__), "Forms", "Templates", form_id)
        template_file = os.path.join(template_folder, template_name)

        with open(template_file, 'r') as f:
            settings = json.load(f)

        # Focus on widget group containing components of selected form settings
        current = template_builder.step_down_initial(settings_window)
        for child in current:
            if child.get_name() == "GtkStack":

                selected_form = child.get_visible_child()
                
                selected_form = template_builder.step_down(selected_form, "GtkViewport")
                selected_form = template_builder.step_down(selected_form, "GtkBox")
                selected_form = template_builder.step_down(selected_form, "GtkFrame")

                container_frame = selected_form[0]

                template_file_name = template_name.replace('.json','')

                # Label for Template Name
                entry_label = Gtk.Label()
                entry_label.set_label("Template Name:")
                entry_label.set_margin_top(5)
                entry_label.set_margin_bottom(5)
                entry_label.set_margin_start(5)

                # Entry For Template Name
                self.name_entry = Gtk.Entry()
                self.name_entry.set_text(template_file_name)
                self.name_entry.set_margin_top(5)
                self.name_entry.set_margin_bottom(5)
                self.name_entry.set_margin_start(5)

                # Grid with Template Options
                form_name_entry = Gtk.Grid()
                form_name_entry.set_name("TemplateOptions")
                form_name_entry.set_margin_top(5)
                form_name_entry.set_margin_bottom(5)
                form_name_entry.set_margin_start(5)

                # Save Button
                save_btn = Gtk.Button(label="Save")
                save_btn.connect('clicked', self.template_saver)

                # Master Label
                template_section_label = Gtk.Label()
                template_section_label.set_margin_top(5)
                template_section_label.set_margin_bottom(5)
                template_section_label.set_margin_start(5)
                template_section_label.set_markup("<b><u>Template Options</u></b>")

                form_name_entry.attach(template_section_label, 0,0,1,1)
                form_name_entry.attach(entry_label, 0,1,1,1)
                form_name_entry.attach(self.name_entry, 1,1,1,1)
                form_name_entry.attach(save_btn, 2, 1, 1, 1)

                selected_form = template_builder.step_down(selected_form, "GtkBox")
                
        for s in selected_form:
            if s.get_name() != "GtkEntry":
                focused = reversed(s.get_children())
                for section in focused:

                    # Get Section Titles
                    if section.get_name() == "GtkLabel":
                        section_title = section.get_text()

                    # Box
                    else:

                        for section_name in section:
                            
                            for field_box in section_name.get_children():

                                for field in field_box.get_children():
                                        
                                    # Get box and add settings
                                    if field.get_name()=="GtkLabel":
                                        field_name = field.get_text()
                                        containing_box = field.get_ancestor(Gtk.Box())

                                        # Add the comboboxes
                                        combobox_settings = settings[section_title][field_name]

                                        for setting in combobox_settings:
                                            self.load_event_dropdown(containing_box, setting)

        container_frame.pack_start(form_name_entry, True, True, 0)
        container_frame.show_all()

    def populate_template(self, settings_window, template_builder, settings):

        template_name = ""

        # Focus on widget group containing components of selected form settings
        current = template_builder.step_down_initial(settings_window)
        for child in current:
            if child.get_name() == "GtkStack":

                selected_form = child.get_visible_child()
                
                selected_form = template_builder.step_down(selected_form, "GtkViewport")
                selected_form = template_builder.step_down(selected_form, "GtkBox")
                selected_form = template_builder.step_down(selected_form, "GtkFrame")

                container_frame = selected_form[0]

                template_file_name = template_name.replace('.json','')

                # Label for Template Name
                entry_label = Gtk.Label()
                entry_label.set_label("Template Name:")
                entry_label.set_margin_top(5)
                entry_label.set_margin_bottom(5)
                entry_label.set_margin_start(5)

                # Entry For Template Name
                self.name_entry = Gtk.Entry()
                self.name_entry.set_text(template_file_name)
                self.name_entry.set_margin_top(5)
                self.name_entry.set_margin_bottom(5)
                self.name_entry.set_margin_start(5)

                # Grid with Template Options
                form_name_entry = Gtk.Grid()
                form_name_entry.set_name("TemplateOptions")
                form_name_entry.set_margin_top(5)
                form_name_entry.set_margin_bottom(5)
                form_name_entry.set_margin_start(5)

                # Save Button
                save_btn = Gtk.Button(label="Save")
                save_btn.connect('clicked', self.template_saver)

                # Master Label
                template_section_label = Gtk.Label()
                template_section_label.set_margin_top(5)
                template_section_label.set_margin_bottom(5)
                template_section_label.set_margin_start(5)
                template_section_label.set_markup("<b><u>Template Options</u></b>")

                form_name_entry.attach(template_section_label, 0,0,1,1)
                form_name_entry.attach(entry_label, 0,1,1,1)
                form_name_entry.attach(self.name_entry, 1,1,1,1)
                form_name_entry.attach(save_btn, 2, 1, 1, 1)

                selected_form = template_builder.step_down(selected_form, "GtkBox")
                
        for s in selected_form:
            if s.get_name() != "GtkEntry":
                focused = reversed(s.get_children())
                for section in focused:

                    # Get Section Titles
                    if section.get_name() == "GtkLabel":
                        section_title = section.get_text()

                    # Box
                    else:

                        for section_name in section:
                            
                            for field_box in section_name.get_children():

                                for field in field_box.get_children():
                                        
                                    # Get box and add settings
                                    if field.get_name()=="GtkLabel":
                                        field_name = field.get_text()
                                        containing_box = field.get_ancestor(Gtk.Box())

        container_frame.pack_start(form_name_entry, True, True, 0)
        container_frame.show_all()

    def template_saver(self, btn):

        # Select grid
        window = self.stacked_options
        
        settings, form_id = self.TemplateHandler.get_current_settings(window)

        template_name = self.name_entry.get_text() + '.json'

        # Write Template File
        template_path = os.path.join(os.path.dirname(__file__), "Forms", "Templates", form_id,template_name)

        settings = json.dumps(settings, indent=4)
        with open(template_path,'w') as f:
             f.write(settings)