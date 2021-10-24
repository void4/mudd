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

# The object map makes querying objects by ID more efficient.
# It is rebuild with recreate_objmap whenever the world is loaded.
OBJMAP = {}

class MUDObject:
    """
    Every object in the MUD is derived from this class.
    Each has a unique ID, displayed as #<ID>
    """
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

    def __str__(self):
        return self.name + (f"- {self.description}" if self.description else "")

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
    """
    Active Objects have methods that can be called
    """
    def __init__(self, *args, **kwargs):
        self.methods = {}
        super().__init__(self, *args, **kwargs)

    def execute(self, name, args):
        method = self.methods.get(name)
        vm.execute(name, args)

class Room(ActiveMUDObject):
    """
    Rooms subdivide space. They are connected by doors.
    """
    pass

class Door(ActiveMUDObject):
    """
    Doors connect rooms.
    """

    def init(self, *args, **kwargs):
        self.target = kwargs["target"]

    def use(self, player):
        player.move(self.target)
        return True

class Player(ActiveMUDObject):
    """
    Each player controls a Player object. Its contents are its inventory.
    """

    def look(self):

        description = f"I'm inside {self.location.name} - {self.location.description}\n"

        for obj in self.location.contents:
            description += f"{str(obj)}\n"

        description = description[:-1]

        return description

    def inventory(self):
        description = "I'm carrying:\n"
        for obj in self.contents:
            description += f"{str(obj)}\n"
        return description[:-1]

    def dig(self, world, room, doorname, newroomname):
        if isinstance(newroomname, Room):
            newroom = newroomname
        else:
            newroom = Room(name=newroomname, location=world)
        door = Door(name=doorname, target=newroom, location=room)
        self.location.put(door)
        return newroom

    def create(self, world, objname):
        obj = MUDObject(name=objname, location=self)

def new_player(name, location):
    return Player(name=name, location=location)

def all_objects(root):
    if root is None:
        return []

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

def get_obj(q, player=None, world=None, globl=False):
    """
    Gets an object by
    integer id or #id string
    by name through local or global search
    or just returns it if it is already one
    """

    if isinstance(q, int):
        return OBJMAP[q]
    elif isinstance(q, str) and q.startswith("#"):
        return OBJMAP[int(q[1:])]
    elif isinstance(q, str):
        if globl:
            for obj in all_objects(world):
                if obj.name == q:
                    return obj

        if player is not None:
            for obj in player.location.contents.union(player.contents):
                if obj.name == q:
                    return obj
    elif isinstance(q, MUDObject):
        return q

def where(world):
    description = ""
    for obj in all_objects(world):
        if isinstance(obj, Player):
            description += f"{obj.name} ({obj.sid})\t{obj.location.name} ({obj.location.sid})\n"

    description = description[:-1]
    return description

if __name__ == "__main__":

    world = Room(name="The initial room", description="This is all there is right now", location=None)

    player = new_player("coda", world)

    player.dig(world, world, "Gate", "Third room")

    player.create(world, "stick")
    print(player.look())
    print(player.inventory())

    print(where(world))

    #print(world.contents)

    #print(all_objects(world))

    import pickle
    image = pickle.dumps(world)
    #print(image)
