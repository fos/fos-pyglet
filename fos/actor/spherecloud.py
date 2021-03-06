import numpy as np

from fos.lib.pyglet.gl import *

from fos import Actor
from fos.data import get_sphere

class SphereCloud(Actor):
    
    def __init__(self, positions, 
                 radii = None,
                 colors = None,
                 force_centering = False,
                 affine = None,
                 *args, **kwargs):
                   
        """ Draw a set of spheres in 3D """
        super(SphereCloud, self).__init__()

        if affine == None:
            # create a default affine
            self.affine = np.eye(4, dtype = np.float32)
        else:
            self.affine = affine
            
        self._update_glaffine()
        
        self.positions = positions
        n = len(positions)
        if colors == None:
            # default colors
            self.colors = np.array( [[1,1,1,1]], dtype = np.float32).repeat(len(self.positions),axis=0)            
        else:
            self.colors = colors.astype( np.ubyte )

        if radii == None:
            # default colors
            self.radii = np.array( [1.0], dtype = np.float32).repeat(len(self.positions),axis=0)            
        else:
            assert(len(positions) == len(radii))
            self.radii = radii

        # create vertices / faces for the primitive
        # which is a sphere in this actor
        mys = np.load(get_sphere())
        v = mys['vertices'].astype(np.float32)
        f = mys['faces'].astype(np.uint32)
        lv = v.shape[0]
        lf = f.shape[0]
        # allocate memory
        vertices = np.zeros( (lv * n, 3), np.float32 )
        faces =  np.zeros( (lf * n, 3), np.uint32 )
        vertexcolors =  np.zeros( (lv * n, 4), np.float32 )
        for i, n in enumerate(range(n)):
            # scale the unit-sphere by the radius
            vertices[i*lv:((i+1)*lv),:] = v * self.radii[i] + self.positions[i,:]
            # add the number of vertices
            faces[i*lf:((i+1)*lf),:] = f + (i * lv)
            # coloring the vertices
            vertexcolors[i*lv:((i+1)*lv),:] = self.colors[i,:].reshape( (1, 4) ).repeat(lv, axis=0)
            
        self.vertices = vertices
        self.faces = faces.astype(np.uint32)
        self.colors = vertexcolors.astype(np.float32)
        self.show_aabb = True        
        self.make_aabb(margin = 0)
        
        # bind the vertex arrays
        self.vert_ptr = self.vertices.ctypes.data
        self.face_ptr = self.faces.ctypes.data
        self.color_ptr = self.colors.ctypes.data
        self.el_count = len(self.faces) * 3
        
        
    def update(self, dt):
        pass
        
    def draw(self):
      
        glPushMatrix()
        glMultMatrixf(self.glaffine)
        glEnable (GL_BLEND)   
        #glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)        
        glVertexPointer(3, GL_FLOAT, 0, self.vert_ptr)                             
        glColorPointer(4, GL_FLOAT, 0, self.color_ptr)
        glDrawElements(GL_TRIANGLES, self.el_count, GL_UNSIGNED_INT, self.face_ptr)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        if self.show_aabb:
            self.draw_aabb()
        glPopMatrix()
