import lx, lxu, lxifc
import modo
import sys, os, math, datetime


__author__ = 'Nicholas Stevenson'
__date__ = 'April 2015'

# Huge thanks David Henry for his web site dissecting the format and contents of id's md5mesh and md5anim files.
# His work made creating this much, much easier.
# http://tfc.duke.free.fr/coding/md5-specs-en.html
#
# '''
# Inheritance Diagram
#
#
#
# Object
# |- Joints
# |- Meshes
#    |-tris
#      |-verts
#        |-weights
#          |-joint
#
#
#    |-verts
#      |-weights
#        |-joint
#
#    |-weights
#      |-joint
# '''
#
#
#
# ## PyCharm Debugger
# import sys
# sys.path.append(r"C:\Program Files (x86)\JetBrains\PyCharm 5.0\debug-eggs\pycharm-debug.egg")
#
# import pydevd
# print pydevd.__file__
# pydevd.settrace('localhost', port=7720, suspend=False)
#
#
#
#
# ##  Export Test
# import modo
# import europa.md5 as md5
# reload(md5)
# eu = md5.MD5()
#
# originNode = modo.Scene().item('origin')
# meshList = [modo.Scene().item('Cube')]
# outPath = r'C:\Users\nstevenson\AppData\Roaming\Luxology\Scripts\Doom\scenes\ExportTest.md5mesh'
#
# eu.meshExport(originNode=originNode, meshList=meshList, outPath=outPath)
#
#
# ##  Build Test
# import modo
# import europa.md5 as md5
# reload(md5)
# eu = md5.MD5()
#
# inPath = r'C:\Users\nstevenson\AppData\Roaming\Luxology\Scripts\Doom\scenes\ExportTest.md5mesh'
# eu.read(inPath)
# eu.build()
# modo.Scene().item('Cube').select()



MD5Version = 10

Comments = True         # The md5mesh format allows for comments, if escaped using //
                        # To make the file a bit more readable, we'll insert some info in a handful of areas

i_to_cm = float(0.0254) # Modo's internal API works in Centimeters, while Radiant is in Inches
                        # When going from Radiant to Modo, this is your scale to be applied to any transform values

cm_to_i = float(39.37)  # When exporting to Radiant, multiply up the world spaces by this value, to convert from Modo's
                        # internal Centimeters to Radiant Inches.



