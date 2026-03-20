class Equipment:
    def __init__(self, eq_id, name, category, serial_number, room, status, description):
        self.eq_id = eq_id
        self.name = name
        self.category = category
        self.serial_number = serial_number
        self.room = room
        self.status = status
        self.description = description

    def to_dict(self):
        return {
            'eq_id': self.eq_id,
            'name': self.name,
            'category': self.category,
            'serial_number': self.serial_number,
            'room': self.room,
            'status': self.status,
            'description': self.description
        }

    def change_status(self, new_status):
        self.status = new_status

    def change_room(self, new_room):
        self.room = new_room


class Movement:
    def __init__(self, mov_id, eq_id, from_room, to_room, reason):
        self.mov_id = mov_id
        self.eq_id = eq_id
        self.from_room = from_room
        self.to_room = to_room
        self.reason = reason

    def to_dict(self):
        return {
            'mov_id': self.mov_id,
            'eq_id': self.eq_id,
            'from_room': self.from_room,
            'to_room': self.to_room,
            'reason': self.reason
        }


class TechIssue:
    def __init__(self, issue_id, eq_id, description, severity):
        self.issue_id = issue_id
        self.eq_id = eq_id
        self.description = description
        self.severity = severity
        self.resolved = False

    def to_dict(self):
        return {
            'issue_id': self.issue_id,
            'eq_id': self.eq_id,
            'description': self.description,
            'severity': self.severity,
            'resolved': self.resolved
        }

    def resolve(self):
        self.resolved = True