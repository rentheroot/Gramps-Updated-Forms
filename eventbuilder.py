from gi.repository import GObject
from gi.repository import Gtk, Gdk
from gramps.gen.plug import Gramplet
from gramps.gui.editors.editevent import EditEvent
from eventmenu import EventMenuWidget
from form import Form
import os
import json

class DroppedDataExtractor():

    def __init__(self, parent_widget):
        self.parent_widget = parent_widget

    def tester(self):
        for child in self.parent_widget.get_children():
            for c in child:
                layer = 0
                self.get_sub_widgets(c, layer)

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
        for i in range(0, num_children):
            try:
                child = parent_grid.get_child_at(i, 0)
                top_layer.append(child)
            except:
                pass

        # Get First Layer of Items
        settings_first_layer = []
        for i in top_layer:
            if i == None:
                pass
            else:
                children = i.get_children()
                for child in children:
                    settings_first_layer.append(child.get_name())
        
        # Start Building Settings Dictionary
        settings_dict = {}
        for n, i in enumerate(settings_first_layer):
            settings_dict[n] = i

        print(settings_dict)



    def get_grid_components(self, grid_widget, default):
        
        print(grid_widget.get_name())
        for child in grid_widget:
            
            if child.get_name() == "GtkBox":

                print(grid_widget.child_get_property(child, 'left-attach'))

                for i in child:
                    
                    if i.get_name() == "Get value from column named:":
                        name = "by-col-name"
                    elif i.get_name() == "Get value from column number:":
                        name = "by-col-num"
                    elif i.get_name() == "Integer":
                        name = "integer"
                    elif i.get_name() == "Text":
                        name = "string"
                    else:
                        name = i.get_name()

                    default[grid_widget.child_get_property(child, 'left-attach')] = name
        print(default)


class DropArea(Gtk.Grid):

    def __init__(self):
        Gtk.Grid.__init__(self)
        self.set_column_spacing(10)
        
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
        self.ExtractData.iter_widgets(self)
        

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
        
        #self.ExtractData.tester()

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
        drag_widget = Gtk.Button()
        self.generic_connection(drag_widget)
        tool_widget.attach(drag_widget, 0, 0, 1, 1)

        tool_widget_2 = Gtk.Grid()
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

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)

        vbox.pack_start(stack_switcher, False, False, 0)
        vbox.pack_start(stack, False, False, 0)

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

        # Setup container
        scrolled_window = self.gui.get_container_widget()

        for widget in scrolled_window.get_children():
            widget.destroy()

        box.add(grid)
        box.add(vbox)
        box.add(tool_palette_container)
        scrolled_window.add(box)
        
        scrolled_window.show_all()

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