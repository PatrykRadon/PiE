# from the commit https://github.com/pite2020sum/tue-09-45-task1-Gordwick/blob/master/lab2.py
#


import unittest
import task


class FlightCase(unittest.TestCase):
    def setUp(self) -> None:
        self.plane = task.Plane()
        self.initiate_state = self.plane.status()

    def tearDown(self) -> None:
        pass

    def test_plane_initiation(self):
        self.assertEqual(self.plane.status(), self.plane.directions)

    def test_turbulence(self):
        self.plane.apply_turbulence('roll')
        self.assertNotEqual(self.plane.status(), self.initiate_state)

    def test_single_correction(self):
        self.plane.apply_turbulence('roll')
        after_turbulence = self.plane.status()['roll']
        self.plane.apply_correction('roll')
        self.assertLess(abs(self.plane.status()['roll']), abs(after_turbulence))

    def test_negative_correction(self):
        self.plane.correction = task.Corrections(-4)
        self.plane.apply_turbulence('roll')
        after_turbulence = self.plane.status()['roll']
        self.plane.apply_correction('roll')
        self.assertGreater(abs(self.plane.status()['roll']), abs(after_turbulence))

    def test_unknown_attribute(self):
        self.assertRaises(AttributeError, self.plane.fly, 'unknown')

    def test_standard_flight(self):
        self.plane.fly('roll')
        self.assertNotEqual(self.plane.status(), self.initiate_state)

    def test_fly_nowhere(self):
        self.plane.fly_far('roll', 0)
        self.assertEqual(self.plane.status(), self.initiate_state)

    def test_fly_backwards(self):
        self.assertRaises(Exception, self.plane.fly_far, 'roll', -10)

    def test_fly_fraction(self):
        self.assertRaises(TypeError, self.plane.fly_far, 'roll', 0.3)

    def test_fly_unknown_value(self):
        self.assertRaises(TypeError, self.plane.fly_far, 'roll', 'string')

if __name__ == '__main__':
    unittest.main()
