import modo, lx, lxu, os, json, ast
import europa.uiMain
import europa.uiModelExportEntry
from PySide import QtCore, QtGui
# This is the default in-scene attribute that will be created and stored on our primary data node
# It will hold the pickled data as a string.

# The data node will hold the DataAttribute as a string.  Our internal data will be pickled and written to
# this attribute
DataNode        = 'Europa'
DataAttribute   = 'EuropaData'

# BaseData is the dictionary format that will be used throughout the class.
# The class can re-arrange the data and add to it, but when creating a fresh
# node, this template will be used to get us started.
# Templates for Export sets will also be stored here.

ModelEntries     = 'Model_Entries'
AnimationEntries = 'Animation_Entries'

Index            = 'Index'
Color            = 'Color'
ColorOrder       = 'ColorOrder'
Name             = 'Name'
FilePath         = 'File_Path'
ExportNodes      = 'Export_Nodes'
Character        = 'Character'

BaseModelEntry     ={
    Color        : str(),
    Name         : str(),
    FilePath     : str(),
    ExportNodes  : list()}

BaseAnimationEntry ={
    Color        : str(),
    Name         : str(),
    FilePath     : str(),
    Character    : str(),
    ExportNodes  : list()}

BaseData      ={ ModelEntries    : {},
                 AnimationEntries: {} }

# Future formats, terrain, collision...

'''

https://youtrack.jetbrains.com/issue/PY-15624
PYCHARM_DEBUG = True



import modo, lx, lxu
import europa.uiMain; reload(europa.uiMain)
import europa.uiModelExportEntry; reload(europa.uiModelExportEntry)
import europa.main; reload(europa.main)


eu = europa.main.Europa()
eu.show()

'''


