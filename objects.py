from vm import vm

GID = 0

def nextid():
    global GID
    GID += 1
    return GID

DEBUG = True

def dprint(*args, **kwargs):
    if DEBUG:
        if kwargs == {}:
            print(*args)
        else:
            print(*args, kwargs)

class MUDObject:
    def __init__(self, *args, **kwargs):
        self.id = nextid()
        dprint(f"Created object #{self.id}")

        self.key = None#Key(self.id)

        self.name = kwargs.get("name")

        self.location = None
        self.move(kwargs.get("location"))

        self.contents = kwargs.get("contents", [])

        if hasattr(self, "init"):
            self.init(*args, **kwargs)

    # TODO __repr__ with name etc.

    def move(self, newlocation):
        if self.location is not None:
            self.location.contents.remove(self)

        self.location = newlocation

        if newlocation is not None:
            newlocation.contents.append(self)

class ActiveMUDObject(MUDObject):
    def __init__(self, *args, **kwargs):
        self.methods = {}
        super().__init__(self, *args, **kwargs)

    def execute(self, name, args):
        method = self.methods.get(name)
        vm.execute(name, args)

class World(ActiveMUDObject):
    pass

world = World()

class Player(ActiveMUDObject):
    pass

def new_player(name):
    return Player(name=name, location=world)

new_player("coda")

print(world.contents)

def all_objects(root=world):
    objects = []
    queue = [root]
    while len(queue) > 0:
        obj = queue.pop(0)
        objects.append(obj)
        queue += obj.contents
    return objects

print(all_objects())
