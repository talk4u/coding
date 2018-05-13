def is_student(user):
    return user.groups.filter(name='student').exists()