class MD5(object):
    def __init__(self, ):
        self.MD5Version = int
        self.commandline = str
        self.joints = []
        self.meshes = []

    def read(self, filePath):
        # If passed a file path, the MD5File object will read in the file and parse its contents in to the class.
        if os.path.exists(filePath) is False: return
        if filePath.lower().endswith('.md5mesh') is False: return

        phile = open(filePath, 'r')
        lines = phile.readlines()
        phile.close()

        jntCnt = 0

        # These will be toggled on and off depending on the section of the
        # file we are currently reading
        sJoints     = 0
        sMeshes     = 0
        sNumVerts   = 0
        sNumTris    = 0
        sNumWeights = 0

        # md5 files store how many items of a certain type, you will encounter inside a section
        # store those numbers so we can turn off the section when we hit that number of items.
        numVerts = int
        numTris = int
        numWeights = int
        # Begin parsing...
        for line in lines:
            line = line.split()

            if len(line) > 0:
                if   line[0] == 'MD5Version':   self.MD5Version = line[1]
                elif line[0] == 'commandline':  self.commandline = ' '.join(line[1:])
                #elif line[0] == 'numJoints':    self.numJoints = line[1]
                #elif line[0] == 'numMeshes':    self.numMeshes = line[1]

                elif line[0] == 'joints':       sJoints = 1
                elif line[0] == 'mesh':         sMeshes = 1
                elif line[0] == 'numverts':     sNumVerts = 1
                elif line[0] == 'numtris':      sNumTris = 1
                elif line[0] == 'numweights':   sNumWeights = 1

                if sJoints:
                    if len(line) == 1:
                        if line[0] == '}':
                            sJoints = 0

                    elif len(line) == 2:        pass        # This will only be hit if we just
                                                            # entered the section, skip this read line.
                    else:
                        joint = self.Joint()
                        joint.name = line[0].strip('"')     # Remove surrounding quotes

                        joint.index = jntCnt           # Start counting at 0 and keep going
                        jntCnt += 1                         # until we're done indexing joints.

                        if line[1] == '-1':                 # If the parent is -1,
                            joint.parent = 'world'          # the joint is parented to the world
                        else:
                            joint.parent = self.getByIdx(objLs=self.joints, index=int(line[1]))



                        joint.position    = [float(line[3])*i_to_cm, float(line[4])*i_to_cm, float(line[5])*i_to_cm]
                        joint.orientation = [float(line[8]), float(line[9]), float(line[10])]
                        #
                        # mtx = modo.mathutils.Matrix4()
                        # mtx.position = joint.position
                        # mtx.
                        #
                        self.joints.append(joint)


                if sMeshes:
                    if len(line) == 2:
                        if line[1] == '{':
                            # We have just entered a mesh section,
                            # create a new mesh item
                            curMesh = self.Mesh()
                            self.meshes.append(curMesh)

                    if line[0] == '//' :
                        for meshName in line[2:]:
                            curMesh.meshNames.append(meshName.strip(','))

                    if line[0] == 'shader':
                        curMesh.shader = ''.join(line[1:]).strip('"')



                    # As soon as we have as many verts, tris, or weights, as the total value (ie numverts 34),
                    # we have finished with that section.
                    if len(curMesh.verts) == numVerts:
                        sNumVerts = 0
                    if len(curMesh.tris) == numTris:
                        sNumTris = 0
                    if len(curMesh.weights) == numWeights:
                        sNumWeights = 0



                    if sNumVerts:
                        if line[0] == 'numverts':
                            numVerts = line[1]
                        elif line[0] == 'vert':
                            vert = curMesh.Vert()
                            curMesh.verts.append(vert)

                            vert.index = int(line[1])
                            vert.tex_u = float(line[3])
                            vert.tex_v = float(line[4])
                            vert.startWeight = int(line[6])
                            vert.countWeight = int(line[7])
                            vert.weights = []   # This list will be populated further down

                    if sNumTris:
                        if line[0] == 'numtris':
                            numTris = line[1]
                        elif line[0] == 'tri':
                            tri = curMesh.Tri()
                            curMesh.tris.append(tri)

                            tri.index = int(line[1])
                            # lines 2, 3, and 4 are index numbers to verts we have already
                            # created objects for, find those actual Vert objects
                            tri.verts = [self.getByIdx(objLs=curMesh.verts, index=int(line[2])),
                                         self.getByIdx(objLs=curMesh.verts, index=int(line[3])),
                                         self.getByIdx(objLs=curMesh.verts, index=int(line[4]))]

                    if sNumWeights:
                        if line[0] == 'numweights':
                            numWeights = line[1]
                        elif line[0] == 'weight':
                            weight = curMesh.Weight()
                            curMesh.weights.append(weight)

                            weight.index = int(line[1])
                            weight.joint = self.getByIdx(objLs=self.joints, index=line[2])
                            weight.bias  = float(line[3])
                            weight.pos   = [float(line[5])*i_to_cm, float(line[6])*i_to_cm, float(line[7])*i_to_cm]

        # Once we have constructed the mesh item, let's go back to the self.verts list
        # The position of the verts are calculated by evaluating the weighting information.
        # Since this information comes up further down in the md5mesh file, we only stored
        # the integers.  We're going to swap those for pointers back to the Weight objects.
        for mesh in self.meshes:
            for vert in mesh.verts:
                # Verts have a startWeight and a countWeight, this is an index list of all
                # the weights that influence this vert's position.  Hard weighted verts will
                # have a single influence, while soft weighted verts will have multiple

                for i in xrange(vert.startWeight, vert.startWeight + vert.countWeight):
                    vert.weights.append(self.getByIdx(objLs=mesh.weights, index=i))


    def write(self, outFile):
        # Once we have a fully constructed MD5Mesh object, either through parsing an existing .md5mesh file,
        # or by creating our own mesh, this method will write the data out to a .md5mesh file.

        if outFile.endswith('.md5mesh') is False:
            outFile += '.md5mesh'

        if os.path.exists(outFile):
            # Add a confirm dialog if you would like to overwrite this file.
            pass

        ind = '	' # This is a tab character, md5mesh files use this rather than spaces

        o = []

        o.append('%s %s'     %('MD5Version',     self.MD5Version))
        o.append('%s "%s"'   %('commandline',    self.commandline))
        o.append('%s %s'     %('//Export Date:', datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S')))
        o.append('')
        o.append('%s %s'     %('numJoints',      self.numJoints))
        o.append('%s %s'     %('numMeshes',      self.numMeshes))
        o.append('')
        o.append('joints {')

        for joint in self.joints:

            # There is special logic for a joint's parent.  A joint can either be parented to the world, or it will
            # have a pointer back to a joint object.  We'll deal with those two situations here.
            parent = ''
            parentName = ''
            if joint.parent == 'world':
                parent = -1
                parentName = 'world'
            else:
                parent = joint.parent.index
                parentName = joint.parent.name

            tStr = '%s"%s"%s%s ( %s %s %s ) ( %s %s %s )' %(ind, joint.name, ind, parent, joint.position[0], joint.position[1], joint.position[2], joint.orientation[0], joint.orientation[1], joint.orientation[2])
            if Comments is True:
                tStr += '%s// %s' %(ind*2, parentName)
            o.append(tStr)

        o.append('}')
        o.append('')

        for mesh in self.meshes:
            o.append('mesh {')
            if Comments is True:
                meshLs = ', '.join(mesh.meshNames)
                o.append('%s// %s: %s' %(ind, 'meshes', meshLs))
            o.append('%s%s "%s"' %(ind, 'shader', mesh.shader))
            o.append('')

            # Verts
            o.append('%s%s %s' %(ind, 'numverts', mesh.numVerts))
            for vert in mesh.verts:
                o.append('%s%s %s ( %s %s ) %s %s' %(ind, 'vert', vert.index, vert.tex_u, vert.tex_v, vert.startWeight, vert.countWeight))
            o.append('')

            # Tris
            o.append('%s%s %s' %(ind, 'numtris', mesh.numTris))
            for tri in mesh.tris:
                o.append('%s%s %s %s %s %s' %(ind, 'tri', tri.index, tri.verts[2].index, tri.verts[1].index, tri.verts[0].index))
            o.append('')

            # Weights
            o.append('%s%s %s' %(ind, 'numweights', mesh.numWeights))
            for weight in mesh.weights:
                o.append('%s%s %s %s %s ( %s %s %s )' %(ind, 'weight', weight.index, weight.joint.index, weight.bias, weight.pos[0], weight.pos[1], weight.pos[2],))
            o.append('}')
            o.append('')

        with open(outFile, 'w') as f:
            f.write('\n'.join(o))

    def build(self):
        '''
        Firing this method from inside Modo will recreate the currently stored md5mesh object as an actual
        object constructed from a list of meshes, bones, and skinning.
        '''
        scene = modo.Scene()

        for joint in self.joints:
            mJnt = scene.addItem('locator', name=joint.name)
            joint.mObj = mJnt
            #joint.mObj.channel('isRadius').set(.005)

        originNode = [j for j in self.joints if j.parent == 'world'][0]
        originNode.mObj.position.set( originNode.position )
        originNode.mObj.rotation.set( originNode.orientationAsEuler, degrees=True )

        for joint in self.joints:
            if joint.parent != 'world':
                joint.mObj.position.set( joint.position )
                joint.mObj.rotation.set( joint.orientationAsEuler, degrees=True )

        for joint in self.joints:
            if joint.parent != 'world':
                #joint.mObj.setParent(joint.parent.mObj)
                lx.eval('item.parent %s %s inPlace:1' %(joint.mObj.UniqueName(), joint.parent.mObj.UniqueName()))

        # Set the joint's current positions as the Setup position
        for joint in self.joints:
            lx.eval('item.toSetup %s' %joint.mObj.UniqueName())

        # Create a new UV map for our meshes.

        # Each joint used in skinning needs a single transform influence, this will be hooked up later in the process
        # once we start generating our weight maps and applying the skinning info.
        skinJoints = []
        for mesh in self.meshes:
            for weight in mesh.weights:
                if weight.joint not in skinJoints:
                    skinJoints.append(weight.joint)

        for joint in skinJoints:
            joint.influence = scene.addItem('genInfluence', 'Transform: %s' %joint.name)

        # With the joints oriented, lets start constructing the mesh items,
        # We'll also make a new UVMap for each mesh.
        normalizeFolder = scene.addItem('deformGroup')
        for mesh in self.meshes:
            mesh.mObj = scene.addMesh()
            mesh.UVMap = mesh.mObj.geometry.vmaps.addMap(mapType=lx.symbol.i_VMAP_TEXTUREUV, name='Texture')

            mesh.maskObj = scene.addItem('mask', '%s%s' %('__'.join(mesh.meshNames), ' (Material)'))
            mesh.maskObj.setParent(scene.items('polyRender')[0])
            mesh.shaderObj = scene.addMaterial(name = mesh.shader)
            mesh.maskObj.channel('ptag').set(mesh.shaderObj.UniqueName())
            mesh.shaderObj.setParent(mesh.maskObj, index=1)

            if mesh.meshNames:
                #mesh.mObj.name = mesh.meshNames[0]
                mesh.mObj.name = '__'.join(mesh.meshNames)
            geo = mesh.mObj.geometry

            for vert in mesh.verts:
                # This will create modo vertex objects,
                # lets capture them and store them on our object as mObj
                vert.mObj = geo.vertices.new(vert.getPosition())

            for tri in mesh.tris:
                # Now, using the Modo vertexes, create faces for each.
                v1 = tri.verts[0].mObj
                v2 = tri.verts[1].mObj
                v3 = tri.verts[2].mObj
                geo.polygons.new((v1, v2, v3), reversed=True)
                geo.polygons[-1].materialTag = mesh.shaderObj.UniqueName()
                #tri.mPolygon.materialTag = mesh.shaderObj
                # Capture the generated modo.meshgeometry.MeshVertex() objects


            # Loop over each polygon that we created for the mesh.
            # We need to find the three verts via vert index and assign their uv data.
            for poly in geo.polygons:
                for vert in poly.vertices:
                    for v in mesh.verts:
                        if vert._index == v.index:
                            # Not sure why, but the texture pages from top to bottom
                            # are reversed in Radiant. so invert the V Value
                            poly.setUV([v.tex_u, 1-v.tex_v], vert, uvmap=mesh.UVMap)

            # Create a deformer and a normalizing folder.
            mesh.normalizeFolder = normalizeFolder
            mesh.normalizeFolder >> mesh.mObj.itemGraph('deformers')

            # TODO: Check if this continues to crash Modo, falling back on >>
            #mesh.normalizeFolder.connectInput(mesh.mObj.itemGraph('deformers'))

            # We only need to perform this for the joints that influence the mesh.
            # This is to prevent deformer attachments that have 0.0 influence.
            for weight in mesh.weights:
                weight.joint.influence >> mesh.normalizeFolder
                weight.joint.influence.channel('type').set('mapWeight')
                weight.joint.influence.channel('name').set(weight.joint.mObj.UniqueName())
                weight.joint.influence >> mesh.mObj.itemGraph('deformers')
                weight.joint.mObj >> weight.joint.influence
                weight.weightmap = geo.vmaps.addWeightMap(weight.joint.mObj.UniqueName(), initValue=0.0)

            for vert in mesh.verts:
                for weight in vert.weights:
                    weight.weightmap[vert.mObj._index] = weight.bias

            geo.setMeshEdits()

        print 'done'

        return self

    def exportSelected(self):

        if not modo.Scene().selected:
            modo.dialogs.alert(title='Error', message='Export Halted:\nplease select either a Group with one or more Meshes inside it, or a single Mesh item.')
            return

        self.exportNodes(nodes=modo.Scene().selected)

    def exportNodes(self, nodes=None, outPath=None, outFile=None):

        if not nodes: return

        nodeList = [i for i in nodes if i.type == 'mesh' or i.type == 'groupLocator']

        meshList = []

        # Deconstruct the nodes items list, if we have a mesh selected, continue as normal.  If we have a group
        # locator selected, we want to query any descendant mesh children.
        for item in nodeList:
            if item.type == 'mesh':
                meshList.append(item)
            elif item.type == 'groupLocator':
                meshChildren = item.children(recursive=True, itemType='mesh')

        print 'Mesh List:', meshList

        if not meshList:
            modo.dialogs.alert(title='Error', message='Export Halted:\nCould not find any meshes for export.')
            return

        # TODO: Figure out the matrix math required for a Yup to Zup conversion
        # Pre export
        # We now have a list of mesh items.  We need to rotate them for Z up during export
        #rNode = None
        #if groupNode is not None:
            #rNode = groupNode
        #elif groupNode is None:
            #rNode = meshList[0]

        #rx = rNode.rotation.x.get()
        #rx += math.radians(90)
        #rNode.rotation.x.set(rx)

        # Post export
        #rx = rNode.rotation.x.get()
        #rx -= math.radians(90)
        #rNode.rotation.x.set(rx)

        # Pass the objects to the export command
        outPath = r"C:\Users\nstevenson\AppData\Roaming\Luxology\Scripts\Doom\scenes\ExportTest.md5mesh"
        rNode = modo.Scene().addJointLocator('origin')
        result = self.meshExport(originNode=rNode, meshList=meshList, outPath=outPath)
        result = None
        # Prompt the user for the export path for the resulting file.
        #inpath = modo.dialogs.customFile('fileOpen', 'Open File', ('md5mesh',), ('MD5 Mesh File',), ('*.md5mesh',))

        #modo.dialogs.alert(title='Success', message='Export Successful!')


        return result

    def meshExport(self, originNode=None, meshList=None, outPath=None):

        # First, construct the joint list. This currently only supports static meshes with a single origin node.
        origin = self.Joint()
        self.joints.append(origin)
        origin.name = 'origin'
        origin.parent = 'world'
        origin.index = 0
        origin.mObj = originNode
        origin.Matrix = modo.mathutils.Matrix4( origin.mObj.channel('worldMatrix').get() )
        origin.Quat = modo.mathutils.Quaternion()
        origin.Quat.fromMatrix4(origin.Matrix)
        origin.position = origin.Matrix.position
        origin.orientation = origin.Quat.values

        # Start construct mesh items, one for each in the mesh list.
        for mObj in meshList:
            # The md5 file format splits up meshes by their materials.
            # Gather a list of material assignments across each mesh.

            mtrLs = self.getMaterialsFromMeshObject(mObj)

            # ASSume that a UV map named 'Texture' exists for the given mesh.
            uvMap = [i for i in mObj.geometry.vmaps.uvMaps if i.name == 'Texture'][0]

            for mtr in mtrLs:
                mesh = self.Mesh(mObj, mObj.UniqueName(), mtr)
                self.meshes.append(mesh)

                # TODO: Verify and add an error prompt if this does not exist
                # Querying the geometry does not give us the correct list of vertices, it will only tell us the number
                # of physical geometry vertices that are part of the mesh, and not the split edge vertices that occur
                # in the UVMaps.
                # TODO: Verify that all mesh Vertices exist in the UVMap

                # First, lets generate all of our items based on the physical geometry items.
                # f for FACE!
                triCnt = 0
                vertCnt = 0
                weightCnt = 0

                for polygon in mesh.mObj.geometry.polygons:

                    if polygon.materialTag == mtr:

                        for tri in polygon.iterTriangles(asIndices=False):
                            triObj = mesh.Tri(tri, polygon, triCnt)
                            mesh.tris.append(triObj)
                            triCnt += 1

                            # While we're looping over the faces, for every vertex, create a vertex item and add it
                            # to the tri object's 'verts' list.
                            for vert in tri:

                                uv = vert.getUVs(uvMap)
                                fVert = None            # The two sections below will attempt a lookup, to ensure we
                                                        # create a vertex twice.  If those fail, we have a new vert

                                if isinstance(uv[0], float):
                                    # Vertex with no additional UV verts
                                    fVert = mesh.findVert(vert, None)

                                    if fVert is None:
                                        mVert = mesh.Vert(vert, None, vertCnt, uv[0], 1-uv[1])
                                        vertCnt += 1

                                else:
                                    fVert = mesh.findVert(vert, polygon)

                                    if fVert is None:
                                        for idx, discoVal in enumerate(uv):
                                            poly, uv = discoVal

                                            if poly == polygon:
                                                mVert = mesh.Vert(vert, polygon, vertCnt, uv[0], 1-uv[1])
                                                vertCnt += 1

                                if fVert is None:
                                    weightObj = mesh.Weight(weightCnt, weightCnt, origin, 1.0,
                                    [vert.position[0] * cm_to_i, vert.position[1] * cm_to_i, vert.position[2] * cm_to_i])
                                    weightCnt += 1

                                    mVert.weights.append(weightObj)
                                    mVert.countWeight = 1
                                    mVert.startWeight = weightObj.index

                                triObj.verts.append( mVert )


        self.MD5Version = MD5Version
        self.commandline = 'Modo Export Selected'

        self.write(outFile=outPath)

        #modo.Scene().removeItems(origin.mObj.UniqueName())
        return self


    class Joint(object):
        '''
        Doc
        name (string) is the joint's name. parent (int) is the joint's parent index. If it is equal to -1,
        then the joint has no parent joint and is what we call a root joint. pos.x, pos.y and pos.z (float)
        are the joint's position in space. orient.x, orient.y and orient.z (float) are the joint's orientation
        quaternion x, y and z components. After reading a joint, you must calculate the w component.

        Format
        "name" parent ( pos.x pos.y pos.z ) ( orient.x orient.y orient.z )

        Example
        "origin"	-1 ( -1491.5367431641 -1880.1069335938 111.8948135376 ) ( -0.5 -0.5 -0.5 )		//
        "joint1"	0 ( -1491.5255126953 -1880.0051269531 48 ) ( -0.5657211542 -0.7070862055 0.0053915498 )		// origin
        "joint2"	1 ( -1491.5255126953 -1838.0020751953 16 ) ( -0.6210179925 -0.690197587 0.0717006698 )		// joint1
        "joint3"	2 ( -1491.5255126953 -1816.2507324219 0 ) ( 0.0289435908 -0.3105864227 -0.9468282461 )		// joint2
        "join4"	3 ( -1491.5255126953 -1796.0070800781 -16 ) ( -0.5 -0.5 -0.5 )		// joint3
        "joint5"	0 ( -1490.9719238281 -1922.3385009766 80.0359344482 ) ( -0.5 -0.5 -0.5 )		// origin
        "joint6"	0 ( -1490.9719238281 -1922.3385009766 15.947719574 ) ( -0.5 -0.5 -0.5 )		// origin
        '''
        def __init__(self):
            self.name  = str
            self.index =  int   # This is an arbitrary number that is used to give the joint an index
            self.parent = int   # This is a pointer back to an actual joint object, or 'world' if -1
            self.position = [float, float, float]
            self.orientation = [float, float, float]
            self.influence = None   # This will hold the transform effector, we only need one per bone
                                    # so we'll store it if we create one

        @property
        def orientationAsFloats(self):
            if self.orientation:
                tFloats = [float(self.orientation[0]),
                           float(self.orientation[1]),
                           float(self.orientation[2])]
                return tFloats
            else:
                return None

        def w(self):
            x, y, z = self.orientation
            t = 1.0 - (x*x) - (y*y) - (z*z)
            if t < 0.0:
                return 0.0
            else:
                return -math.sqrt(t)

        @property
        def orientationAsEuler(self):
            # Using the stored self.orientation, convert the Quaternions to Euler XYZ values
            # x(heading), y(attitude), z(bank)

            x, y, z = self.orientation
            Quat = modo.mathutils.Quaternion(values=[x, y, z, getW(x, y, z)])

            Quat_Mtx4 = Quat.toMatrix4()

            rot = modo.mathutils.Matrix4()._MatrixToEuler(Quat_Mtx4)
            return [math.degrees(rot[0]), math.degrees(rot[1]), math.degrees(rot[2])]

        def matrix(self):
            x, y, z = self.orientation
            Quat = modo.mathutils.Quaternion(values=[x, y, z, getW(x, y, z)])

            Matrix = Quat.toMatrix4()
            Matrix.position = self.position

            return Matrix

    class Mesh(object):
        '''
        Example
        mesh {
            shader "<string>"

            numverts <int>
            vert vertIndex ( s t ) startWeight countWeight
            vert ...

            numtris <int>
            tri triIndex vertIndex[0] vertIndex[1] vertIndex[2]
            tri ...

            numweights <int>
            weight weightIndex joint bias ( pos.x pos.y pos.z )
            weight ...
        }
        '''
        def __init__(self, mObj=None, meshNames=[], shader=None):
            self.mObj = mObj
            self.meshNames = [meshNames]
            self.shader = shader
            self.tris = []

        @property
        def numTris(self):
            return len(self.tris)

        @property
        def numVerts(self):
            vertLs = []
            for tri in self.tris:
                for vert in tri.verts:
                    if vert not in vertLs:
                        vertLs.append(vert)
            return len(vertLs)

        @property
        def numWeights(self):
            return len(self.weights)

        @property
        def weights(self):
            weights  = []
            for tri in self.tris:
                for vert in tri.verts:
                        for weight in vert.weights:
                            if weight not in weights:
                                weights.append(weight)
            weights = sorted(weights, key=lambda weights: weights.index)
            return weights

        @property
        def verts(self):
            verts = []
            for tri in self.tris:
                for vert in tri.verts:
                    if vert not in verts:
                        verts.append(vert)
            verts = sorted(verts, key=lambda vert: vert.index)
            return verts

        def findVert(self, vert, polygon):
            result = None
            for tri in self.tris:
                for v in tri.verts:
                    if polygon is None:
                        if v.mObj == vert:
                            return v
                    else:
                        if v.mObj == vert and v.polygon == polygon:
                            return v
            return result

        class Vert(object):
            '''
            Doc
            numverts (int) is the number of vertices of the mesh. After this variable, you have the vertex list.
            vertIndex (int) is the vertex index. u and v (float) are the texture coordinates (also called UV coords).
            In the MD5 Mesh format, a vertex hasn't a proper position. Instead, its position is computed from vertex weights
            (this is explained later in this document). countWeight (int) is the number of weights,
            starting from the startWeight (int) index, which are used to calculate the final vertex position.

            Format
            vert vertIndex ( u v ) startWeight countWeight

            Example
            vert 0 ( 0.5000165105 0.75 ) 7 1
            vert 1 ( -0.000017 0.5 ) 6 1
            vert 2 ( -0.000017 0.75 ) 8 2
            '''
            def __init__(self, mObj=None, polygon=None, index=None, tex_u=None, tex_v=None):
                self.mObj = mObj
                self.polygon = polygon
                self.index = index
                self.tex_u = tex_u
                self.tex_v = tex_v
                self.startWeight = int
                self.countWeight = int
                self.weights = []

            def getPosition(self):
                '''
                A vertex's final position is an evaluation of its weights.  Each weight caries a position, a bias, and a joint
                the bias is multiplied against the position, and then offset by the joint.

                If a vert sits right on top of a bone and is 100% influenced by that bone, its position is 0,0,0
                If it's 100% weighted to a bone but is not on top of the bone, its position will be its distance from that bone.

                If smooth skinning comes in to play, each joint adds to the final position of the bone, and the bias
                is simply the skinning value from 0 to 1, giving each joint more sway in the final position.
                '''
                x, y, z = 0, 0, 0
                scene = modo.Scene()
                for weight in self.weights:

                    Jx, Jy, Jz = weight.joint.position

                    # We need to rotate the weight.pos vector around the bone's rotation matrix.
                    wMtx = modo.mathutils.Matrix4(position=weight.pos)

                    mObj = modo.Item(weight.joint.name)
                    jMtx = modo.mathutils.Matrix4( mObj.channel('worldMatrix').get() )

                    # fMtx = wMtx.__mul__(jMtx)
                    fMtx = wMtx.__mul__(jMtx.asRotateMatrix())
                    fVec = fMtx.position
                    x += (Jx + fVec[0]) * weight.bias
                    y += (Jy + fVec[1]) * weight.bias
                    z += (Jz + fVec[2]) * weight.bias

                return [x, y, z]


        class Tri(object):
            '''
            Doc
            numtris is the number of triangles of the mesh. triIndex (int) is the index of the triangle. Each is defined by
            three vertex indices composing it: vertIndex[0], vertIndex[1] and vertIndex[2] (int).

            Format
            tri triIndex vertIndex[0] vertIndex[1] vertIndex[2]

            Example
            tri 0 2 1 0
            tri 1 4 0 3
            tri 2 7 6 5
            '''
            def __init__(self, mObj=None, polygon=None, index=None):
                self.mObj = mObj
                self.polygon = polygon
                self.index = index
                self.verts = []

        class Weight(object):
            '''
            Doc
            numweights (int) is the number of weights of the mesh. weightIndex (int) is the weight index.
            joint (int) is the joint it depends on. bias (float) is a factor in the [0.0, 1.0] range which defines the
            contribution of this weight when computing a vertex position. pos.x, pos.y and pos.z (float) are the weight's
            position in space.

            Format
            weight weightIndex joint bias ( pos.x pos.y pos.z )

            Example
            weight 0 1 1 ( -1.0363395214 -0.0061404649 0 )
            weight 1 1 1 ( -0.7328026891 -0.0061404649 0.7328026891 )
            weight 2 1 .5 ( 0 -0.0061404649 1.0363395214 )
            '''

            def __init__(self, index=None, startWeight=None, joint=None, bias=None, pos=None):
                self.index = index
                self.startWeight = startWeight
                self.joint = joint
                self.bias = bias
                self.pos  = pos
            # Each of these getX... functions are so we can use a pointer back to the index object rather than storing a number.
            # For example, the numTris section uses Verts

    def getByIdx(self, objLs, index):
        if type(index) is not int:
            index = int(index)
        result = None
        for obj in objLs:
            if obj.index == index:
                return obj

        return result

    def getShaders(self, mObj):
        '''
        When passed a Modo object, this will return a dictionary where each key is a material name,
        and the value is a list of modo.meshgeometry.MeshPolygon objects assigned with that material.
        Example:
        {'Mat2': [modo.MeshPolygon(0, 'mesh026'), modo.MeshPolygon(1, 'mesh026'), modo.MeshPolygon(2, 'mesh026'), modo.MeshPolygon(4, 'mesh026'), modo.MeshPolygon(5, 'mesh026')],
        'Mat1': [modo.MeshPolygon(3, 'mesh026')]}
        '''

        shaders = {}
        for polygon in mObj.geometry.polygons:
            if polygon.materialTag not in shaders:
                shaders[polygon.materialTag] = [polygon]
            else:
                shaders[polygon.materialTag].append(polygon)
        return shaders

    def getMaterialsFromMeshObject(self, meshObj):
        materialList = []

        for poly in meshObj.geometry.polygons:
            if poly.materialTag not in materialList:
                materialList.append(poly.materialTag)

        return materialList

    @property
    def numJoints(self):
        return len(self.joints)
    @property
    def numMeshes(self):
        return len(self.meshes)



def getW(x, y, z):

    t = 1.0 - (x*x) - (y*y) - (z*z)
    if t < 0.0:
        return 0.0
    else:
        return -math.sqrt(t)

def mtxToY(matrix):
    x = [ 1.0, 0.0, 0.0, 0.0 ]
    y = [ 0.0, 0.0,-1.0, 0.0 ]
    z = [ 0.0, 1.0, 0.0, 0.0 ]
    w = [ 0.0, 0.0, 0.0, 1.0 ]

    yMtx = modo.mathutils.Matrix4([x,y,z,w])
    matrix = matrix.__mul__(yMtx)
    return matrix
# modo.Scene().item('origin').rotation.set(origin.asEuler())



def mtxToZ(item):
    matrix = modo.mathutils.Matrix4( item.channel('worldMatrix').get() )
    x = [ 1.0, 0.0, 0.0, 0.0 ]
    y = [ 0.0, 0.0, 1.0, 0.0 ]
    z = [ 0.0, 1.0, 0.0, 0.0 ]
    w = [ 0.0, 0.0, 0.0, 1.0 ]

    yMtx = modo.mathutils.Matrix4([x,y,z,w])
    matrix = matrix.__mul__(yMtx)
    item.position.set( matrix.position )
    item.rotation.set( matrix._MatrixToEuler(matrix) )



