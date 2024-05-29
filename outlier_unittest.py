import singleton_timer as st
import time

timer = st.SingletonTimer()

for i in range(101):
  t = timer.start(tag='Test', category='Test')
  time.sleep(i * 0.01)
  timer.end(t)

timer.display_summary()