import singleton_timer as st
import time

timer = st.SingletonTimer()

ticket = timer.start(tag="Test 1", category="Test 1 Category")
time.sleep(0.0123)
timer.end(ticket)

ticket = timer.start(tag="Test 2", category="Test 2 Category", exclude=True)
time.sleep(0.0567)
timer.end(ticket)

ticket = timer.start(tag="Test 3", category="Test 3 Category")
time.sleep(0.0789)
timer.end(ticket)

timer.display_log()
