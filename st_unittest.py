import unittest
import singleton_timer as st


class SingletonTimerTest(unittest.TestCase):
    def test_singleton(self):
        timer = st.SingletonTimer()
        timer2 = st.SingletonTimer()
        self.assertTrue(timer is timer2)

    def test_allow_overlap(self):
        timer = st.SingletonTimer(allow_overlap=True)
        self.assertTrue(timer.get_allow_overlap())
        timer.start(tag="A")
        timer.start(tag="B")
        timer.start(tag="C")
        self.assertEqual(timer.get_overlap_counter(), 3)


if __name__ == '__main__':
    unittest.main()
