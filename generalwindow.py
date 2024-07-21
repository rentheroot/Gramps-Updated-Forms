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
from gi.repository import Gtk
from gramps.gen.plug import Gramplet
from gramps.gui.editors.editevent import EditEvent
from eventmenu import EventMenuWidget
from form import Form
import os
from guibuilder import GuiBuilder
from templatehandler import HandleTemplate
import json

class WindowGramplet(Gramplet):

    def init(self):

        """
        GUI setup
        """
        # Instantiate GuiBuilder
        self.GuiComponents = GuiBuilder(self.dbstate)

        # Instantiate Template Handling
        self.TemplateHandler = HandleTemplate()

        # List of form files
        forms_path = os.path.join(os.path.dirname(__file__), 
                                  "Forms")
        
        form_files = [f for f in os.listdir(forms_path) if os.path.isfile(os.path.join(forms_path, f))]

        # Dynamic sizing
        adaptive_height = len(form_files)

        """
        Template buttons
        """
        # Layout options
        bBox = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        bBox.set_spacing(5)

        # Create buttons
        new_btn = Gtk.Button(label="New")
        new_btn.connect('clicked', self.new_template)

        # Group buttons
        bBox.pack_start(new_btn, False, False, 0)

        tree_view, adaptive_height, self.stacked_options = self.GuiComponents.\
            formid_selector_builder(form_files,
                                    adaptive_height)

        """
        Setup treeviews
        """
        renderer = Gtk.CellRendererText()
        
        # Add columns
        column = Gtk.TreeViewColumn("Title", 
                                    renderer, 
                                    text=0)
        
        column.set_sort_column_id(0)
        tree_view.append_column(column)

        # Handle file selection
        select = tree_view.get_selection()
        select.connect("changed", 
                        self.on_tree_selection_changed)
        
        # Make tree_view scrollable
        scroll_forms = Gtk.ScrolledWindow()
        scroll_forms.add(tree_view)
        scroll_forms.set_policy(Gtk.PolicyType.NEVER, 
                                Gtk.PolicyType.AUTOMATIC)

        # Add components to grid layout
        grid = Gtk.Grid()
        grid.insert_column(0)
        grid.insert_column(0)
        grid.attach(scroll_forms, 
                    left=0, 
                    top=0, 
                    width=2, 
                    height=3)

        self.add_default_settings_folders()

        # Make template_view scrollable
        scroll_template = Gtk.ScrolledWindow()
        scroll_template.add(self.templates_tree_view)
        scroll_template.set_policy( Gtk.PolicyType.NEVER, 
                                    Gtk.PolicyType.AUTOMATIC)

        grid.attach(scroll_template, 
                    left=3, 
                    top=0, 
                    width=1, 
                    height=1)
        
        grid.attach(bBox, 
                    left=3, 
                    top=1, 
                    width=1, 
                    height=1)
        
        grid.add(self.stacked_options)

        # Setup container
        scrolled_window = self.gui.get_container_widget()

        for widget in scrolled_window.get_children():
            widget.destroy()

        scrolled_window.add(grid)
        
        scrolled_window.show_all()
        self.stacked_options.hide()
    
    # Swap Gui window to match selected form
    def on_tree_selection_changed(self, selection):

        model, treeiter = selection.get_selected()

        if treeiter is not None \
                        and '.xml' not in \
                        model[treeiter][0]:
            
            # Select Grid
            window = self.gui.get_container_widget()\
                .get_children()[0]\
                .get_children()[0]
            
            form_id = model[treeiter][0]
            self.visible_form = form_id

            # Load Template Names
            self.add_default_settings_folders(form_id)

            # Remove all comboboxes
            self.recursive_destroy(window)
        
        self.stacked_options.hide()

    def on_template_file_changed(self, selection):

        selection = selection.get_selection()

        model, treeiter = selection.get_selected()

        if treeiter is not None:

            self.stacked_options.show()
            self.stacked_options.set_visible_child_name(self.visible_form)

            selected = model[treeiter][0] + '.json'

            # Select Grid
            window = self.gui.get_container_widget()
            window = window.get_children()[0]
            window = window.get_children()[0]

            # Remove all comboboxes
            self.recursive_destroy(window)

            form_id = self.stacked_options.get_visible_child_name()

            self.GuiComponents.load_template_file(form_id=form_id,
                                                template_name=selected,
                                                settings_window=window, 
                                                template_builder=self.TemplateHandler)
        else:

            # Select Grid
            window = self.gui.get_container_widget()
            window = window.get_children()[0]
            window = window.get_children()[0]

            self.recursive_destroy(window)

    def on_template_file_created(self, settings):

        self.stacked_options.show()
        self.stacked_options.set_visible_child_name(self.visible_form)

        # Select Grid
        window = self.gui.get_container_widget()
        window = window.get_children()[0]
        window = window.get_children()[0]

        # Remove all comboboxes
        self.recursive_destroy(window)

        self.GuiComponents.populate_template(settings_window=window, 
                                            template_builder=self.TemplateHandler,
                                            settings=settings)
            
    def recursive_destroy(self, parent):

        for child in parent.get_children():
            if child.get_name()=="GtkComboBox" or child.get_name()=="TemplateOptions":
                child.destroy()

            else:
                if hasattr(child, "get_children"):
                    self.recursive_destroy(child)

    # Add Templates to selection options
    def add_default_settings_folders(self, form_id=None):

        if form_id is not None:
             
             self.templates_model.clear()
             template_paths = os.path.join(os.path.dirname(__file__), 
                                           "Forms", 
                                           "Templates", 
                                           form_id)
             
             templates = os.listdir(template_paths)
             
             for template in templates:
                
                template = template.replace('.json','')
                self.templates_model.append(None,[template])

        else:
            self.templates_model = Gtk.TreeStore(str)

        """
        Setup treeview
        """
        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)

        # Add columns
        column = Gtk.TreeViewColumn("Template Files", 
                                    renderer, 
                                    text=0)
        
        column.set_sort_column_id(0)

        self.templates_tree_view = Gtk.TreeView(model=self.templates_model)
        self.templates_tree_view.append_column(column)

        # Handle file selection
        select = self.templates_tree_view
        selector = select.get_selection()
        selector.unselect_all()
        select.connect("cursor-changed", self.on_template_file_changed)

        # Handle file name edited
        renderer.connect("edited", self.text_edited)

    def text_edited(self, widget, path, text):
         
        self.templates_model[path] = [text]

    def new_template(self, btn):

        # Select grid
        window = self.stacked_options

        form_id = self.visible_form
        
        settings = self.TemplateHandler.get_settings_from_form_file(form_id)

        settings = json.dumps(settings, indent=4)

        self.on_template_file_created(settings)