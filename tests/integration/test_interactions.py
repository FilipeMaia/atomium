import math
from unittest import TestCase
import atomium

class DistanceTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pdb = atomium.open("tests/integration/files/1lol.cif")


    def test_atom_distances(self):
        # Atom to atom
        atom1 = self.pdb.model.atom(1)
        atom2 = self.pdb.model.atom(2)
        self.assertEqual(round(atom1.distance_to(atom2), 3), 1.496)

        # Atom to point
        self.assertEqual(round(atom1.distance_to([1, 2, 3]), 1), 68.2)
    

    def test_atom_angles(self):
        # Angles between atoms
        atom1 = self.pdb.model.atom(1)
        atom2 = self.pdb.model.atom(2)
        atom3 = self.pdb.model.atom(3)
        self.assertEqual(round(atom1.angle(atom2, atom3), 2), 0.63)
        self.assertEqual(round(atom2.angle(atom1, atom3), 2), 1.91)
        self.assertEqual(round(atom3.angle(atom1, atom2), 2), 0.6)
        self.assertAlmostEqual(sum([
            atom1.angle(atom2, atom3),
            atom2.angle(atom1, atom3),
            atom3.angle(atom1, atom2)
        ]), math.pi, delta=0.001)

        # Angles between points
        self.assertEqual(round(atom1.angle([1, 2, 3], [4, 5, 6]), 2), 0.05)
    

    def test_atoms_in_sphere(self):
        for use_grid in [False, True]:
            if use_grid: self.pdb.model.optimise_distances()

            # Model sphere
            atoms = self.pdb.model.atoms_in_sphere([0, 50, 50], 2)
            self.assertEqual(len(atoms), 1)
            self.assertEqual(list(atoms)[0].id, 881)
            atoms = self.pdb.model.atoms_in_sphere([0, 50, 50], 3)
            self.assertEqual(len(atoms), 5)
            atoms = self.pdb.model.atoms_in_sphere([0, 0, 0], 1)
            self.assertEqual(len(atoms), 0)

            # Model sphere filtering
            atoms = self.pdb.model.atoms_in_sphere([0, 50, 50], 3, element="C")
            self.assertEqual(len(atoms), 4)
            atoms = self.pdb.model.atoms_in_sphere([0, 50, 50], 3, element="S")
            self.assertEqual(len(atoms), 1)
    

    def test_atom_nearby_atoms(self):
        # All atoms
        atom = self.pdb.model.atom(1)
        atoms = atom.nearby_atoms(5)
        self.assertEqual(len(atoms), 15)

        # Filtering
        atoms = atom.nearby_atoms(5, element="C")
        self.assertEqual(len(atoms), 9)
        atoms = atom.nearby_atoms(5, element="O")
        self.assertEqual(len(atoms), 4)
        atoms = atom.nearby_atoms(5, element__regex="O|C")
        self.assertEqual(len(atoms), 13)
        atoms = atom.nearby_atoms(5, residue__name="HIS")
        self.assertEqual(len(atoms), 3)
