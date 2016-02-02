import logging
logging.basicConfig(level=logging.DEBUG)

from suds.client import Client
from suds.plugin import MessagePlugin
from suds.wsse import *

wsdl = 'https://staging.payu.co.za/service/PayUAPI?wsdl'
capture = 'https://staging.payu.co.za/rpp.do'
username = '100032'
password = 'PypWWegU'

class PayUPlugin(MessagePlugin):
    def marshalled(self, context):
        username_token = context.envelope.childAtPath('Header/wsse:Security/wsse:UsernameToken')
        username_token.getChild('wsse:Password').set('Type', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText')

client = Client(wsdl, plugins=[PayUPlugin()])

security = Security()
token = UsernameToken(username, password)
security.tokens.append(token)
client.set_options(wsse=security)

print client.service.setTransaction(
    Api='ONE_ZERO',
    Safekey='{CE62CE80-0EFD-4035-87C1-8824C5C46E7F}',
    TransactionType='PAYMENT',
    AdditionalInformation=dict(
        merchantReference='123456',
        supportedPaymentMethods='CREDITCARD',
        returnUrl='http://return.example.com',
        cancelUrl='http://cancel.example.com'
    ),
    Basket=dict(
        amountInCents=1000,
        currencyCode='ZAR',
        description='Something'
    )
)
