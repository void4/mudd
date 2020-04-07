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

        self.name = kwargs.get("name", "???")
        self.description = kwargs.get("description", "")

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

    def look(self):

        print(self.location.name, self.location.description)

        for obj in self.location.contents:
            print(obj.name, obj.description)

    def inventory(self):
        for obj in self.contents:
            print(obj.name, obj.description)

class Room(ActiveMUDObject):
    pass

class Door(ActiveMUDObject):

    def init(self, *args, **kwargs):
        self.target = kwargs["target"]

    def use(self, player):
        player.move(self.target)

initialroom = Room(name="The initial room", description="This is all there is right now", location=world)

secondroom = Room(name="The Second Room", description="This is all there is right now", location=world)


door = Door(name="Door", description="A nondescript door", location=initialroom, target=secondroom)

def new_player(name):
    return Player(name=name, location=initialroom)

player = new_player("coda")

player.look()
player.inventory()

#print(world.contents)

def all_objects(root=world):
    objects = []
    queue = [root]
    while len(queue) > 0:
        obj = queue.pop(0)
        objects.append(obj)
        queue += obj.contents
    return objects

#print(all_objects())

import pickle
image = pickle.dumps(world)
#print(image)
