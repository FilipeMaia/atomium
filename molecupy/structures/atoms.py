"""This module contains classes for atoms and their bonds. It is perfectly
possible, though probably not very useful, to describe a molecular system solely
in terms of the classes in this module - a collection of atoms bonded to each
other."""

import math
import warnings
from ..exceptions import LongBondWarning

class GhostAtom:
    """This class represents atoms with no location. It is a 'ghost' in the
    sense that it is accounted for in terms of its mass, but it is 'not really
    there' because it has no location and cannot form bonds.

    The reason for the distinction between ghost atoms and 'real' atoms comes
    from PDB files, where often not all the atoms in the studied molecule can
    be located in the (for example) electron density data and so there are no
    coordinates for them. They do 'exist' but they are missing from the PDB file
    coordinates.

    They are described in terms of an Atom ID, an Atom name, and an element.
    They have mass but no location, and they can still be associated with
    molecules and models.

    In terms of awareness of their context, all atoms know the molecule they are
    part of (which must either be a :py:class:`.Residue` or
    :py:class:`.SmallMolecule`), and the overall :py:class:`.Model` they exist
    within.

    :param str element: The atom's element.
    :param int atom_id: The atom's id.
    :param str atom_name: The atom's name."""

    def __init__(self, element, atom_id, atom_name):
        if not isinstance(element, str):
            raise TypeError("element must be str, not '%s'" % str(element))
        if not 0 < len(element) <= 2:
            raise ValueError("element must be of length 1 or 2, not %s" % element)
        self._element = element
        if not isinstance(atom_id, int):
            raise TypeError("atom_id must be int, not '%s'" % str(atom_id))
        self._atom_id = atom_id
        if not isinstance(atom_name, str):
            raise TypeError("atom_name must be str, not '%s'" % str(atom_name))
        self._atom_name = atom_name
        self._molecule = None


    def __repr__(self):
        return "<%s %i (%s)>" % (
         self.__class__.__name__, self._atom_id, self._atom_name
        )


    def element(self, element=None):
        """Returns or sets the atom's element. This must be one or two character
        string representing the atom's symbol on the periodic table (though no
        check is made that the symbol corresponds to a real element, so you are
        free to call elements 'X' etc.).

        :param str element: If given, the atom's element will be set to this.
        :rtype: ``str``"""

        if element is None:
            return self._element
        else:
            if not isinstance(element, str):
                raise TypeError("element must be str, not '%s'" % str(element))
            if not 0 < len(element) <= 2:
                raise ValueError(
                 "element must be of length 1 or 2, not %s" % element
                )
            self._element = element


    def atom_id(self):
        """Returns the atom's ID. This should be a unique integer - most
        structures that contain elements will not allow you to have two atoms
        with the same ID.

        The ID is set when the atom is created and cannot be changed after this
        time.

        :rtype: ``int``"""

        return self._atom_id


    def atom_name(self, atom_name=None):
        """Returns or sets the atom's name. In PDB files this corresponds to the
        'Atom type' - so alpha carbons will be 'CA' for example.

        :param str name: If given, the atom's name will be set to this.
        :rtype: ``str``"""

        if atom_name is None:
            return self._atom_name
        else:
            if not isinstance(atom_name, str):
                raise TypeError("atom_name must be str, not '%s'" % str(atom_name))
            self._atom_name = atom_name


    def mass(self):
        """Returns the atom's mass. This is calculated from its element - if you
        have set the element to be some made up symbol like 'X' this will return
        0.

        :rtype: ``float``"""

        return PERIODIC_TABLE.get(self.element().upper(), 0)


    def molecule(self):
        """Returns the :py:class:`.SmallMolecule` or :py:class:`.Residue` the
        atom is a part of."""

        return self._molecule


    def model(self):
        """Returns the :py:class:`.Model` the atom is a part of.

        :rtype: ``Model``"""

        try:
            return self.molecule().model()
        except AttributeError:
            return self.molecule().chain().model()
        except AttributeError:
            return None



