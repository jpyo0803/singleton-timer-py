import singleton_timer as st
import time
import random

timer = st.SingletonTimer(allow_overlap=False)


for i in range(100):
  ticket_a = timer.start(tag="A", category="A")
  time.sleep(0.01)
  timer.end(ticket_a)

  ticket_b = timer.start(tag="B", category="B", exclude=(i % 2 == 0))
  time.sleep(0.01)
  timer.end(ticket_b)
  
  ticket_c = timer.start(tag="C", category="C")
  time.sleep(0.01)
  timer.end(ticket_c)


timer.display_log()
timer.display_summary()
