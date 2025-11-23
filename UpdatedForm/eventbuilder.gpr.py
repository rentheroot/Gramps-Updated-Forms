#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025 Renee Schmidt
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
#

#------------------------------------------------------------------------
#
# Form Gramplet
#
#------------------------------------------------------------------------

register(GRAMPLET,
         id = "Forms Event Builder Gramplet",
         name = _("Forms Event Builder Gramplet"),
         description = _("Gramplet interface for creating event definitions for use with the form templating gramplet."),
         status = EXPERIMENTAL,
         version = '2.0.40',
         gramps_target_version = '6.0',
         authors=["Renee Schmidt"],
         navtypes=["Person"],
         fname = "eventbuilder.py",
         gramplet = 'EventBuilderWindow',
         height = 375,
         detached_width = 510,
         detached_height = 480,
         expand = True,
         gramplet_title = _("Event Builder"),
         help_url="https://gramps.discourse.group/t/plans-to-update-forms-addon-over-the-2024-summer/5274",
         include_in_listing = True,
        )