class Atom(GhostAtom):
    """Base class: :py:class:`GhostAtom`

    Represents standard atoms which have Cartesian coordinates, and which can
    form bonds with other atoms.

    They are distinguished from :py:class:`GhostAtom` objects because they have
    a location in three dimensional space, though they inherit some properties
    from that more generic class of atom.

    :param float x: The atom's x-coordinate.
    :param float y: The atom's y-coordinate.
    :param float z: The atom's z-coordinate.
    :param str element: The atom's element.
    :param int atom_id: The atom's id.
    :param str atom_name: The atom's name."""

    def __init__(self, x, y, z, *args):
        if not isinstance(x, float):
            raise TypeError("x coordinate must be float, not '%s'" % str(x))
        self._x = x
        if not isinstance(y, float):
            raise TypeError("y coordinate must be float, not '%s'" % str(y))
        self._y = y
        if not isinstance(z, float):
            raise TypeError("z coordinate must be float, not '%s'" % str(z))
        self._z = z
        self._bonds = set()
        GhostAtom.__init__(self, *args)


    def x(self, x=None):
        """Returns or sets the atom's x coordinate.

        :param float x: If given, the atom's x coordinate will be set to this.
        :rtype: ``float``"""

        if x is None:
            return self._x
        else:
            if not isinstance(x, float):
                raise TypeError("x coordinate must be float, not '%s'" % str(x))
            self._x = x


    def y(self, y=None):
        """Returns or sets the atom's y coordinate.

        :param float y: If given, the atom's y coordinate will be set to this.
        :rtype: ``float``"""

        if y is None:
            return self._y
        else:
            if not isinstance(y, float):
                raise TypeError("y coordinate must be float, not '%s'" % str(y))
            self._y = y


    def z(self, z=None):
        """Returns or sets the atom's z coordinate.

        :param float z: If given, the atom's z coordinate will be set to this.
        :rtype: ``float``"""

        if z is None:
            return self._z
        else:
            if not isinstance(z, float):
                raise TypeError("z coordinate must be float, not '%s'" % str(z))
            self._z = z


    def location(self):
        """Returns the atom's xyz coordinates in the form of a (x, y, z) tuple.

        :rtype: ``tuple``"""

        return (self.x(), self.y(), self.z())


    def distance_to(self, other_atom):
        """Returns the distance between this atom and another, in Angstroms.
        Alternatively, an :py:class:`.AtomicStructure` can be provided and the
        method will return the distance between this atom and that structure's
        :py:meth:`~.molecules.AtomicStructure.center_of_mass`.

        :param other_atom: The other atom or atomic structure.
        :rtype: ``float``"""

        from .molecules import AtomicStructure
        if not isinstance(other_atom, Atom) and not isinstance(other_atom, AtomicStructure):
            raise TypeError(
             "Can only get distance between Atoms, not '%s'" % str(other_atom)
            )
        x, y, z = other_atom.location() if isinstance(other_atom, Atom)\
         else other_atom.center_of_mass()
        x_sum = math.pow((x - self.x()), 2)
        y_sum = math.pow((y - self.y()), 2)
        z_sum = math.pow((z - self.z()), 2)
        distance = math.sqrt(x_sum + y_sum + z_sum)
        return distance


    def bonds(self):
        """The set of :py:class:`Bond` objects belonging to this atom.

        :returns: ``set`` of :py:class:`Bond` objects."""

        return self._bonds


    def bond_to(self, other_atom):
        """Creates a :py:class:`Bond` between this atom and another.

        :param Atom other_atom: The other atom."""

        Bond(self, other_atom)


    def bonded_atoms(self):
        """The set of :py:class:`Atom` objects bonded to this atom.

        :returns: ``set`` of :py:class:`Atom` objects."""

        bonded_atoms = set()
        for bond in self.bonds():
            for atom in bond.atoms():
                bonded_atoms.add(atom)
        if self in bonded_atoms: bonded_atoms.remove(self)
        return bonded_atoms


    def get_bond_with(self, other_atom):
        """Returns the specific :py:class:`Bond` between this atom and some
        other atom, if it exists. If not, it returns ``None``.

        :param Atom other_atom: The other atom.
        :rtype: ``Bond``"""

        for bond in self.bonds():
            if other_atom in bond.atoms():
                return bond


    def break_bond_with(self, other_atom):
        """Removes the specific :py:class:`Bond` between this atom and some
        other atom, if it exists. If there is no bond, this method has no
        effect.

        :param Atom other_atom: The other atom."""

        bond = self.get_bond_with(other_atom)
        if bond:
            bond.delete()


    def accessible_atoms(self, already_checked=None):
        """The set of all :py:class:`Atom` objects that can be accessed by
        following bonds. The method will traverse all accessible atom nodes on
        the graph created by the bonds and, as long as there exists some path
        between this atom and some other, this method will return it in its set.

        :returns: ``set`` of :py:class:`Atom` objects."""

        already_checked = already_checked if already_checked else set()
        already_checked.add(self)
        while len(self.bonded_atoms().difference(already_checked)) > 0:
            picked = list(self.bonded_atoms().difference(already_checked))[0]
            picked.accessible_atoms(already_checked)
        already_checked_copy = already_checked.copy()
        already_checked_copy.discard(self)
        return already_checked_copy


    def local_atoms(self, distance, include_hydrogens=True):
        """Returns all :py:class:`Atom` objects within a given distance of
        this atom (within a model). If this atom is not associated with a
        :py:class:`.Model`, it will return an empty set, because they will be
        invisible to it. Similarly any atoms nearby that are not associated with
        the same :py:class:`.Model` will be invisible to this method.

        By default, hydrogen atoms will be included in the search but if you
        don't care about hydrogens you can disable this.

        :param distance: The cutoff in Angstroms to use.
        :param bool include_hydrogens: determines whether to include hydrogen atoms.
        :returns: ``set`` of :py:class:`Atom` objects."""

        if self.model():
            return set([atom for atom in self.model().atoms()
             if atom.distance_to(self) <= distance and atom is not self
              and (include_hydrogens or atom.element().upper() != "H")])
        else:
            return set()



