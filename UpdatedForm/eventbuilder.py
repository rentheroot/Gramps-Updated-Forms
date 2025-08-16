#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024 Renee Schmidt
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from gi.repository import GObject
from gi.repository import Gtk, Gdk
from gramps.gen.plug import Gramplet
from gramps.gui.editors.editevent import EditEvent
from eventmenu import EventMenuWidget
from form import Form
import os
import json

class DropAreaTextExtractor():

    # Initialize with relevant JSON data
    def __init__(self, j_data):
        self.j_data = j_data

        '''
        Categories of Components
        for logical checks
        '''
        self.int_operations = [
            "plus",
            "minus",
            "divide",
            "times"
        ]

        self.str_operations = [
            "plus"
        ]

        self.int_comparators = [
            "greater",
            "less",
            "less-equal",
            "great-equal",
            "not-equal-to",
            "equal"
        ]

        self.str_comparators = [
            "not-equal-to",
            "equal"
        ]

        self.as_text = {
            'plus' : '+',
            'minus' : '-',
            'divide' : '÷',
            'times' : '*',
            'greater' : '>',
            'less' : '<',
            'equal' : '=',
            'great-equal' : '>=',
            'less-equal' : '<=',
            'not-equal-to' : '!='
        }

        self.numerical = [
            "Integer"
        ]
        self.string = [
            "Text"
        ]

        self.extract()

    # Extract text version of validated json
    def extract(self):
        
        self.valid = True
        self.text_representation = ""
        self.error_representation = ""

        # JSON first Layer (Numbers)
        positions = sorted(self.j_data.keys())
        sub_data = self.j_data
        self.error_catcher(positions, sub_data)
        
    def error_catcher(self, positions, sub_data):

        if self.valid == True:

            for pos in positions:

                component = sub_data[pos]

                # Add to text representation
                if type(component) == dict:
                    pass

                elif type(component) == tuple:
                    if component[0] == "Text":
                        self.text_representation += f' "{component[1]}" '
                    if component[0] == "Integer":
                        self.text_representation += f' {component[1]} '

                else:
                    if component in self.as_text.keys():
                        self.text_representation += f' {self.as_text[component]} '

                component_types = self.check_component_type(component)

                # Check for sub-layers
                if type(component) is dict:
                    if 'if' in component.keys():
                        sub_dict = component['if']

                        # Validate Subsections
                        if_section = sub_dict['if-section']
                        then_section = sub_dict['then-section']

                        if len(if_section.keys()) == 0:
                            self.error_representation = "Error: The 'if' section of the 'if' component must have subcomponents"
                            self.valid = False

                        if len(then_section.keys()) == 0:
                            self.error_representation = "Error: The 'then' section of the 'if' component must have subcomponents"
                            self.valid = False

                        # Check all sub layers
                        if self.valid == True:
                            sub_pos = sorted(if_section.keys())
                            self.error_catcher(sub_pos, if_section)

                            sub_pos = sorted(then_section.keys())
                            self.error_catcher(sub_pos, then_section)

                    elif 'if-else' in component.keys():
                        sub_dict = component['if-else']

                        # Validate Subsections
                        if_section = sub_dict['if-section']
                        then_section = sub_dict['then-section']
                        else_section = sub_dict['else-section']

                        if len(if_section.keys()) == 0:
                            self.error_representation = "Error: The 'if' section of the 'if-else' component must have subcomponents"
                            self.valid = False

                        if len(then_section.keys()) == 0:
                            self.error_representation = "Error: The 'then' section of the 'if-else' component must have subcomponents"
                            self.valid = False

                        if len(else_section.keys()) == 0:
                            self.error_representation = "Error: The 'else' section of the 'if-else' component must have subcomponents"
                            self.valid = False

                        # Check all sub layers
                        if self.valid == True:
                            sub_pos = sorted(if_section.keys())
                            self.error_catcher(sub_pos, if_section)

                            sub_pos = sorted(then_section.keys())
                            self.error_catcher(sub_pos, then_section)

                            sub_pos = sorted(else_section.keys())
                            self.error_catcher(sub_pos, else_section)

                # Some components need to be between two variables
                prev_pos = pos - 1
                next_pos = pos + 1

                if "int_operation" in component_types or \
                    "str_operation" in component_types or \
                    "int_comparator" in component_types or \
                    "str_comparator" in component_types:

                    if prev_pos < 0:
                        
                        if "str_comparator" in component_types or \
                            "str_operation" in component_types:

                            self.error_representation = f"Error: The '{component}' component must be placed between two string or numerical values"
                            self.valid = False

                        else:
                            
                            self.error_representation = f"Error: The '{component}' component must be placed between two numerical values"
                            self.valid = False

                    else:

                        try:
                            prev_component = sub_data[prev_pos]
                            next_component = sub_data[next_pos]

                            if type(prev_component) is tuple:
                                prev_component = prev_component[0]

                            if type(next_component) is tuple:
                                next_component = next_component[0]

                            prev_types = self.check_component_type(prev_component)
                            next_types = self.check_component_type(next_component)

                            all_types = [*prev_types, *next_types]

                            # Don't allow two operations one after the other
                            if "int_operation" in all_types or \
                                "str_operation" in all_types or \
                                "int_comparator" in all_types or \
                                "str_comparator" in all_types:

                                if "str_comparator" in component_types or \
                                    "str_operation" in component_types:

                                    self.error_representation = f"Error: The '{component}' component must be placed between two string or numerical values"
                                    self.valid = False

                                else:
                                    
                                    self.error_representation = f"Error: The '{component}' component must be placed between two numerical values"
                                    self.valid = False 

                            # Check next and prev component types
                            else:
                                if "int" in all_types:
                                    if component not in [*self.int_operations, *self.int_comparators]:
                                        self.error_representation = f"Error: The '{component}' component cannot be placed between numerical values"
                                        self.valid = False
                                        
                                if "str" in all_types and self.valid is True:
                                    if component not in [*self.str_operations, *self.str_comparators]:
                                        self.error_representation = f"Error: The '{component}' component cannot be placed between textual values"
                                        self.valid = False
                                        

                        # No next component
                        except KeyError:

                            if "str_comparator" in component_types or \
                                "str_operation" in component_types:

                                self.error_representation = f"Error: The '{component}' component must be placed between two string or numerical values"
                                self.valid = False

                            else:
                                
                                self.error_representation = f"Error: The '{component}' component must be placed between two numerical values"
                                self.valid = False

    def check_component_type(self, component):
        
        types = []
        if type(component) is tuple:
            component = component[0]
        if component in self.int_operations:
            types.append("int_operation")
        if component in self.str_operations:
            types.append("str_operation")
        if component in self.int_comparators:
            types.append("int_comparator")
        if component in self.str_comparators:
            types.append("str_comparator")
        if component in self.numerical:
            types.append("int")
        if component in self.string:
            types.append("str")

        return(types)

