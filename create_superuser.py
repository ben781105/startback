from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='ben').exists():
    User.objects.create_superuser('ben','benardleno77@gmail.com','1105')
