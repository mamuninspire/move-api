from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "SYSTEM")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email,
            password=password,
            **extra_fields
        )
    
    def create_mover(self, email, password, **extra_fields):
        """
        Creates and saves a mover with the given email and password.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_mover", True)
        extra_fields.setdefault("is_customer", False)
        
        
        extra_fields.setdefault("role", "MOVER")

        return self.create_user(
            email,
            password=password,
            **extra_fields
        )
    
    def create_customer(self, email, password, **extra_fields):
        """
        Creates and saves a customer with the given email and password.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_mover", False)
        extra_fields.setdefault("is_customer", True)

        extra_fields.setdefault("role", "CUSTOMER")

        return self.create_user(
            email,
            password=password,
            **extra_fields
        )