class Bond:
    """Represents a chemical bond between two :py:class:`Atom` objects -
    covalent or ionic.

    Normally you would not need to directly instantiate this class yourself, as
    the :py:meth:`~Atom.bond_to` method is a more convenient way of connecting
    two atoms, and which creates a Bond object for you. This is the object type
    that will be returned if you access the atom's bonds directly.

    If you *do* create an instance manually, the two atoms will have their bonds
    updated autoamtically.

    If you try to bond too atoms that are more than 20 Ångstroms apart, a
    warning will be issued.

    :param ``Atom`` atom1: The first atom.
    :param ``Atom`` atom2: The second atom.
    :raises ValueError: if you try to bond an atom to itself."""

    def __init__(self, atom1, atom2):
        if not isinstance(atom1, Atom) or not isinstance(atom2, Atom):
            raise TypeError(
             "Can only create bond between Atoms, not %s and %s" % (
              str(atom1), str(atom2)
             )
            )
        if atom1 is atom2:
            raise ValueError("Cannot bond %s to itself." % str(atom1))
        if atom1.distance_to(atom2) >= 20:
            warnings.warn(LongBondWarning(
             "Bond between Atom %i and Atom %i is %.1f Angstroms long" % (
              atom1.atom_id(), atom2.atom_id(), atom1.distance_to(atom2)
             )
            ))
        self._atoms = set((atom1, atom2))
        atom1.bonds().add(self)
        atom2.bonds().add(self)


    def __repr__(self):
        id1, id2 = sorted([atom.atom_id() for atom in self._atoms])
        return "<Bond between Atom %i and Atom %i>" % (id1, id2)


    def atoms(self):
        """Returns the two atoms in this bond.

        :returns: ``set`` of :py:class:`Atom`"""

        return set(self._atoms)


    def bond_length(self):
        """The length of the bond in Angstroms.

        :rtype: ``float``"""

        atom1, atom2 = self._atoms
        return atom1.distance_to(atom2)


    def delete(self):
        """Removes the bond and updates the two atoms. Unless you have manually
        created some other reference, this will remove all references to the
        bond and it will eventually removed by garbage collection."""

        atom1, atom2 = tuple(self._atoms)
        atom1.bonds().remove(self)
        atom2.bonds().remove(self)



PERIODIC_TABLE = {
 "H": 1.0079, "HE": 4.0026, "LI": 6.941, "BE": 9.0122, "B": 10.811,
 "C": 12.0107, "N": 14.0067, "O": 15.9994, "F": 18.9984, "NE": 20.1797,
 "NA": 22.9897, "MG": 24.305, "AL": 26.9815, "SI": 28.0855, "P": 30.9738,
 "S": 32.065, "CL": 35.453, "K": 39.0983, "AR": 39.948, "CA": 40.078,
 "SC": 44.9559, "TI": 47.867, "V": 50.9415, "CR": 51.9961, "MN": 54.938,
 "FE": 55.845, "NI": 58.6934, "CO": 58.9332, "CU": 63.546, "ZN": 65.39,
 "GA": 69.723, "GE": 72.64, "AS": 74.9216, "SE": 78.96, "BR": 79.904,
 "KR": 83.8, "RB": 85.4678, "SR": 87.62, "Y": 88.9059, "ZR": 91.224,
 "NB": 92.9064, "MO": 95.94, "TC": 98, "RU": 101.07, "RH": 102.9055,
 "PD": 106.42, "AG": 107.8682, "CD": 112.411, "IN": 114.818, "SN": 118.71,
 "SB": 121.76, "I": 126.9045, "TE": 127.6, "XE": 131.293, "CS": 132.9055,
 "BA": 137.327, "LA": 138.9055, "CE": 140.116, "PR": 140.9077, "ND": 144.24,
 "PM": 145, "SM": 150.36, "EU": 151.964, "GD": 157.25, "TB": 158.9253,
 "DY": 162.5, "HO": 164.9303, "ER": 167.259, "TM": 168.9342, "YB": 173.04,
 "LU": 174.967, "HF": 178.49, "TA": 180.9479, "W": 183.84, "RE": 186.207,
 "OS": 190.23, "IR": 192.217, "PT": 195.078, "AU": 196.9665, "HG": 200.59,
 "TL": 204.3833, "PB": 207.2, "BI": 208.9804, "PO": 209, "AT": 210, "RN": 222,
 "FR": 223, "RA": 226, "AC": 227, "PA": 231.0359, "TH": 232.0381, "NP": 237,
 "U": 238.0289, "AM": 243, "PU": 244, "CM": 247, "BK": 247, "CF": 251,
 "ES": 252, "FM": 257, "MD": 258, "NO": 259, "RF": 261, "LR": 262, "DB": 262,
 "BH": 264, "SG": 266, "MT": 268, "RG": 272, "HS": 277
}
