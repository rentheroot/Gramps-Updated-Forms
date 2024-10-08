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

from gramps.gui.autocomp import StandardCustomSelector
from gramps.gen.lib.eventtype import EventType

class EventMenuWidget:
    def __init__(
        self,
        obj,
        readonly=False,
        custom_values=None,
    ):
        """
        Constructor for the EventMenuWidget class.

        :param obj: Existing ComboBox widget to use with has_entry=True.
        :type obj: Gtk.ComboBox
        :param custom_values: Extra values to show in the combobox. These can be
                              text of custom type, tuple with type info or
                              GrampsType class
        :type custom_values: list of str, tuple or GrampsType
        """
        self.__type = EventType()
        self.obj = obj

        val = self.get_val()

        if val:
            default = int(val)
        else:
            default = None

        map = self.get_val().get_map().copy()

        self.sel = StandardCustomSelector(
            map,
            obj,
            self.get_val().get_custom(),
            default,
            additional=custom_values,
            menu=self.get_val().get_menu(),
        )

        self.sel.set_values((int(self.get_val()), str(self.get_val())))
        self.obj.set_sensitive(not readonly)
        self.obj.connect("changed", self.on_change)

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def fix_value(self, value):
        if value[0] == self.get_val().get_custom():
            return value
        else:
            return (value[0], "")

    def update(self):
        val = self.get_val()
        if isinstance(val, tuple):
            self.sel.set_values(val)
        else:
            self.sel.set_values((int(val), str(val)))

    def on_change(self, obj):
        value = self.fix_value(self.sel.get_values())
        self.set_val(value)

    def set_val(self, the_type):
        """
        Set the type of the Event to the passed (int,str) tuple.

        :param the_type: Type to assign to the Event
        :type the_type: tuple
        """
        self.__type.set(the_type)

    def get_val(self):
        """
        Return the type of the Event.

        :returns: Type of the Event
        :rtype: tuple
        """
        return self.__type
