import singleton_timer as st
import time
import random

timer = st.SingletonTimer()

for i in range(1001):
  if i != 0 and i % 500 == 0:
    timer.display_summary()
    timer.reset()
    if i == 1000:
      break

  ticket = timer.start(tag=f"Test {i * 3}", category="Test 1 Category")
  time.sleep(random.random() / 1000)
  timer.end(ticket)

  ticket = timer.start(tag=f"Test {i * 3 + 1}", category="Test 2 Category", exclude=True)
  time.sleep(random.random() / 1000 * 2)
  timer.end(ticket)

  ticket = timer.start(tag=f"Test {i * 3 + 2}", category="Test 3 Category")
  time.sleep(random.random() / 1000 * 3)
  timer.end(ticket)
  

  # timer.display_log()
