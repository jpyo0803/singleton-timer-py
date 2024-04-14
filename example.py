import singleton_timer as st
import time
import random

timer = st.SingletonTimer()

for i in range(101):
  if i != 0 and i % 50 == 0:
    timer.display_log()
    timer.display_summary()
    timer.reset()
    if i == 100:
      break

  ticket = timer.start(tag=f"Test {i * 3}", category="Test 1 Category")
  time.sleep(random.random() / 100)
  timer.end(ticket)

  ticket = timer.start(tag=f"Test {i * 3 + 1}", category="Test 2 Category", exclude=False)
  time.sleep(random.random() / 100 * 2)
  timer.end(ticket)

  ticket = timer.start(tag=f"Test {i * 3 + 2}", category="Test 3 Category")
  time.sleep(random.random() / 100 * 3)
  timer.end(ticket)
  

  # timer.display_log()
