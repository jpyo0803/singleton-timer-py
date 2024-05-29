import singleton_timer as st
import time

timer = st.SingletonTimer()

for i in range(101):
  t = timer.start(tag='Test', category='Test')
  time.sleep(i * 0.001)
  timer.end(t)

for i in range(101):
  t = timer.start(tag='Test2', category='Test2')
  time.sleep(i * 0.005)
  timer.end(t)

timer.display_summary()