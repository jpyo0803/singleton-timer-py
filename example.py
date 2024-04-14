import singleton_timer as st

timer = st.SingletonTimer()
ticket = timer.start(tag = "setest")
ticket = timer.start(tag = "setest")