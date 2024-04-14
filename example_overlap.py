import singleton_timer as st
import time
import random

timer = st.SingletonTimer(allow_overlap=True)


for _ in range(3):
  ticket_a = timer.start(tag="A", category="A")
  time.sleep(1)
  ticket_b = timer.start(tag="B", category="B")
  time.sleep(1)
  ticket_c = timer.start(tag="C", category="C")
  time.sleep(1)
  timer.end(ticket_a)
  time.sleep(1)
  timer.end(ticket_b)
  time.sleep(1)
  timer.end(ticket_c)

  ticket_d = timer.start(tag="D", category="D")
  time.sleep(1)
  ticket_e = timer.start(tag="E", category="E")
  time.sleep(1)
  timer.end(ticket_e)
  time.sleep(1)
  timer.end(ticket_d)

# Total latency must be 8, N = 3

timer.display_log()
timer.display_summary()
