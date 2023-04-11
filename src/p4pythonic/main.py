import P4 as p4python

class Spec(p4python.Spec):
    pass


class P4(p4python.P4):
    def __init__(self, *args, **kwlist):
        super().__init__(*args, **kwlist)

    def get_depot(self, depot_name: str):
        if res := self.run_depot("-o", depot_name):
            return Spec(res[0])

