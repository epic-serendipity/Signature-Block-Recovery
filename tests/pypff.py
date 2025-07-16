class FakeMessage:
    def __init__(self, body, ts, ident):
        self._body = body
        self.html_body = ""
        self.client_submit_time = ts
        self.identifier = ident.to_bytes(4, "big")

    @property
    def plain_text_body(self):
        return self._body

class FakeFolder:
    def __init__(self, name, msgs, subs=None):
        self.name = name
        self._msgs = msgs
        self._subs = subs or []

    def get_number_of_sub_messages(self):
        return len(self._msgs)

    def get_sub_message(self, i):
        return self._msgs[i]

    def get_number_of_sub_folders(self):
        return len(self._subs)

    def get_sub_folder(self, i):
        return self._subs[i]


class FakePst:
    def __init__(self):
        msgs = [
            FakeMessage("Hi\n--\nJohn Doe\nEngineer", 100.0, 1),
            FakeMessage("Hello\n--\nJane Smith\nManager", 200.0, 2),
        ]
        inbox = FakeFolder("Inbox", msgs)
        self.root = FakeFolder("root", [], [inbox])

    def open(self, path):
        pass

    def get_root_folder(self):
        return self.root


def file():
    return FakePst()