class DroppedDataExtractor():

    def __init__(self, parent_widget):
        self.parent_widget = parent_widget

    def iter_widgets(self, parent_grid):

        # First layer of widgets
        og_num_children = len(parent_grid.get_children())
        
        # Count widgets that take up more than one column
        num_children = og_num_children
        for i in range(0, num_children):
            child = parent_grid.get_child_at(i, 0)
            if child == None:
                og_num_children += 1

        num_children = og_num_children

        top_layer = []

        # Get the components of the first layer in order
        for i in range(0, num_children):
            try:
                child = parent_grid.get_child_at(i, 0)
                top_layer.append(child)

            # Error catcher for if there is no child at location
            except:
                pass

        # Start Building Settings Dictionary
        settings_dict = {}
        num_items = 0

        # Iterate through first layer of components
        for i in top_layer:

            """
            If a widget covers more than one column, 
            the widget will only be identified
            when the first column the widget is part of
            is queried. The rest of the columns covered by
            the widget will be Nonetype objects
            """
            if i == None:
                pass

            else:
                children = i.get_children()
                for child in children:

                    # Check for Components with Sub-Widgets
                    if child.get_name() in ["if", "if-else"]:
                        sub_dict = self.handle_sub_widgets(child)
                        settings_dict[num_items] = {child.get_name() : sub_dict}
                        num_items += 1

                    # Check for constants with values
                    elif child.get_name() == "Text":
                        entry_widgets = child.get_children()
                        for w in entry_widgets:
                            if w.get_name() == "string":
                                settings_dict[num_items] = ("Text", w.get_text())
                        num_items += 1

                    elif child.get_name() == "Integer":
                        entry_widgets = child.get_children()
                        for w in entry_widgets:
                            if w.get_name() == "integer":
                                settings_dict[num_items] = ("Integer", w.get_text())
                        num_items += 1

                    # Check for Components without Sub-Widgets
                    else:
                        settings_dict[num_items] = child.get_name()
                        num_items += 1

        return(settings_dict)
    
    def save_full_config(self,btn):
        full_config = {}
        child = self.parent_widget.get_parent().get_parent().get_children()
        stack_contents = ["DateGrid", "DescGrid", "PlaceGrid", "RoleGrid"]

        for c in child:
            if c.get_name() == "GtkStack":
                for slide in stack_contents:
                    current_slide = c.get_child_by_name(slide)
                    full_config[slide] = self.iter_widgets(current_slide)

        config_path = os.path.join(os.path.dirname(__file__), 'testsave.txt')
        with open(config_path, 'w') as f:
            print(json.dumps(full_config, indent=4))
            f.write(json.dumps(full_config, indent=4))

    def refresh_config_json(self, btn):
        slide_config = {}
        child = self.parent_widget.get_parent().get_parent().get_children()
        stack_contents = ["DateGrid", "DescGrid", "PlaceGrid", "RoleGrid"]

        for c in child:
            if c.get_name() == "GtkStack":
                for slide in stack_contents:
                    current_slide = c.get_child_by_name(slide)
                    slide_config[slide] = self.iter_widgets(current_slide)

                    text_data_obj = DropAreaTextExtractor(slide_config[slide])
                    text_data = text_data_obj.text_representation
                    del text_data_obj

                    print(text_data)

        config_path = os.path.join(os.path.dirname(__file__), 'testsave.txt')
        j_data = json.dumps(slide_config, indent=4)
        

        return(j_data)

    def handle_sub_widgets(self, component):
        sub_widget_dict = {}

        for grid in component.get_children():

            # Iterate through sections of component
            for i in grid.get_children():

                if i.get_name() in ["if-section", "then-section", "else-section"]:
                    sub_dict = self.iter_widgets(i)
                    sub_widget_dict[i.get_name()] = sub_dict

        return(sub_widget_dict)

