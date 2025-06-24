FUEL_TYPE = (
    ('gasoline', 'Gasoline'),
    ('diesel', 'Diesel'),
    ('electric', 'Electric'),
    ('hybrid', 'Hybrid'),
    ('cng', 'CNG'),
)

TRANSMISSION_TYPE = (
    ("manual", "Manual"),
    ("automatic", "Automatic"),
    ("cvt", "CVT")
)

COMMON_STATUS = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('pending', 'Pending')
)

DOCUMENT_TYPES = (
    ('registration', 'Vehicle Registration'),
    ('insurance', 'Insurance Certificates')
)

DURATION_TYPE_CHOICES = [
    ('HOUR', 'Hour'),
    ('DAY', 'Day'),
]

SERVICE_STATUS = (
    ("available", "Available"),
    ("busy", "Busy"),
    ("off_service", "Off Service")
)

DELIVERY_STATUS = (
    ("waiting", "Waiting for Request Acceptance"),
    ("request_accepted", "Delivery Request Accepted"),
    ("picked_up", "Parcel Picked Up"),
    ("on_the_way", "Parcel On the Way"),
    ("delivered", "Parcel Delivered")
)

LICENSE_VERIFICATION_STATUS = (("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"))