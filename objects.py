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

OBJMAP = {}

class MUDObject:
    def __init__(self, *args, **kwargs):

        self.id = nextid()
        self.sid = "#" + str(self.id)
        OBJMAP[self.id] = self
        dprint(f"Created object #{self.id}")

        self.key = None#Key(self.id)

        self.name = kwargs.get("name", "???")
        self.description = kwargs.get("description", "")

        self.location = None
        self.move(kwargs.get("location"))

        self.contents = kwargs.get("contents", set())

        if hasattr(self, "init"):
            self.init(*args, **kwargs)

    # TODO __repr__ with name etc.

    def move(self, newlocation):
        if self.location is not None:
            self.location.contents.remove(self)

        self.location = newlocation

        if newlocation is not None:
            newlocation.contents.add(self)

    def put(self, object):
        self.contents.add(object)

class ActiveMUDObject(MUDObject):
    def __init__(self, *args, **kwargs):
        self.methods = {}
        super().__init__(self, *args, **kwargs)

    def execute(self, name, args):
        method = self.methods.get(name)
        vm.execute(name, args)

class World(ActiveMUDObject):
    pass

class Room(ActiveMUDObject):
    pass

class Door(ActiveMUDObject):

    def init(self, *args, **kwargs):
        self.target = kwargs["target"]

    def use(self, player):
        player.move(self.target)

class Player(ActiveMUDObject):

    def look(self):

        description = f"{self.location.name} - {self.location.description}\n"

        for obj in self.location.contents:
            description += f"{obj.name} - {obj.description}\n"

        description = description[:-1]

        return description

    def inventory(self):
        for obj in self.contents:
            print(obj.name, obj.description)

    def dig(self, world, room, doorname, newroomname):
        newroom = Room(name=newroomname, location=world)
        door = Door(name=doorname, target=newroom, location=room)
        self.location.put(door)

def new_player(name, location):
    return Player(name=name, location=location)

def all_objects(root):
    objects = []
    queue = [root]
    while len(queue) > 0:
        obj = queue.pop(0)
        objects.append(obj)
        queue += obj.contents
    return objects

def recreate_objmap(world):
    global OBJMAP
    for obj in all_objects(world):
        OBJMAP[obj.id] = obj

def idorobj(q):
    if isinstance(q, int):
        return OBJMAP[q]
    elif isinstance(q, str) and q.startswith("#"):
        return OBJMAP[int(q[1:])]
    else:
        return q

def where(world):
    for obj in all_objects(world):
        if isinstance(obj, Player):
            print(f"{obj.name} ({obj.sid})\t{obj.location.name} ({obj.location.sid})")

if __name__ == "__main__":
    world = World()

    initialroom = Room(name="The initial room", description="This is all there is right now", location=world)

    player = new_player("coda", initialroom)

    player.dig(world, initialroom, "Gate", "Third room")

    player.look()
    player.inventory()

    where(world)

    #print(world.contents)

    #print(all_objects(world))

    import pickle
    image = pickle.dumps(world)
    #print(image)
