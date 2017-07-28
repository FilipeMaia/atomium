from unittest import TestCase
from unittest.mock import Mock, patch
from atomium.structures.chains import ResidueSequence
from atomium.structures.molecules import Residue, AtomicStructure
from atomium.structures.atoms import Atom

class ResidueSequenceTest(TestCase):

    def setUp(self):
        self.residue1 = Mock(Residue)
        self.residue2 = Mock(Residue)
        self.atom1, self.atom2 = Mock(Atom), Mock(Atom)
        self.atom3, self.atom4 = Mock(Atom), Mock(Atom)
        self.residue1.atoms.return_value = set([self.atom1, self.atom2])
        self.residue2.atoms.return_value = set([self.atom3, self.atom4])
        self.atom1.residue.return_value = self.residue1
        self.atom2.residue.return_value = self.residue1
        self.atom3.residue.return_value = self.residue2
        self.atom4.residue.return_value = self.residue2



class ResidueSequenceCreationTests(ResidueSequenceTest):

    @patch("atomium.structures.molecules.AtomicStructure.__init__")
    def test_can_create_residue_sequence(self, mock_init):
        mock_init.return_value = None
        sequence = ResidueSequence(self.residue1, self.residue2)
        self.assertIsInstance(sequence, AtomicStructure)
        self.assertEqual(mock_init.call_count, 1)
        args, kwargs = mock_init.call_args_list[0]
        self.assertEqual(args[0], sequence)
        self.assertEqual(set(args[1:]), set(
         [self.atom1, self.atom2, self.atom3, self.atom4]
        ))
        self.assertEqual(sequence._residues, [self.residue1, self.residue2])


    def test_residue_sequence_needs_residues(self):
        with self.assertRaises(TypeError):
            ResidueSequence(self.residue1, "self.residue2")


    def test_residue_needs_at_least_one_residue(self):
        with self.assertRaises(ValueError):
            ResidueSequence()



class ResidueSequenceReprTests(ResidueSequenceTest):

    def test_residue_sequence_repr(self):
        sequence = ResidueSequence(self.residue1, self.residue2)
        self.assertEqual(str(sequence), "<ResidueSequence (2 residues)>")



class ResidueSequenceLenTests(ResidueSequenceTest):

    def test_residue_sequence_len(self):
        sequence = ResidueSequence(self.residue1, self.residue2)
        self.assertEqual(len(sequence), 2)



class ResidueSequenceLengthTests(ResidueSequenceTest):

    @patch("atomium.structures.chains.ResidueSequence.__len__")
    def test_residue_sequence_lenght_is_len(self, mock_len):
        mock_len.return_value = 100
        sequence = ResidueSequence(self.residue1, self.residue2)
        self.assertEqual(sequence.length(), 100)



class ResidueSequenceIterableTests(ResidueSequenceTest):

    def test_residue_sequence_is_iterable(self):
        sequence = ResidueSequence(self.residue1, self.residue2)
        for residue, correct_residue in zip(sequence, (self.residue1, self.residue2)):
            self.assertEqual(residue, correct_residue)



class ResidueSequenceResiduesTests(ResidueSequenceTest):

    def test_residues_by_default_returns_residues(self):
        sequence = ResidueSequence(self.residue1, self.residue2)
        self.assertEqual(sequence.residues(), tuple(sequence._residues))


    @patch("atomium.structures.molecules.AtomicStructure.residues")
    def test_residues_uses_parent_method_for_search_terms(self, mock_residues):
        mock_residues.return_value = set([self.residue2, self.residue1])
        sequence = ResidueSequence(self.residue1, self.residue2)
        residues = sequence.residues(name="A")
        mock_residues.assert_called_with(sequence, name="A")
        self.assertEqual(residues, (self.residue1, self.residue2))



class ResidueSequenceResidueAdditionTests(ResidueSequenceTest):

    @patch("atomium.structures.molecules.AtomicStructure.add_residue")
    def test_adding_residue_to_sequence_updates_residues(self, mock_add):
        sequence = ResidueSequence(self.residue1)
        sequence.add_residue(self.residue2)
        mock_add.assert_called_with(sequence, self.residue2)
        self.assertEqual(sequence._residues, [self.residue1, self.residue2])



class ResidueSequenceResidueRemovalTests(ResidueSequenceTest):

    @patch("atomium.structures.molecules.AtomicStructure.remove_residue")
    def test_removing_residue_from_sequence_updates_residues(self, mock_remove):
        sequence = ResidueSequence(self.residue1, self.residue2)
        sequence.remove_residue(self.residue2)
        mock_remove.assert_called_with(sequence, self.residue2)
        self.assertEqual(sequence._residues, [self.residue1])