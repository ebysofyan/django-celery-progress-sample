from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Generating fake user by running python manage.py generate_user"

    def handle(self, *args, **kwargs):
        for i in range(0, 500):
            User.objects.create_user(
                username="username_%s" % i,
                password="password_%s_123" % i,
                email="username_%s@email.com" % i,
                first_name="first_name_%s" % i,
                last_name="last_name_%s" % i,
                is_superuser=bool(i % 2 == 0),
                is_staff=bool(i % 2 != 0)
            )
            print("Insrting item %s" % i)
