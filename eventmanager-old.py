import os
import json

class ManageEvents():

    def __init__(self):

        pass

    """
    Get sub-events from notes
    """
    def load_connected_events(self, master_event_ref, db, person_handle):

        # Get note list
        note_list = master_event_ref.get_note_list()

        if len(note_list) > 0:
            for note in note_list:
                note_ref = db.get_note_from_handle(note)
                return note_ref.get_links()
        else:
            return []
            
    """
    Get the column the event is tracking
    """
    def map_event_to_column(self, db, event_handles):

        """
        format: 
        event_handle -> col num
        """ 
        event_to_col = {}

        if len(event_handles) > 0:
            for event_handle in event_handles:
                event_obj = db.get_event_from_handle(event_handle[3])
                attrs = event_obj.get_attribute_list()

                for attr in attrs:
                    if attr.get_type() == "Column":
                        col = attr.get_value()
                        event_to_col[event_handle[3]] = col

        return event_to_col
    
    """
    Update Existing Events
    """
    def update_events(self, db, event_to_col, connected_personal_events, heading_to_value, trans):
        for event in connected_personal_events:
            event_handle = event[3]
            event_obj = db.get_event_from_handle(event_handle)

            # Identify Column
            col_num = int(event_to_col[event_handle])

            desc = heading_to_value[col_num]

            # Update Event Description
            event_obj.set_description(desc)

            db.commit_event(event_obj, trans)

    """
    Create New Events
    """
    def create_new_events(self, 
                          event_creation_rules, 
                          connected_personal_events, 
                          headings_to_col_num, 
                          event_to_col):
        
        num_expected_events = []
        expected_columns = []

        # Count Expected Number of Connected Events
        for column, events in event_creation_rules.items():
            num_expected_events.extend(events)
            expected_columns.extend(column)

        num_expected_events = len(num_expected_events)

        # Count the Actual Number of Connected Events
        num_connected_events = len(connected_personal_events)
        print(event_to_col)

        col_num_to_headings = {v: k for k, v in headings_to_col_num.items()}
        print(col_num_to_headings)
        print(event_creation_rules)

        # Compare Number of Events
        if num_expected_events != num_connected_events:
            
            # Number of Events to Create
            to_create = num_expected_events - num_connected_events

            # Identify Missing Events
            for heading, events in event_creation_rules.items():
                if len(events) > 1:
                    pass
                else:
                    event = events[0]

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
    
