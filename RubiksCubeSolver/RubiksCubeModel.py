from abc import ABC;
import sys

from typing import TypeVar

import copy

class RubiksCubeState(object):
    def __init__(self, cubesize: int, flat_in):
        self._cubesize = cubesize
        self._flat = flat_in
    
    @property
    def cubesize(self):
        return self._cubesize
    
    # immutable ref to list flat.  but flat can be modified
    @property
    def flat(self):
        return self._flat



class RubiksCubeActionModel:
    # class that defines the rubiks cube model representation in memory and actions to manipulate the model
    #
    FACEID_U=0
    FACEID_D=1
    FACEID_R=2
    FACEID_L=3
    FACEID_F=4
    FACEID_B=5
    # face layout (for 3x3) , 1-indexed, is:
    # 1 2 3
    # 4 5 6
    # 7 8 9
    # convention is a clockwise rotation
    # 7 4 1
    # 8 5 2
    # 9 6 3
    # orientation and numbering of faces is such that:
    # 1.) you start by looking at the front face.
    # 2.) left, right, front, back are achieved by rotating the cube on the z axis (like a spining top)
    # 3.) top (up)  and bottom (down) are achieved by rotating the cube on the x axis (toward/away from you)

    @staticmethod
    def new_flat(cubesize, fill=None):
        return [(x if fill else None) for x in range(cubesize*cubesize*6)]
    
    @classmethod
    def new_state(cls, cubesize: int, fill=None) -> RubiksCubeState:
        return RubiksCubeState(cubesize, cls.new_flat(cubesize, fill))
    
    
    @staticmethod
    def face_offset(cubesize: int, faceid: int) -> int:
        return cubesize * cubesize * faceid
    
    @classmethod
    def state_get_flat_face(cls, state, faceid):
        start=cls.face_offset(state.cubesize,faceid  )
        end  =cls.face_offset(state.cubesize,faceid+1)
        return state.flat[start:end]
    
    #####

    @classmethod
    def state_rotate_by_faceid(cls, state: RubiksCubeState, faceid: int) -> RubiksCubeState:
        si, so = state, copy.deepcopy(state)

        _edge_rotator = {
            cls.FACEID_U: cls._rotate_U_edges,
            cls.FACEID_D: cls._rotate_D_edges,
            cls.FACEID_R: cls._rotate_R_edges,
            cls.FACEID_L: cls._rotate_L_edges,
            cls.FACEID_F: cls._rotate_F_edges,
            cls.FACEID_B: cls._rotate_B_edges,
        } [faceid]
        
        cls._rotate_helper_just_face(si.cubesize, faceid, si, so)
        _edge_rotator(si.cubesize, si, so)
        cls._rotate_helper_fill_none(si, so)
        return so

    #######

    @classmethod
    def _rotate_helper_just_face(cls, cubesize, faceid, si, so):
        ''' common code for permuting just the face for a given rotation. '''
        face_offset = cls.face_offset(cubesize, faceid)
        for r in range(cubesize):
            for c in range(cubesize):
                so.flat[face_offset + r*cubesize + c ] = si.flat[face_offset + (cubesize-1-c) * cubesize + r]

    @classmethod
    def _rotate_helper_fill_none(cls, si, so):
        for i in range(len(si.flat)):
            if None==so.flat[i]:
                so.flat[i] = si.flat[i]
        return so

    @classmethod
    def _rotate_U_edges(cls, cubesize, si, so):
        for i in range(cubesize):
            # F->L , R->F , B->R , L->B
            so.flat[cls.face_offset(cubesize,cls.FACEID_L) + i] = si.flat[cls.face_offset(cubesize,cls.FACEID_F) + i]
            so.flat[cls.face_offset(cubesize,cls.FACEID_F) + i] = si.flat[cls.face_offset(cubesize,cls.FACEID_R) + i]
            so.flat[cls.face_offset(cubesize,cls.FACEID_R) + i] = si.flat[cls.face_offset(cubesize,cls.FACEID_B) + i]
            so.flat[cls.face_offset(cubesize,cls.FACEID_B) + i] = si.flat[cls.face_offset(cubesize,cls.FACEID_L) + i]
        
        return so

    @classmethod
    def _rotate_D_edges(cls, cubesize, si, so):
        for i in range(cubesize):
            off_bot_edge = (cubesize-1)*cubesize + i
            # B->L, R->B, F->R, L->F
            so.flat[cls.face_offset(cubesize,cls.FACEID_F) + off_bot_edge] = si.flat[cls.face_offset(cubesize,cls.FACEID_L) + off_bot_edge]
            so.flat[cls.face_offset(cubesize,cls.FACEID_R) + off_bot_edge] = si.flat[cls.face_offset(cubesize,cls.FACEID_F) + off_bot_edge]
            so.flat[cls.face_offset(cubesize,cls.FACEID_B) + off_bot_edge] = si.flat[cls.face_offset(cubesize,cls.FACEID_R) + off_bot_edge]
            so.flat[cls.face_offset(cubesize,cls.FACEID_L) + off_bot_edge] = si.flat[cls.face_offset(cubesize,cls.FACEID_B) + off_bot_edge]
        
        return so

    @classmethod
    def _rotate_R_edges(cls, cubesize, si, so):
        for i in range(cubesize):
            # U->B , B->D , D->F , F->U
            off_left_edge  = (cubesize)*i
            off_right_edge = off_left_edge + (cubesize-1)
            off_left_edge_flip = (cubesize -1 -i) * cubesize
            off_right_edge_flip = off_left_edge_flip + (cubesize-1)

            # 3,6,9 -> 7,4,1
            so.flat[cls.face_offset(cubesize,cls.FACEID_B)+off_left_edge_flip] = si.flat[cls.face_offset(cubesize,cls.FACEID_U)+off_right_edge]
            # 7,4,1 -> 3,6,9
            so.flat[cls.face_offset(cubesize,cls.FACEID_D)+off_right_edge]     = si.flat[cls.face_offset(cubesize,cls.FACEID_B)+off_left_edge_flip]
            # 3,6,9 -> 3,6,9 
            so.flat[cls.face_offset(cubesize,cls.FACEID_F)+off_right_edge]     = si.flat[cls.face_offset(cubesize,cls.FACEID_D)+off_right_edge]
            # 3,6,9 -> 3,6,9 
            so.flat[cls.face_offset(cubesize,cls.FACEID_U)+off_right_edge]     = si.flat[cls.face_offset(cubesize,cls.FACEID_F)+off_right_edge]
        
        return so

    @classmethod
    def _rotate_L_edges(cls, cubesize, si, so):
        for i in range(cubesize):
            # U->F , F->D , D->B , B->U
            off_left_edge  = (cubesize)*i
            off_right_edge = off_left_edge + (cubesize-1)
            off_left_edge_flip = (cubesize -1 -i) * cubesize
            off_right_edge_flip = off_left_edge_flip + (cubesize-1)

            # 1,4,7 -> 1,4,7
            so.flat[cls.face_offset(cubesize,cls.FACEID_F)+off_left_edge] = si.flat[cls.face_offset(cubesize,cls.FACEID_U)+off_left_edge]
            # 1,4,7 -> 1,4,7
            so.flat[cls.face_offset(cubesize,cls.FACEID_D)+off_left_edge] = si.flat[cls.face_offset(cubesize,cls.FACEID_F)+off_left_edge]
            # 1,4,7 -> 9,6,3 
            so.flat[cls.face_offset(cubesize,cls.FACEID_B)+off_right_edge_flip] = si.flat[cls.face_offset(cubesize,cls.FACEID_D)+off_left_edge]
            # 9,6,3 -> 1,4,7 
            so.flat[cls.face_offset(cubesize,cls.FACEID_U)+off_left_edge] = si.flat[cls.face_offset(cubesize,cls.FACEID_B)+off_right_edge_flip]
        
        return so

    @classmethod
    def _rotate_F_edges(cls, cubesize, si, so):
        for i in range(cubesize):
            # U->R , R->D , D->L , L->U
            off_top_edge = i
            off_bot_edge = (cubesize-1)*cubesize + i
            off_left_edge  = (cubesize)*i
            off_right_edge = off_left_edge + (cubesize-1)
            off_left_edge_flip = (cubesize -1 -i) * cubesize
            off_right_edge_flip = off_left_edge_flip + (cubesize-1)

            # U->R, 789 -> 147 = be -> le
            so.flat[cls.face_offset(cubesize,cls.FACEID_R)+off_left_edge]  = si.flat[cls.face_offset(cubesize,cls.FACEID_U)+off_bot_edge]
            # R->D, 147 -> 321 = le -> tef
            so.flat[cls.face_offset(cubesize,cls.FACEID_D)+off_top_edge]   = si.flat[cls.face_offset(cubesize,cls.FACEID_R)+off_left_edge_flip]
            # D->L, 123 -> 369 = te -> re
            so.flat[cls.face_offset(cubesize,cls.FACEID_L)+off_right_edge] = si.flat[cls.face_offset(cubesize,cls.FACEID_D)+off_top_edge]
            # L->U, 369 -> 987 = re -> bef
            so.flat[cls.face_offset(cubesize,cls.FACEID_U)+off_bot_edge]   = si.flat[cls.face_offset(cubesize,cls.FACEID_L)+off_right_edge_flip]
        
        return so

    @classmethod
    def _rotate_B_edges(cls, cubesize, si, so):
        for i in range(cubesize):
            # U->L , L->D , D->R , R->U
            off_top_edge = i
            off_bot_edge = (cubesize-1)*cubesize + i
            off_left_edge  = (cubesize)*i
            off_right_edge = off_left_edge + (cubesize-1)
            off_left_edge_flip = (cubesize -1 -i) * cubesize
            off_right_edge_flip = off_left_edge_flip + (cubesize-1)

            # U->L, 123->741 = te->lef
            so.flat[cls.face_offset(cubesize,cls.FACEID_L)+off_left_edge_flip] = si.flat[cls.face_offset(cubesize,cls.FACEID_U)+off_top_edge]
            # L->D, 147->789 = le->be
            so.flat[cls.face_offset(cubesize,cls.FACEID_D)+off_bot_edge]        = si.flat[cls.face_offset(cubesize,cls.FACEID_L)+off_left_edge]
            # D->R, 789->963 = be->ref
            so.flat[cls.face_offset(cubesize,cls.FACEID_R)+off_right_edge_flip] = si.flat[cls.face_offset(cubesize,cls.FACEID_D)+off_bot_edge]
            # R->U, 369->123 = re->te
            so.flat[cls.face_offset(cubesize,cls.FACEID_U)+off_top_edge]        = si.flat[cls.face_offset(cubesize,cls.FACEID_R)+off_right_edge]

        return so
        


