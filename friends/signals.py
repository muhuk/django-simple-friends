from django.dispatch import Signal


friendship_accepted = Signal()


friendship_declined = Signal(providing_args=['cancelled'])
