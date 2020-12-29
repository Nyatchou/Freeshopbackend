MALE = "male"
FEMALE = "female"
OTHER = "other"
SEX_CHOICES = (
    (MALE, MALE),
    (FEMALE, FEMALE),
    (OTHER, OTHER),
)
SIGNUP_TOKEN = 'SIGNUP_TOKEN'
PASSWORD_TOKEN = 'PASSWORD_TOKEN'
EMAIL_TOKEN = 'EMAIL_TOKEN'
TOKEN_TYPES = (
    (SIGNUP_TOKEN, SIGNUP_TOKEN),
    (PASSWORD_TOKEN, PASSWORD_TOKEN),
    (EMAIL_TOKEN, EMAIL_TOKEN),
)
email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


GOOGLE_REST_AUTH = '/auth/rest-auth/google/'
FACEBOOK_REST_AUTH = '/auth/rest-auth/facebook/'