####################

class RubiksCube(object):

    def __init__(self, cubesize, state = None):
        self.cubesize = cubesize
        self._state = state if state else RubiksCubeActionModel.new_state(cubesize, fill=True)
    
    @property
    def state(self):
        return self._state
    
    def get_flat_face(self, faceid: int):
        return RubiksCubeActionModel.state_get_flat_face(self.state, faceid)


    def rotate_U(self, inPlace=False):
        return self.rotate_by_faceid(RubiksCubeActionModel.FACEID_U, inPlace=inPlace)
    def rotate_D(self, inPlace=False):
        return self.rotate_by_faceid(RubiksCubeActionModel.FACEID_D, inPlace=inPlace)
    def rotate_R(self, inPlace=False):
        return self.rotate_by_faceid(RubiksCubeActionModel.FACEID_R, inPlace=inPlace)
    def rotate_L(self, inPlace=False):
        return self.rotate_by_faceid(RubiksCubeActionModel.FACEID_L, inPlace=inPlace)
    def rotate_F(self, inPlace=False):
        return self.rotate_by_faceid(RubiksCubeActionModel.FACEID_F, inPlace=inPlace)
    def rotate_B(self, inPlace=False):
        return self.rotate_by_faceid(RubiksCubeActionModel.FACEID_B, inPlace=inPlace)

    def rotate_by_faceid(self, faceid: int, inPlace=False):
        new_state = RubiksCubeActionModel.state_rotate_by_faceid(self.state, faceid)
        rk=self
        if inPlace:
            self._state = new_state
        else:
            rk = RubiksCube(self.cubesize, state=new_state)

        return rk