class DropArea(Gtk.Grid):

    def __init__(self):
        Gtk.Grid.__init__(self)
        self.set_column_spacing(10)
        self.on_update = None

        blank = Gtk.Button()
        
        blank.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        blank.drag_dest_add_text_targets()
        blank.connect("drag-data-received", self.on_drag_data_received)
        
        self.add(blank)
        self.show_all()

        self.ExtractData = DroppedDataExtractor(self)



    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        text = data.get_text()
        self.build_widget(text, widget)

        self.ExtractData.refresh_config_json(widget)
        if self.on_update:
            self.on_update()
        
    def build_widget(self, received_text, dest_widget):
        
        if received_text == "Minus":
            self.make_icon_tool("minus", dest_widget)

        if received_text == "Plus":
            self.make_icon_tool("plus", dest_widget)

        if received_text == "Times":
            self.make_icon_tool("times", dest_widget)

        if received_text == "Divide":
            self.make_icon_tool("divide", dest_widget)

        if received_text == "Equal":
            self.make_icon_tool("equal", dest_widget)

        if received_text == "Not Equal":
            self.make_icon_tool("not-equal-to", dest_widget)

        if received_text == "Less Than":
            self.make_icon_tool("less", dest_widget)

        if received_text == "Less Than / Equal to":
            self.make_icon_tool("less-equal", dest_widget)

        if received_text == "Greater Than":
            self.make_icon_tool("greater", dest_widget)

        if received_text == "Greater Than / Equal to":
            self.make_icon_tool("great-equal", dest_widget)

        if received_text == "If":
            label_name = "If"

            tool_widget = Gtk.Grid()
            drag_widget = Gtk.Button()

            tool_widget.attach(drag_widget, 0, 0, 1, 1)
            self.generic_connection(drag_widget)

            self.make_if_tool(label_name, dest_widget, tool_widget)
        
        if received_text == "If / else":
            label_name = "If"
            tool_widget = Gtk.Grid()
            
            drag_widget = Gtk.Button()
            tool_widget.attach(drag_widget, 0, 0, 1, 1)
            self.generic_connection(drag_widget)
            
            self.make_if_else_tool(label_name, dest_widget, tool_widget)

        if received_text == "Number":
            label_name = "Integer"
            adjustment = Gtk.Adjustment(value=0,
                                    lower=-99999999999999999999999999999999,
                                    upper=99999999999999999999999999999999,
                                    step_increment=1,
                                    page_increment=5,
                                    page_size=0)
            tool_widget = Gtk.SpinButton(adjustment=adjustment)
            tool_widget.set_name("integer")

            self.make_labelled_tool(label_name, dest_widget, tool_widget)

        if received_text == "By Column Number":
            label_name = "Get value from column number:"
            adjustment = Gtk.Adjustment(value=0,
                                    lower=-99999999999999999999999999999999,
                                    upper=99999999999999999999999999999999,
                                    step_increment=1,
                                    page_increment=5,
                                    page_size=0)
            tool_widget = Gtk.SpinButton(adjustment=adjustment)
            tool_widget.set_name("by-col-num")

            self.make_labelled_tool(label_name, dest_widget, tool_widget)

        if received_text == "String":
            label_name = "Text"
            tool_widget = Gtk.Entry()
            tool_widget.set_name("string")

            self.make_labelled_tool(label_name, dest_widget, tool_widget)

        if received_text == "By Column Name":
            label_name = "Get value from column named:"
            tool_widget = Gtk.Entry()
            tool_widget.set_name("by-col-name")

            self.make_labelled_tool(label_name, dest_widget, tool_widget)

    def make_icon_tool(self, icon_name, dest_widget):
        widget = Gtk.Image.new_from_icon_name(icon_name, 5)

        box = Gtk.Grid()
        box.set_name(icon_name)
        box_enclosure = Gtk.Box()

        parent_grid = dest_widget.get_ancestor(Gtk.Grid())

        # Clear Button
        image = Gtk.Image()
        image.set_from_icon_name('edit-clear', Gtk.IconSize.BUTTON)
        clear_btn = Gtk.Button()
        clear_btn.set_relief(Gtk.ReliefStyle.NONE)
        clear_btn.add(image)
        clear_btn.connect('clicked', self.del_component)
        
        box.attach(clear_btn, 0, 0, 1, 1)
        box.attach(widget, 0, 1, 1, 1)
        parent_grid.insert_next_to(dest_widget, 0)
        box_enclosure.add(box)
        parent_grid.attach_next_to(box_enclosure, dest_widget, 0, 1, 1)
        dest_widget.destroy()
        
        # Insert new blank placeholders
        front_blank = Gtk.Button()
        self.generic_connection(front_blank)
        parent_grid.insert_next_to(box_enclosure, 0)
        parent_grid.attach_next_to(front_blank, box_enclosure, 0, 1, 1)

        back_blank = Gtk.Button()
        self.generic_connection(back_blank)
        parent_grid.insert_next_to(box_enclosure, 1)
        parent_grid.attach_next_to(back_blank, box_enclosure, 1, 1, 1)

        self.show_all()

    def make_labelled_tool(self, label_name, dest_widget, widget):
        label = Gtk.Label()
        label.set_label(label_name)

        box = Gtk.Grid()
        box.set_name(label_name)
        box_enclosure = Gtk.Box()

        parent_grid = dest_widget.get_ancestor(Gtk.Grid())

        # Clear Button
        image = Gtk.Image()
        image.set_from_icon_name("edit-clear", Gtk.IconSize.BUTTON)
        clear_btn = Gtk.Button()
        clear_btn.set_relief(Gtk.ReliefStyle.NONE)
        clear_btn.add(image)
        clear_btn.connect('clicked', self.del_component)
        
        box.attach(label, 0, 0, 3, 1)
        box.attach(clear_btn, 3, 0, 1, 1)
        box.attach(widget, 0, 1, 4, 1)
        parent_grid.insert_next_to(dest_widget, 0)
        box_enclosure.add(box)
        parent_grid.attach_next_to(box_enclosure, dest_widget, 0, 1, 1)
        dest_widget.destroy()

        # Insert new blank placeholders
        front_blank = Gtk.Button()
        self.generic_connection(front_blank)
        parent_grid.insert_next_to(box_enclosure, 0)
        parent_grid.attach_next_to(front_blank, box_enclosure, 0, 1, 1)

        back_blank = Gtk.Button()
        self.generic_connection(back_blank)
        parent_grid.insert_next_to(box_enclosure, 1)
        parent_grid.attach_next_to(back_blank, box_enclosure, 1, 1, 1)

        self.show_all()

    def make_if_tool(self, label_name, dest_widget, widget):
        label = Gtk.Label()
        label.set_markup(f"<big><b>{label_name}</b></big>")

        then_label = Gtk.Label()
        then_label.set_markup(f"<big><b> ; Then</b></big>")

        frame = Gtk.Frame()
        box = Gtk.Grid()
        box.set_column_spacing(10)
        box_enclosure = Gtk.Box()
        frame.set_name("if")
        parent_grid = dest_widget.get_ancestor(Gtk.Grid())

        tool_widget = Gtk.Grid()
        tool_widget.set_name("then-section")
        drag_widget = Gtk.Button()
        self.generic_connection(drag_widget)
        tool_widget.attach(drag_widget, 0, 0, 1, 1)

        # Clear Button
        image = Gtk.Image()
        image.set_from_icon_name("edit-clear", Gtk.IconSize.BUTTON)
        clear_btn = Gtk.Button()
        clear_btn.set_relief(Gtk.ReliefStyle.NONE)
        clear_btn.add(image)
        clear_btn.connect('clicked', self.del_component)

        box.attach(label, 0, 1, 3, 1)
        box.attach(clear_btn, 3, 0, 1, 1)
        widget.set_name("if-section")
        box.attach(widget, 3, 1, 4, 1)
        box.attach(then_label, 7, 1, 1, 1)
        box.attach(tool_widget, 9, 1, 4, 1)

        parent_grid.insert_next_to(dest_widget, 0)
        frame.add(box)
        box_enclosure.add(frame)
        parent_grid.attach_next_to(box_enclosure, dest_widget, 0, 1, 1)
        dest_widget.destroy()

        # Insert new blank placeholders
        front_blank = Gtk.Button()
        self.generic_connection(front_blank)
        parent_grid.insert_next_to(box_enclosure, 0)
        parent_grid.attach_next_to(front_blank, box_enclosure, 0, 1, 1)

        back_blank = Gtk.Button()
        self.generic_connection(back_blank)
        parent_grid.insert_next_to(box_enclosure, 1)
        parent_grid.attach_next_to(back_blank, box_enclosure, 1, 1, 1)

        self.show_all()

    def make_if_else_tool(self, label_name, dest_widget, widget):
        label = Gtk.Label()
        label.set_markup(f"<big><b>{label_name}</b></big>")

        then_label = Gtk.Label()
        then_label.set_markup(f"<big><b> ; Then</b></big>")

        else_label = Gtk.Label()
        else_label.set_markup(f"<big><b> ; Else</b></big>")

        frame = Gtk.Frame()
        frame.set_name("if-else")
        box = Gtk.Grid()
        box.set_column_spacing(10)
        box_enclosure = Gtk.Box()

        parent_grid = dest_widget.get_ancestor(Gtk.Grid())

        tool_widget = Gtk.Grid()
        tool_widget.set_name("then-section")
        drag_widget = Gtk.Button()
        self.generic_connection(drag_widget)
        tool_widget.attach(drag_widget, 0, 0, 1, 1)

        tool_widget_2 = Gtk.Grid()
        tool_widget_2.set_name("else-section")
        drag_widget_2 = Gtk.Button()
        self.generic_connection(drag_widget_2)
        tool_widget_2.attach(drag_widget_2, 0, 0, 1, 1)

        # Clear Button
        image = Gtk.Image()
        image.set_from_icon_name("edit-clear", Gtk.IconSize.BUTTON)
        clear_btn = Gtk.Button()
        clear_btn.set_relief(Gtk.ReliefStyle.NONE)
        clear_btn.add(image)
        clear_btn.connect('clicked', self.del_component)

        box.attach(label, 0, 1, 3, 1)
        box.attach(clear_btn, 3, 0, 1, 1)
        widget.set_name("if-section")
        box.attach(widget, 3, 1, 4, 1)
        box.attach(then_label, 7, 1, 1, 1)
        box.attach(tool_widget, 9, 1, 4, 1)

        box.attach(else_label, 14, 1, 1, 1)
        box.attach(tool_widget_2, 16, 1, 4, 1)

        parent_grid.insert_next_to(dest_widget, 0)
        frame.add(box)
        box_enclosure.add(frame)
        parent_grid.attach_next_to(box_enclosure, dest_widget, 0, 1, 1)
        dest_widget.destroy()

        # Insert new blank placeholders
        front_blank = Gtk.Button()
        self.generic_connection(front_blank)
        parent_grid.insert_next_to(box_enclosure, 0)
        parent_grid.attach_next_to(front_blank, box_enclosure, 0, 1, 1)

        back_blank = Gtk.Button()
        self.generic_connection(back_blank)
        parent_grid.insert_next_to(box_enclosure, 1)
        parent_grid.attach_next_to(back_blank, box_enclosure, 1, 1, 1)

        self.show_all()

    def generic_connection(self, widget):

        widget.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        widget.drag_dest_add_text_targets()
        widget.connect("drag-data-received", self.on_drag_data_received)

    def del_component(self, del_btn):
        parent_widget = del_btn.get_ancestor(Gtk.Box)
        master_grid = parent_widget.get_ancestor(Gtk.Grid)
        col = master_grid.child_get_property(parent_widget, 'left-attach')
        col = col + 1
        extra_blank = master_grid.get_child_at(col, 0)

        for widget in parent_widget.get_children():
            widget.destroy()
        
        extra_blank.destroy()
        if self.on_update:
            self.on_update()