class Europa(QtGui.QMainWindow):
    '''
    This class will generate a new data node, or read from an existing node in the scene.
    It handles the list generation, setting, and reading of the model and animation export
    entries.
    '''

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = europa.uiMain.Ui_EuropaExporter()
        self.ui.setupUi(self)
        self.parent = parent

        # Establish List Models
        self.modelMeshExportsList = QtGui.QStandardItemModel( self.ui.modelMeshExports_ListView )
        self.ui.modelMeshExports_ListView.setModel(self.modelMeshExportsList)
        
        self.modelJointsExportsList = QtGui.QStandardItemModel( self.ui.modelJointExports_ListView )
        self.ui.modelJointExports_ListView.setModel(self.modelJointsExportsList)        
        
        self.modelMaterialsExportsList = QtGui.QStandardItemModel( self.ui.modelMaterialExports_ListView )
        self.ui.modelMaterialExports_ListView.setModel(self.modelMaterialsExportsList)             
        
        # Hook up the button clicks and UI interaction code.
        self.establishConnections()

        # Check if the node exists, if it doesn't, create it.
        self.getNode()
        self.populateExportLists()

    def populateExportLists(self, sortBy=Color): #sortedBy=Color
        self.clearExportLists(self.ui.modelExportList_BoxLayout)
        
        modelEntries = self.getModelExportEntries()

        sortedEntries = []
        # Insert horizontal splitters between different color groups, but leave order alone
        if sortBy == Color:
            print 'Sorting By', Color
            curCol = None
            for modelEntry in modelEntries:
                # For every export entry, test the curColor variable.
                # If we have only just started, curCol will be None and we store the first entrie's color
                # After that, every time we hit a different color, add a divider and then append the entry.
                # If the color matches, add it to the entry list since it belongs to the current color group
                if curCol == None:
                    curCol = modelEntry.colorGroup.color
                    sortedEntries.append(modelEntry)
                elif modelEntry.colorGroup.color != curCol:
                    curCol = modelEntry.colorGroup.color
                    splitter = QtGui.QSplitter()
                    splitter.setMinimumHeight(15)
                    sortedEntries.append(splitter)
                    sortedEntries.append(modelEntry)
                else:
                    curCol = modelEntry.colorGroup.color
                    sortedEntries.append(modelEntry)
            modelEntries = sortedEntries

        # Reorganize the export entries and group them by color.
        # the order is dictated by the ColorGroup().order
        if sortBy == ColorOrder:
            colorOrder = ColorGroup().order
            cColor = colorOrder[0]
            for color in colorOrder:
                for modelEntry in modelEntries:
                    if modelEntry.colorGroup.color == color:
                        if cColor != color:
                            # We have entered a new color group, create a split.
                            if sortedEntries:
                                # Ensure you aren't adding a spacer at the very first position in the list.
                                # Only add a splitter if we have already added at least one export entry, not before.
                                splitter = QtGui.QSplitter()
                                splitter.setMinimumHeight(15)
                                sortedEntries.append(splitter)
                        cColor = color
                        sortedEntries.append(modelEntry)
            modelEntries = sortedEntries
        
        for modelEntry in modelEntries:
            self.ui.modelExportList_BoxLayout.addWidget(modelEntry)
        
    def getModelExportEntries(self):
        # Read from the data node and return Model Export Entry 
        # objects populated with the correct data.
        data = self.readData()

        modelExports = []
        
        for idx, val in data[ModelEntries].iteritems():
            ModelEntry = ExportEntry(idx, self)
            ModelEntry.setColorGroup(QtGui.QColor(val[Color]))
            ModelEntry.parent.setPathTextFields(ModelEntry, outFile=val[Name], outDir=val[FilePath])
            modelExports.append(ModelEntry)

        return modelExports
        

    def clearExportLists(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearExportList(layout)

    def establishConnections(self):
        self.ui.addEntry_PushButton.clicked.connect(self.addModelEntry)
        self.ui.exportAll_PushButton.clicked.connect(self.printData)
        #self.ui.pushButton_21.clicked.connect(self.setPath)
        self.ui.refresh_pushButton.clicked.connect(self.refreshUI)
        self.ui.deleteEntry_PushButton.clicked.connect(self.deleteSelectedEntry)
        
        #self.modelExportsList = QtGui.QStandardItemModel( self.ui.modelExports_ListView )
        self.ui.modelMeshExports_ListView.selectionChanged = self.thingChanged
        # self.ui.modelExports_ListView.selectionChanged =  self.thingChanged
        # QtGui.QListView.clicked = self.thingChanged

    
    def thingChanged(self, selected, deselected):
        pass
        #print 'yarp', selected, deselected
        
    def getSelectedEntry(self):
        for i in range(self.ui.modelExportList_BoxLayout.count()):
            exportEntry = self.ui.modelExportList_BoxLayout.itemAt(i).widget()
            if type(exportEntry) == ExportEntry:
                if exportEntry.ui.selected_pushButton.isChecked() is True:
                    return exportEntry

        return None
    
    def deleteSelectedEntry(self):
        idx = self.getSelectedEntry()
        if idx is not None:
            self.deleteEntryByIndex(ModelEntries, idx.index)
        self.refreshUI()
        
    
    def refreshUI(self):
        self.populateExportLists()


    def exists(self):
        '''
        Test if the data node exists in the current scene,
        return True if it exists, return False if it doesn't
        :return:
        '''
        try:
            node = modo.Scene().item(DataNode)
            return True
        except:
            return False

    def getNode(self):
        '''
        Query the data node from the current scene, if it doesn't already exist,
        it will be created and populated with template entries
        '''
        node = None
        if self.exists() is False:
            node = self.createNode()
        else:
            node = modo.Scene().item(DataNode)
        return node

    def createNode(self):
        '''
        Create a Modo locator node and initialize its data holding attributes

        :return: DataNode Modo Locator Object
        '''
        # Original logic used Modo script to create the in-scene node,
        # but this is apparently not required.
        lx.eval('item.create type:{locator} name:{%s}' %DataNode)
        lx.eval('layer.setVisibility item:{%s}, visible:False' %DataNode)
        node = modo.Scene().item(DataNode)
        # node = modo.Scene().addItem(DataNode)
        # node.PackageAdd('glItemShape')
        #
        # channelValues = {'isRadius' : (316000000 * .00000000001),
        #                  'drawShape': 'custom',
        #                  'isShape'  : 'Sphere',
        #                  'isAxis'   : 'y',
        #                  'visible'  : 'off'}
        #
        # node._setChannelValuesFromDict(channelValues)
        # node.name = DataNode

        self.initAttributes()
        return node

    def channelAdd(self, node=None, channel=None, typ=None):
        # Creating channels is apparently not exposed in the API
        # and is apparently much safer to do so using Modo's scripting.
        # Standard types: string, float, time, percentage, integer, boolean, divider
        lx.eval('channel.create item:{%s} name:{%s} type:{%s}' %(node.UniqueName(), channel, typ))

    def initAttributes(self):
        node = self.getNode()
        self.channelAdd(node=node, channel=ModelEntries, typ='string')
        self.channelAdd(node=node, channel=AnimationEntries, typ='string')
        self.storeData(BaseData)


    # Data storage to and from in-scene node
    def storeData(self, data):
        node = self.getNode()

        ModelData = json.dumps( data[ModelEntries], sort_keys=True )
        AnimationData = json.dumps( data[AnimationEntries], sort_keys=True )

        lx.eval('item.channel item:{%s} name:{%s} value:{%s}' %(node.UniqueName(), ModelEntries, ModelData))
        lx.eval('item.channel item:{%s} name:{%s} value:{%s}' %(node.UniqueName(), AnimationEntries, AnimationData))

    def readData(self):
        node = self.getNode()
        data = {ModelEntries:     json.loads(node.channel(ModelEntries).get()),
                AnimationEntries: json.loads(node.channel(AnimationEntries).get())}

        #test = self.byteify(data)

        # Jason data is converted everything to Tuples.  To prevent the need for our code to check if 
        # we're dealing with ints, longs, strings, etc... reconstruct the data as expected object types.
        nDict = {}
        for exportType, exports in data.iteritems():
            nDict[exportType] = {}
            for idx, attributes in exports.iteritems():
                idx = int(idx)
                nDict[exportType][idx] = attributes
                for attribute, val in attributes.iteritems():
                    if attribute == Color: 
                        val = long(val)
                    elif attribute == ExportNodes:
                        if not val:
                            val = []
                        else:
                            val = ast.literal_eval(str(val))
                    nDict[exportType][idx][attribute] = val

        return nDict

    def byteify(self, input):
        # http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
        if isinstance(input, dict):
            return {self.byteify(key):self.byteify(value) for key,value in input.iteritems()}
        elif isinstance(input, list):
            return [self.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input    

    # Data queries
    def modelCount(self):
        data = self.readData()
        return len(data[ModelEntries])

    def animationCount(self):
        data = self.readData()
        return len(data[AnimationEntries])

    def firstIndex(self, dataDict):
        '''
        When passed a dataDict, the data dictionary will be looped through and the
        next available index slot will be returned.  Dictionaries aren't sortable, so
        we simply need to loop through all entries and return the highest entry index+1

        :param dataDict:    Example: ModelEntries or AnimationEntries
        :return:            Int
        '''
        data = self.readData()
        entries = data[dataDict]
        val = 0
        for index, entry in entries.iteritems():
            if val <= int(index):
                val = int(index) + 1
        return val

    def getEntryByIndex(self, type, index):
        data = self.readData()
        return data[type][index]

    def printData(self):
        data = self.readData()
        print ' '
        for typ, entriesDict in data.iteritems():
            print typ      # Model List, Animation List, etc...
            print ' '
            for index, entry in entriesDict.iteritems():
                print 'Index: %s' %(index)
                for attr, val in entry.iteritems():
                    print '\t {0:15}'.format(attr) + ' %s' %(val)
                print ' '

    # Setting Data
    def addModelEntry(self):
        data = self.readData()
        ModelEntry = BaseModelEntry.copy()
        Index = self.firstIndex(ModelEntries)
        data[ModelEntries][Index] = ModelEntry
        data[ModelEntries][Index][Color] = ColorGroup().default.rgb()
        self.storeData(data)

        newEntry = ExportEntry(Index, self)
        self.ui.modelExportList_BoxLayout.addWidget(newEntry)
        #self.ui.modelExportList_BoxLayout.addWidget(QtGui.QPushButton())
        #print self.ui.modelExportList_BoxLayout.count()
        #print newEntry

    def addAnimationEntry(self):
        data = self.readData()
        AnimationEntry = BaseAnimationEntry.copy()
        Index = self.firstIndex(AnimationEntries)
        data[AnimationEntries][Index] = AnimationEntry
        data[AnimationEntries][Index][Color] = ColorGroup().default.rgb()
        self.storeData(data)

    def setData(self, type, index, attribute, val):
        data = self.readData()
        data[type][index][attribute] = str(val)
        self.storeData(data)

    def deleteEntryByIndex(self, type, index):
        data = self.readData()

        del data[type][index]

        newDict = {}
        for key, val in data[type].iteritems():
            key = int(key)
            if key > index:
                newDict[key-1] = val
            else:
                newDict[key] = val

        data[type] = newDict
        self.storeData(data)

    def entrySelectedClicked(self, ExportEntry):
        # Ensure that none of the other entry objects are selected
        self.selectedExclusive(ExportEntry)
        self.setModelExportsList(ExportEntry)

    def selectedExclusive(self, btnObj):
        for i in range(self.ui.modelExportList_BoxLayout.count()):
            exportEntry = self.ui.modelExportList_BoxLayout.itemAt(i).widget()
            if type(exportEntry) == ExportEntry:
                if exportEntry.index != btnObj.index:
                    exportEntry.ui.selected_pushButton.setChecked(False)        

    def setPath(self, ExportEntry, outDir=None, outFile=None):
        # If the path and fileName is not passed in, the user will be prompted with a file browser dialog.
        if outDir is None and outFile is None:
            #outPath = modo.dialogs.customFile('fileSave', 'Save File', ('md5mesh',), ('MD5 Mesh',), ext=('md5mesh',))
            outPath = modo.dialogs.dirBrowse('Output Folder', path='C:/MyExampleProject/export')
            if not outPath: return
            outDir = os.path.abspath(outPath).replace('\\', '/') # Sanitize the resulting string, removes escape slashes, etc.
        
        if outFile is not None:
            self.setData(ModelEntries, ExportEntry.index, Name, outFile)
            self.setPathTextFields(ExportEntry, outFile=outFile)

        if outDir is not None:
            self.setData(ModelEntries, ExportEntry.index, FilePath, outDir)
            self.setPathTextFields(ExportEntry, outDir=outDir)

    def setPathTextFields(self, ExportEntry, outDir=None, outFile=None):
        if outFile: ExportEntry.ui.fileName_LineEdit.setText(outFile)        
        if outDir:  ExportEntry.ui.filePath_LineEdit.setText(outDir)
        

    def setExports(self, ExportEntry):
        # Get the currently selected nodes, and only grab the meshes and group nodes
        selected = modo.Scene().selected
        filtered = [i for i in selected if i.type == 'mesh' or i.type == 'groupLocator']
        if not filtered: return

        # Before writing, convert object string names to idents.  It's safer that way...
        filtered = [i.id for i in filtered]  # Convert object names to 
        self.setData(ModelEntries, ExportEntry.index, ExportNodes, filtered)
        self.setModelExportsList(ExportEntry)
        
    def setModelExportsList(self, ExportEntry):
        data = self.readData()
        
        self.modelMeshExportsList.clear()
        exports = data[ModelEntries][ExportEntry.index][ExportNodes]

        self.modelMaterialsExportsList.clear()

        for e in exports:
            # Stored export nodes are saved as idents, 
            # convert back to their friendly object names
            try:
                e = modo.Scene().item(e)
                item = QtGui.QStandardItem(e.UniqueName())
                self.modelMeshExportsList.appendRow(item)
                
                materials = self.getMaterialsFromMeshObject(e)
                
                for m in materials:
                    item = QtGui.QStandardItem(m)
                    self.modelMaterialsExportsList.appendRow(item)
                    
            except:
                pass

    def getMaterialsFromMeshObject(self, meshObj):
        materialList = []
        
        for poly in meshObj.geometry.polygons:
            if poly.materialTag not in materialList:
                materialList.append(poly.materialTag)

        return materialList        
        
    def colorGroupClicked(self, ExportEntry, mode):
        if mode == 'forward':
            color = ExportEntry.colorGroup.forward
        elif mode == 'back':
            color = ExportEntry.colorGroup.back
        ExportEntry.setColorGroup(color)
        self.setData(ModelEntries, ExportEntry.index, Color, color.rgb())

class ExportEntry( QtGui.QWidget ):
    '''
    Every export entry will get a Qt Widget containing the typical buttons
    '''
    def __init__(self, index, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = europa.uiModelExportEntry.Ui_ModelExportEntry()
        self.ui.setupUi(self)
        self.index = index
        self.parent = parent
        self.colorGroup = ColorGroup()
        self.setColorGroup(self.colorGroup.color)
        self.establishConnections()

    def establishConnections(self):
        self.ui.setPath_pushButton.clicked.connect(self.setPath)
        self.ui.selected_pushButton.clicked.connect(self.selectedClicked)
        #self.ui.colorGroup_pushButton.clicked.connect(self.colorGroupClicked)
        self.ui.colorGroup_pushButton.mousePressEvent = self.mousePressEventColorGroup
        self.ui.setExports_pushButton.clicked.connect(self.setExports)
        self.ui.fileName_LineEdit.editingFinished.connect(self.fileNameEdited)
        self.ui.filePath_LineEdit.editingFinished.connect(self.filePathEdited)
        
    def fileNameEdited(self):
        self.parent.setPath(self, outFile=self.ui.fileName_LineEdit.text())
    def filePathEdited(self):
        self.parent.setPath(self, outDir=self.ui.filePath_LineEdit.text())
    def setPath(self):
        self.parent.setPath(self)
    def setExports(self):
        self.parent.setExports(self)
    def setColorGroup(self, color):
        self.ui.frame.setStyleSheet('QFrame { background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgb(%s, %s, %s), stop:1 rgba(255, 255, 255, 0)) }' %(color.red(), color.green(), color.blue()))
        self.colorGroup.color = color

    def selectedClicked(self):
        self.parent.entrySelectedClicked(self)
    #def colorGroupClicked(self):
        #self.parent.colorGroupClicked(self, 'forward')
    def mousePressEventColorGroup(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.parent.colorGroupClicked(self, 'back')
            # TODO: Make this a copy/paste like function, 
            # for quickly setting a group color using another group
        elif event.button() == QtCore.Qt.LeftButton:
            self.parent.colorGroupClicked(self, 'forward')
        elif event.button() == QtCore.Qt.MiddleButton:
            pass

class ColorGroup(object):
    def __init__(self, getColor = None):
        self.default = self.grey
        self.color   = self.grey
        self.order   = [self.grey, self.maroon, self.red, self.orange, self.yellow,
                        self.purple, self.white, self.lime, self.green, self.navy, self.blue]
        
    @property
    def forward(self):
        for idx, val in enumerate(self.order):
            if self.color == val:
                if idx < len(self.order)-1:
                    self.color = self.order[idx+1]
                else:
                    self.color = self.order[0]
                return self.color

    @property
    def back(self):
        for idx, val in enumerate(self.order):
            if self.color == val:
                if idx == 0:
                    self.color = self.order[-1]
                else:
                    self.color = self.order[idx-1]
                return self.color

    @property
    def grey(self):return QtGui.QColor(127,127,127)

    @property
    def maroon(self):return QtGui.QColor(170,0,0)

    @property
    def red(self):return QtGui.QColor(255,0,0)

    @property
    def orange(self):return QtGui.QColor(255,85,0)

    @property
    def yellow(self):return QtGui.QColor(255,255,0)

    @property
    def purple(self):return QtGui.QColor(170,0,255)

    @property
    def white(self):return QtGui.QColor(255,255,255)

    @property
    def lime(self):return QtGui.QColor(170,255,0)

    @property
    def green(self):return QtGui.QColor(85,255,0)

    @property
    def navy(self):return QtGui.QColor(0,0,255)

    @property
    def blue(self):return QtGui.QColor(0,0,127)
