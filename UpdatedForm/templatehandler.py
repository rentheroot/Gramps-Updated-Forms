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

import os
import json
from gi.repository import GObject
from gi.repository import Gtk
from form import Form

class HandleTemplate:
    def __init__(self):
        pass
    
    # Get the settings of focused window as a JSON object
    def get_current_settings(self, settings_window):

        settings_dict = {}


        form_name = settings_window.get_visible_child_name()
        selected_form = settings_window.get_visible_child()
        selected_form = self.step_down(selected_form, "GtkViewport")
        selected_form = self.step_down(selected_form, "GtkBox")
        selected_form = self.step_down(selected_form, "GtkFrame")
        selected_form = self.step_down(selected_form, "GtkBox")

        for s in selected_form:

            if s.get_name() == "GtkFrame":

                focused = s.get_children()

                for section in focused:
                    
                    # Get Section Titles
                    if section.get_name() == "GtkLabel":

                        settings_dict[section.get_text()] = field_dict

                    # Box
                    else:
                        field_dict = {}
                        
                        for section_name in section:
                            if hasattr(section_name, "get_children"):
                                for field_box in section_name.get_children():
                                    if hasattr(field_box, "get_children"):

                                        for field in field_box.get_children():
                                                
                                            if field.get_name()=="GtkLabel":
                                                field_name = field.get_text()
                                                if field_name not in field_dict.keys():
                                                    field_dict[field_name] = []

                                            elif field.get_name()=="GtkComboBox":
                                                
                                                entry = field.get_children()[0].get_text()
                                                field_dict[field_name].append(entry)

        return(settings_dict, form_name)

    def step_down_initial(self, current):
        children = []
        for child in current.get_children():
            children.append(child)

        return(children)
    
    def step_down(self, current, obj_name=None):
        children = []

        if obj_name is None:
            for child in current:
                children.extend(child.get_children())
        else:
            for child in current:
                if child.get_name() == obj_name:
                    children.extend(child.get_children())

        return(children)
    
    def get_settings_from_form_file(self, form_id):

        settings = {}

        mappings_file = os.path.join(os.path.dirname(__file__), "form-mappings.json")

        with open(mappings_file, 'r') as f:
            form_mappings = json.load(f)
            form_file = form_mappings[form_id]

        filename = form_file

        self.formReader = Form([filename])

        """
        Add section content
        """
        sections = self.formReader.get_sections(form_id)

        # Iterate through sections
        for section in sections:

            # Get title of section
            section_title = self.formReader.get_section_title(form_id, section)

            # Get column names
            form_columns = self.formReader.get_section_columns(form_id, section)

            # Format column names
            form_columns = [i[0] for i in form_columns]
            column_dict = {}

            for col in form_columns:
                column_dict[col] = []

            settings[section_title] = column_dict

        return settings

