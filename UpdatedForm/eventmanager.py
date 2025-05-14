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
from gramps.gen.lib import (Event, Note, EventRef)
from gramps.gen.db import DbTxn

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

class ManageEvents():

    def __init__(self):

        pass

    """
    Load events from notes
    """
    def load_notes(self, master_event_ref, db, template_rules, event, trans):

        # Get note list
        note_list = master_event_ref.get_note_list()

        if len(note_list) > 0:

            # All notes of type link
            for note in note_list:
                note_obj = db.get_note_from_handle(note)
                if note_obj.get_type() == "Link":

                    linked_events = json.loads(str(note_obj.get_styledtext()))
                    note_handle = note

        else:
            empty_note = Note()
            empty_note.set(json.dumps(template_rules))
            empty_note.set_type("Link")
            empty_note.set_gramps_id(db.find_next_note_gramps_id())
            db.add_note(empty_note, trans)
            master_event_ref.set_note_list([empty_note.get_handle()])

            linked_events = template_rules
            note_handle = empty_note.get_handle()

        return linked_events, note_handle
    
    """
    Update Note
    """
    def update_note(self, db, note_handle, linked_events, trans):

        note = db.get_note_from_handle(note_handle)

        note.set(json.dumps(linked_events))

        db.commit_note(note, trans)

    """
    Update Event
    """
    def update_event(self, event_handle, value, db, trans, person, event_refs):
        
        event = db.get_event_from_handle(event_handle)
        event.set_description(value)
        db.commit_event(event, trans)
        if event_handle not in event_refs:
            event_ref = EventRef()
            event_ref.set_reference_handle(event.get_handle())
            person.add_event_ref(event_ref)

    """
    Identify Template Rules for Form
    """
    def get_template_rules(self, form_id, template_id):
        template_path = os.path.join(os.path.dirname(__file__),
                                     "Forms",
                                     "Templates",
                                     form_id,
                                     template_id)
        
        template_path = template_path + '.json'
        
        with open(template_path, 'r') as f:
            template_rules = json.load(f)

        return template_rules
    
    """
    Determine which form headings have rules attached 
    """
    def extract_rules(self, og_rules):
        parsed_rules = {}
        for k, v in og_rules.items():
            if v != []:
                parsed_rules[k] = v

        return parsed_rules
    
    """
    Determine if events have been linked or not
    """
    def get_linked_event_status(self, 
                                template_rules, 
                                note_handle, 
                                note_rules, 
                                person, 
                                db, 
                                trans, 
                                row_value_dict):

        # Any new events created?
        new_events = False

        for k, v in template_rules.items():
            if v == note_rules[k] and v != [] and row_value_dict[k]!=None:

                new_events = True

                # Create and link events
                event_type = v
                handles = []
                for e in event_type:
                    handle = self.create_linked_event(e, person, db, trans)
                    handles.append(handle)

                note_rules[k] = handles

            elif v != []:
                print(v)

        # Write new events
        if new_events:
            self.update_note(db, note_handle, note_rules, trans)


    def create_linked_event(self, event_type, person, db, trans):
        new_event = Event()
        db.add_event(new_event, trans)
        new_event.set_type(event_type)
        db.commit_event(new_event, trans)

        # return new event's handle
        return str(new_event.get_handle())