class EventBuilderWindow(Gramplet):

    def init(self):

        """
        GUI setup
        """
        # Append icon directory to the theme search path
        theme = Gtk.IconTheme.get_default()
        theme.append_search_path(os.path.join(os.path.dirname(__file__), 
                                           "Icons"))

        # Add components to grid layout
        grid = Gtk.Grid()
        box = Gtk.HBox()

        # Add Labels
        event_template_label = Gtk.Label()
        event_template_label.set_label("Event Template Name")
        event_template_label.set_name("Template Label")

        type_label = Gtk.Label()
        type_label.set_label("Event Type")
        type_label.set_name("Type Label")

        # Add Entry Boxes
        event_template_entry = Gtk.Entry()

        # Add Combo Boxes
        column_dropdown = Gtk.ComboBox(has_entry=True, 
                                       margin=3)
        
        column_dropdown_events = EventMenuWidget(obj=column_dropdown,
                                                custom_values=self.get_custom_events()).obj
        
        column_dropdown_events.set_name("Event Dropdown")

        # Attach Labels
        grid.attach(event_template_label, 0, 0, 1, 1)
        grid.attach(type_label, 0, 1, 1, 1)

        # Attach Entry
        grid.attach(event_template_entry, 1, 0, 1, 1)

        # Attach Combobox
        grid.attach(column_dropdown_events, 1, 1, 1, 1)

        """
        Editor Area
        """
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)

        date_grid_dest = DropArea()
        stack.add_titled(date_grid_dest, "DateGrid", "Date")

        desc_grid_dest = DropArea()
        stack.add_titled(desc_grid_dest, "DescGrid", "Description")

        place_grid_dest = DropArea()
        stack.add_titled(place_grid_dest, "PlaceGrid", "Place")

        role_grid_dest = DropArea()
        stack.add_titled(role_grid_dest, "RoleGrid", "Role")

        self.date_grid_dest = date_grid_dest
        self.desc_grid_dest = desc_grid_dest
        self.place_grid_dest = place_grid_dest
        self.role_grid_dest = role_grid_dest

        self.date_grid_dest.on_update = self.update_text_labels
        self.desc_grid_dest.on_update = self.update_text_labels
        self.place_grid_dest.on_update = self.update_text_labels
        self.role_grid_dest.on_update = self.update_text_labels

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)

        vbox.pack_start(stack_switcher, False, False, 0)
        vbox.pack_start(stack, False, False, 0)

        # Add Save Button
        self.ExtractData = DroppedDataExtractor(date_grid_dest)
        save_btn = Gtk.Button(label = "Save")
        save_btn.connect('clicked', self.ExtractData.save_full_config)
        grid.attach(save_btn, 0, 2, 1, 1)

        # Add Load Button
        load_btn = Gtk.Button(label = "Load")
        load_btn.connect('clicked', self.rebuild_events)
        grid.attach(load_btn, 0, 3, 1, 1)

        # Add description editor window
        desc_editor = self.build_description_editor()

        # Add Tool Palette
        tool_palette_container = Gtk.Frame()
        tool_palette_container.set_name("Palette Container")

        tool_palette = Gtk.ToolPalette()
        tool_palette.set_name("Tool Palette")
        palette_style = Gtk.ToolbarStyle(2)
        tool_palette.set_style(palette_style)

        """
        Variable Tools
        """

        # Variable Group
        variable_group = Gtk.ToolItemGroup(label="Variables")
        variable_group.set_name("Variable Palette")

        # String Variable
        string_var = Gtk.ToolButton()
        string_var.set_label("String")
        string_var.set_icon_name("gramps-font")
        string_var.set_use_drag_window(True)
        self.enable_drag(string_var, "gramps-font")
        variable_group.add(string_var)

        # Number Variable
        num_var = Gtk.ToolButton()
        num_var.set_label("Number")
        num_var.set_icon_name("accessories-calculator")
        num_var.set_use_drag_window(True)
        self.enable_drag(num_var, "accessories-calculator")
        variable_group.add(num_var)

        """
        Column Tools
        """
        # Column Variables Group
        col_group = Gtk.ToolItemGroup(label="Column Value Extractors")
        col_group.set_name("Column Palette")

        # Column by Name
        col_name = Gtk.ToolButton()
        col_name.set_label("By Column Name")
        col_name.set_icon_name("column-name")
        col_name.set_use_drag_window(True)
        self.enable_drag(col_name, "column-name")
        col_group.add(col_name)

        # Column by Number
        col_num = Gtk.ToolButton()
        col_num.set_label("By Column Number")
        col_num.set_icon_name("column-num")
        col_num.set_use_drag_window(True)
        self.enable_drag(col_num, "column-num")
        col_group.add(col_num)

        """
        Mathematical Operation Tools
        """

        # Mathematical Operations Group
        math_group = Gtk.ToolItemGroup(label="Mathematical Operations")
        math_group.set_name("Math Palette")

        # Addition
        addition = Gtk.ToolButton()
        addition.set_label("Plus")
        addition.set_icon_name("plus")
        addition.set_use_drag_window(True)
        self.enable_drag(addition, "plus")
        math_group.add(addition)

        # Subtraction
        subtraction = Gtk.ToolButton()
        subtraction.set_label("Minus")
        subtraction.set_icon_name("minus")
        subtraction.set_use_drag_window(True)
        self.enable_drag(subtraction, "minus")
        math_group.add(subtraction)

        # Multiplication
        multiplication = Gtk.ToolButton()
        multiplication.set_label("Times")
        multiplication.set_icon_name("times")
        multiplication.set_use_drag_window(True)
        self.enable_drag(multiplication, "times")
        math_group.add(multiplication)

        # Division
        divide = Gtk.ToolButton()
        divide.set_label("Divide")
        divide.set_icon_name("divide")
        divide.set_use_drag_window(True)
        self.enable_drag(divide, "divide")
        math_group.add(divide)

        """
        Comparator Tools
        """
        # Comparators Group
        comp_group = Gtk.ToolItemGroup(label="Comparators")
        comp_group.set_name("Comparator Palette")

        # Equal
        equal = Gtk.ToolButton()
        equal.set_label("Equal")
        equal.set_icon_name("equal")
        equal.set_use_drag_window(True)
        self.enable_drag(equal, "equal")
        comp_group.add(equal)

        # Not Equal
        n_equal = Gtk.ToolButton()
        n_equal.set_label("Not Equal")
        n_equal.set_icon_name("not-equal-to")
        n_equal.set_use_drag_window(True)
        self.enable_drag(n_equal, "not-equal-to")
        comp_group.add(n_equal)

        # Less Than
        less_than = Gtk.ToolButton()
        less_than.set_label("Less Than")
        less_than.set_icon_name("less")
        less_than.set_use_drag_window(True)
        self.enable_drag(less_than, "less")
        comp_group.add(less_than)

        # Greater Than
        great_than = Gtk.ToolButton()
        great_than.set_label("Greater Than")
        great_than.set_icon_name("greater")
        great_than.set_use_drag_window(True)
        self.enable_drag(great_than, "greater")
        comp_group.add(great_than)

        # Less Than or Equal
        less_equal = Gtk.ToolButton()
        less_equal.set_label("Less Than / Equal to")
        less_equal.set_icon_name("less-equal")
        less_equal.set_use_drag_window(True)
        self.enable_drag(less_equal, "less-equal")
        comp_group.add(less_equal)

        # Less Than or Equal
        great_equal = Gtk.ToolButton()
        great_equal.set_label("Greater Than / Equal to")
        great_equal.set_icon_name("great-equal")
        great_equal.set_use_drag_window(True)
        self.enable_drag(great_equal, "great-equal")
        comp_group.add(great_equal)

        """
        Logical Operator Tools
        """
        # Logical Operator Group
        logic_group = Gtk.ToolItemGroup(label="Logic")
        logic_group.set_name("Logic Palette")

        # If x Then y
        if_then = Gtk.ToolButton()
        if_then.set_label("If")
        if_then.set_icon_name("if-statement")
        if_then.set_use_drag_window(True)
        self.enable_drag(if_then, "if-statement")
        logic_group.add(if_then)

        # If - Else
        if_else = Gtk.ToolButton()
        if_else.set_label("If / else")
        if_else.set_icon_name("if-else")
        if_else.set_use_drag_window(True)
        self.enable_drag(if_else, "if-else")
        logic_group.add(if_else)

        tool_palette.add(variable_group)
        tool_palette.add(col_group)
        tool_palette.add(math_group)
        tool_palette.add(comp_group)
        tool_palette.add(logic_group)

        tool_palette_container.add(tool_palette)


        # Add labels for text and error representation
        self.date_text_label = Gtk.Label(label="Date: ")
        self.date_error_label = Gtk.Label(label="Date Error: ")

        self.desc_text_label = Gtk.Label(label="Description: ")
        self.desc_error_label = Gtk.Label(label="Description Error: ")

        self.place_text_label = Gtk.Label(label="Place: ")
        self.place_error_label = Gtk.Label(label="Place Error: ")

        self.role_text_label = Gtk.Label(label="Role: ")
        self.role_error_label = Gtk.Label(label="Role Error: ")

        # Container for labels
        text_label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        text_label_box.pack_start(self.date_text_label, False, False, 0)
        text_label_box.pack_start(self.date_error_label, False, False, 0)

        text_label_box.pack_start(self.desc_text_label, False, False, 0)
        text_label_box.pack_start(self.desc_error_label, False, False, 0)

        text_label_box.pack_start(self.place_text_label, False, False, 0)
        text_label_box.pack_start(self.place_error_label, False, False, 0)

        text_label_box.pack_start(self.role_text_label, False, False, 0)
        text_label_box.pack_start(self.role_error_label, False, False, 0)

        # Setup container
        scrolled_window = self.gui.get_container_widget()

        for widget in scrolled_window.get_children():
            widget.destroy()

        box.add(grid)
        box.add(vbox)
        box.add(tool_palette_container)
        box.pack_start(text_label_box, False, False, 0)

        scrolled_window.add(box)
        scrolled_window.show_all()

        # Initial update
        self.update_text_labels()

    def update_text_labels(self, *args):
        # Extract and update text for each section using DropAreaTextExtractor
        date_dict = self.date_grid_dest.ExtractData.iter_widgets(self.date_grid_dest)
        desc_dict = self.desc_grid_dest.ExtractData.iter_widgets(self.desc_grid_dest)
        place_dict = self.place_grid_dest.ExtractData.iter_widgets(self.place_grid_dest)
        role_dict = self.role_grid_dest.ExtractData.iter_widgets(self.role_grid_dest)

        date_text = DropAreaTextExtractor(date_dict).text_representation
        date_error_text = DropAreaTextExtractor(date_dict).error_representation

        desc_text = DropAreaTextExtractor(desc_dict).text_representation
        desc_error_text = DropAreaTextExtractor(desc_dict).error_representation

        place_text = DropAreaTextExtractor(place_dict).text_representation
        place_error_text = DropAreaTextExtractor(place_dict).error_representation

        role_text = DropAreaTextExtractor(role_dict).text_representation
        role_error_text = DropAreaTextExtractor(role_dict).error_representation

        self.date_text_label.set_text(f"Date: {date_text}")
        self.desc_text_label.set_text(f"Description: {desc_text}")
        self.place_text_label.set_text(f"Place: {place_text}")
        self.role_text_label.set_text(f"Role: {role_text}")

        self.date_error_label.set_text(f"Date Error: {date_error_text}")
        self.desc_error_label.set_text(f"Description Error: {desc_error_text}")
        self.place_error_label.set_text(f"Place Error: {place_error_text}")
        self.role_error_label.set_text(f"Role Error: {role_error_text}")

    def get_custom_events(self):
        return sorted(self.dbstate.db.get_event_types(), key=lambda s: s.lower())
    
    def build_description_editor(self):
        desc_editor = Gtk.HBox()

        return desc_editor
    
    def enable_drag(self, tool_item=None, icon_name=None):
        """
        Enable self as a drag source.
        """
        drag_data_get = self.drag_data_get
        if tool_item:
            tool_item.drag_source_set(
                Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY
            )
            
            tool_item.drag_source_set_icon_name(icon_name)
            tool_item.drag_source_add_text_targets()
            tool_item.connect("drag_data_get", drag_data_get)

    def drag_data_get(
        self, _dummy_widget, _dummy_context, data, info, _dummy_time
    ):
        """
        Return requested data.
        """
        data.set_text(_dummy_widget.get_label(),-1)

    # Load Saved Configuration
    def load_config_file(self, filename):
        with open(filename, 'r') as f:
            j_data = json.load(f)
            return j_data


    def rebuild_events(self, btn):
        
        # Load Config File
        config_path = os.path.join(os.path.dirname(__file__), 'testsave.txt')
        j_data = self.load_config_file(config_path)

        """
        Get Stack Widget
        """
        scrolled_window = self.gui.get_container_widget()
        viewport =  scrolled_window.get_children()[0]
        h_box = viewport.get_children()[0]
        box = self.get_child_by_name(h_box, "GtkBox")
        stack = self.get_child_by_name(box, "GtkStack")

        for window in j_data.keys():

            if window == "DescGrid":
                drop_slide = self.desc_grid_dest
            elif window == "DateGrid":
                drop_slide = self.date_grid_dest
            elif window == "RoleGrid":
                drop_slide = self.role_grid_dest
            elif window == "PlaceGrid":
                drop_slide = self.place_grid_dest

            stack.set_visible_child_name(window)
            scrolled_window.show_all()

            # Get window widget
            slide = stack.get_visible_child()
            for child in slide.get_children():
                
                if child.get_name() == "GtkBox":
                    for component in child.get_children():
                        for element in component.get_children():

                            # Remove existing widgets from slide
                            if element.get_name() == "GtkButton":
                                self.del_component(element)

                            if element.get_name() == "GtkGrid":
                                del_button = self.get_child_by_name(element, "GtkButton")
                                self.del_component(del_button)

                scrolled_window.show_all()

            # Add elements from saved config to gui
            slide_data = j_data[window]
            drop_button = self.get_child_by_name(slide, "GtkButton")
            drop_grid = drop_button.get_parent()
            print(type(drop_grid))

            self.add_events_from_layer(slide_data, drop_grid, scrolled_window, drop_slide)
            scrolled_window.show_all()

    def add_events_from_layer(self, layer, drop_grid, scrolled_window, drop_slide, parent_section=None):
        """
        Recursively add events from saved configuration layer
        
        Args:
            layer (dict): Layer of event configuration to process
            drop_grid (Gtk.Grid): Grid to add widgets to 
            scrolled_window (Gtk.ScrolledWindow): Main window
            drop_slide (DropArea): Drop area for the current section
            parent_section (str): Name of parent section (if/then) being processed
        """
        if drop_grid is None:
            print("Warning: drop_grid is None")
            return

        # Get number of elements
        total = len(layer.keys())
        print(f"Processing layer with {total} elements")
        print(f"Current parent_section: {parent_section}")

        # Iterate through elements 
        for i in range(total):
            widget_data = layer[str(i)]
            print(f"Processing widget_data: {widget_data}")

            if parent_section:
                # If we're in a section, get the grid based on section name
                if parent_section == "if-section":
                    target_grid = self.find_section_grid(drop_grid, "if-section")
                elif parent_section == "then-section":
                    target_grid = self.find_section_grid(drop_grid, "then-section")
                else:
                    target_grid = drop_grid
            else:
                target_grid = drop_grid

            if target_grid is None:
                print(f"Warning: Could not find target grid for section {parent_section}")
                continue

            # Get Widget Type and handle different data structures
            if isinstance(widget_data, list):
                widget_name = widget_data[0]
                if widget_name == "Text":
                    widget_name = "String"

                if widget_name == "Integer":
                    widget_name = "Number"

                dest_button = target_grid.get_child_at(i + i, 0)
                print(dest_button)

            elif isinstance(widget_data, str):
                widget_name = widget_data

                if widget_name == "plus":
                    widget_name = "Plus"

                if widget_name == "equal":
                    widget_name = "Equal"

                if widget_name == "minus":
                    widget_name = "Minus"

                if widget_name == "times":
                    widget_name = "Times"

                if widget_name == "divide":
                    widget_name = "Divide"

                dest_button = target_grid.get_child_at(i + i, 0)
                print(dest_button)

            elif isinstance(widget_data, dict):
                widget_name = list(widget_data.keys())[0]  # This will be 'if'
                if widget_name == "if":
                    display_name = "If"
                    dest_button = target_grid.get_child_at(i + i, 0)
                    
                    print(f"Building If widget at position {i}")
                    # Build the if widget first
                    DropArea.build_widget(drop_slide, display_name, dest_button)
                    scrolled_window.show_all()

                    # Find the newly created if widget's frame and box
                    if_frame = self.find_if_frame(target_grid)
                    if if_frame:
                        print("Found if frame")
                        # Get the main grid inside the frame
                        box = if_frame.get_child()
                        if box and isinstance(box, Gtk.Grid):
                            # Process if-section
                            if_data = widget_data[widget_name].get("if-section", {})
                            print("Processing if-section")
                            self.add_events_from_layer(if_data, box, 
                                                    scrolled_window, drop_slide, "if-section")

                            # Process then-section
                            then_data = widget_data[widget_name].get("then-section", {})
                            print("Processing then-section")
                            self.add_events_from_layer(then_data, box,
                                                    scrolled_window, drop_slide, "then-section")
                    else:
                        print("Warning: Could not find if frame")
                    
                    continue  # Skip the normal widget building since we handled it specially

                else:
                    dest_button = target_grid.get_child_at(i + i, 0)

            if dest_button is None:
                print(f"Warning: Could not find destination button at position {i}")
                continue

            print(f"Building widget {widget_name}")
            
            # Build the widget
            DropArea.build_widget(drop_slide, widget_name, dest_button)
            scrolled_window.show_all()

    def find_section_grid(self, container, section_name):
        """
        Find the grid for a specific section based on the widget name
        """
        print(f"Looking for section grid: {section_name}")
        if isinstance(container, Gtk.Grid):
            for child in container.get_children():
                if isinstance(child, Gtk.Grid) and child.get_name() == section_name:
                    return child
                # Also check inside the grid
                if isinstance(child, Gtk.Grid):
                    result = self.find_section_grid(child, section_name)
                    if result:
                        return result
        return None

    def find_if_frame(self, container):
        """
        Find the Frame widget that contains the if/then structure
        """
        if isinstance(container, Gtk.Grid):
            for child in container.get_children():
                if isinstance(child, Gtk.Box):
                    for box_child in child.get_children():
                        if isinstance(box_child, Gtk.Frame) and box_child.get_name() == "if":
                            return box_child
        return None

    def get_section_grid(self, parent_box, section_name):
        """
        Get the grid for a specific section (if/then) from the parent box
        
        Args:
            parent_box (Gtk.Box): Parent box containing the sections
            section_name (str): Name of section to find ("if-section" or "then-section")
            
        Returns:
            Gtk.Grid: Grid for the specified section
        """
        if parent_box is None:
            print("Warning: parent_box is None in get_section_grid")
            return None

        for child in parent_box.get_children():
            if isinstance(child, Gtk.Frame) and child.get_label() == section_name:
                grid = child.get_child()
                if grid is None:
                    print(f"Warning: No grid found in {section_name} frame")
                return grid
        print(f"Warning: No frame found with label {section_name}")
        return None
    
    def get_child_by_name(self, widget, name):
        for child in widget.get_children():
            if child.get_name() == name:
                return child
            
    def del_component(self, del_btn):
        parent_widget = del_btn.get_ancestor(Gtk.Box)
        master_grid = parent_widget.get_ancestor(Gtk.Grid)
        col = master_grid.child_get_property(parent_widget, 'left-attach')
        col = col + 1
        extra_blank = master_grid.get_child_at(col, 0)

        for widget in parent_widget.get_children():
            widget.destroy()
        
        extra_blank.destroy()