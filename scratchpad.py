from P4 import P4, P4Exception

p4 = P4()
p4.connect()

# p4.run_login()
user = p4.run_user("-o", "jlindgren")
user2 = p4.fetch_user("new_user")

print(user)