import unittest
from server import Server

class TestClojureMetaphors(unittest.TestCase):
    """A garden where Python blossoms with Clojure's wisdom"""
    
    def test_immutable_roots(self):
        """Like a tree's roots, immutability provides stability"""
        server = Server()
        # Test immutability patterns
        self.assertEqual(server.get_state(), "initial")
        with self.assertRaises(AttributeError):
            server.state = "modified"
            
    def test_functional_flow(self):
        """Rivers flow without changing their banks - pure functions"""
        server = Server()
        result = server.process_data([1, 2, 3])
        self.assertEqual(result, [2, 3, 4])
        # Original data remains unchanged
        self.assertEqual(server.get_data(), [1, 2, 3])
        
    def test_composition_as_ecosystem(self):
        """An ecosystem thrives through composition"""
        server = Server()
        composed = server.compose_functions(
            lambda x: x + 1,
            lambda x: x * 2
        )
        self.assertEqual(composed(3), 8)  # (3 + 1) * 2
        
    def test_persistent_data_structures(self):
        """Like rings in a tree, we add without destroying"""
        server = Server()
        original = server.get_data()
        modified = server.update_data(4)
        self.assertEqual(modified, [1, 2, 3, 4])
        self.assertEqual(server.get_data(), original)

if __name__ == '__main__':
    unittest.main()
