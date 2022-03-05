import unittest

from RubiksCubeSolver.RubiksCubeModel import RubiksCube, RubiksCubeActionModel
import copy

####################################

# identitycube = RubiksCube(2)
# cube = copy.deepcopy(identitycube)

# # check that each rotation does at least something
# assert(cube.state.flat != cube.rotate_U(inPlace=False).state.flat)
# assert(cube.state.flat != cube.rotate_D(inPlace=False).state.flat)
# assert(cube.state.flat != cube.rotate_R(inPlace=False).state.flat)
# assert(cube.state.flat != cube.rotate_L(inPlace=False).state.flat)
# assert(cube.state.flat != cube.rotate_F(inPlace=False).state.flat)
# assert(cube.state.flat != cube.rotate_B(inPlace=False).state.flat)

# # check if rotation is correct; 4x rotations should have no effect
# # ok
# cube = cube.rotate_U().rotate_U().rotate_U().rotate_U()
# assert(cube.state.flat == identitycube.state.flat)
# cube = cube.rotate_D().rotate_D().rotate_D().rotate_D()
# assert(cube.state.flat == identitycube.state.flat)
# cube = cube.rotate_R().rotate_R().rotate_R().rotate_R()
# assert(cube.state.flat == identitycube.state.flat)
# cube = cube.rotate_L().rotate_L().rotate_L().rotate_L()
# assert(cube.state.flat == identitycube.state.flat)
# cube = cube.rotate_F().rotate_F().rotate_F().rotate_F()
# assert(cube.state.flat == identitycube.state.flat)
# cube = cube.rotate_B().rotate_B().rotate_B().rotate_B()
# assert(cube.state.flat == identitycube.state.flat)


class TestRubiksCube3x3(unittest.TestCase):
    
    @property
    def faceid_list(self):
        return [
            RubiksCubeActionModel.FACEID_U,
            RubiksCubeActionModel.FACEID_D,
            RubiksCubeActionModel.FACEID_R,
            RubiksCubeActionModel.FACEID_L,
            RubiksCubeActionModel.FACEID_F,
            RubiksCubeActionModel.FACEID_B,
        ]

    def test_creation(self):
        expected=[x for x in range(3*3*6)]
        rk = RubiksCube(3)
        self.assertTrue( rk.state.flat == expected )
    
    def test_single_rotation(self):
        flat=[0, 1, 2, 3, 4, 5, 6, 7, 8]
        rotated=[6,3,0, 7,4,1, 8,5,2]

        for fid in self.faceid_list:
            face_offset = 3*3*fid
            flat_face_rotated = [x+face_offset for x in rotated]

            rk = RubiksCube(3)
            rk = rk.rotate_by_faceid(fid)
            self.assertTrue(rk.get_flat_face(fid) == flat_face_rotated)
        
        return True
    
    def test_in_place(self):
        idcube=RubiksCube(3)
        cube=RubiksCube(3)
        cube.rotate_U(inPlace=False)
        self.assertTrue(idcube.state.flat == cube.state.flat)

        cube.rotate_U(inPlace=True)
        self.assertFalse(idcube.state.flat == cube.state.flat)
        
    
    def test_rotation_symmetry(self):
        # foreach face, test 4x rotation that we get the same cube state
        from functools import reduce
        for fid in self.faceid_list:
            rk = RubiksCube(3)
            f= lambda x,_: x.rotate_by_faceid(fid)
            rkrot=reduce(f, range(4), RubiksCube(3))
            self.assertTrue(rk.state.flat == rkrot.state.flat)
