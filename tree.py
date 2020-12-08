from collections import deque


class vertex:
    def __init__(self, value, id, type, path, link, parent):
        self.id = id
        self.value = value
        self.path = path
        self.link = link
        self.parent = parent
        self.children = []
        self.type = type

    def setValue(self, value):
        self.value = value

    def setType(self, type):
        self.type = type

    def setChildren(self, children):
        self.children = children

    def addChild(self, child):
        self.children.append(child)

    def getValue(self):
        return self.value

    def getId(self):
        return self.id

    def getParent(self):
        return self.parent

    def getPath(self):
        return self.path

    def getLink(self):
        return self.link

    def getChildren(self):
        return self.children

    def getType(self):
        return self.type


class Tree:
    count = 0

    def __init__(self, service, rootVal='root'):
        self.root = vertex(rootVal, 'root', 'root', 'root', None, None)
        self.service = service
        self.count += 1

    def getRoot(self):
        return self.root

    def bfsIdSearch(self, id):
        queue = deque()
        queue.append(self.root)
        while len(queue) > 0:
            current = queue.popleft()
            if current.id == id:
                return current
            if current.children:
                for child in current.children:
                    queue.append(child)
        return None

    def bfsValueSearch(self, value):
        ids = []
        queue = deque()
        queue.append(self.root)
        while len(queue) > 0:
            current = queue.popleft()
            if current.value == value:
                ids.append(current.id)
            if current.children:
                for child in current.children:
                    queue.append(child)
        return ids

    def findVal(self, value):
        return self.bfsIdSearch(value)

    def findId(self, id):
        return self.bfsIdSearch(id)

    def addChild(self, parent, value, childId, type, link):
        childPath = f"{parent.getPath()},{value}"
        child = vertex(value, childId, type, childPath, link, parent)
        parent.addChild(child)
        self.count += 1

    def expandTree(self, vert):
        page_token = None
        while True:
            response = self.service.files().list(q=f"'{vert.getId()}' in parents and trashed=false",
                                                 spaces='drive',
                                                 fields='nextPageToken, files(id, name, mimeType, webViewLink)',
                                                 pageToken=page_token).execute()
            for file in response.get('files', []):
                # print('Found file: %s (%s) (%s)' % (file['name'], file['id'], file['mimeType']))
                t = file['mimeType'].split('.')[-1]
                self.addChild(vert, file['name'], file['id'], t, file['webViewLink'],)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    def moveToChild(self, current, childName):
        cmp = childName.lower()
        for child_tmp in current.children:
            if child_tmp.getValue().lower() == cmp:
                if "folder" in child_tmp.getType().lower():
                    if len(child_tmp.children) == 0:
                        self.expandTree(child_tmp)
                    return child_tmp
        print("Child could not be found")
        return current

    def moveToParent(self, child):
        if not child.parent:
            print("current node is root, it has no parent")
            return child
        else:
            return child.parent