import logging
logging.basicConfig(level=logging.INFO)

from suds.client import Client
from suds.plugin import MessagePlugin
from suds.wsse import *

api = 'ONE_ZERO'
wsdl = 'https://staging.payu.co.za/service/PayUAPI?wsdl'
capture = 'https://staging.payu.co.za/rpp.do'

additional_information = {
    'merchantReference': '123456',
    'supportedPaymentMethods': 'CREDITCARD',
}

safekey = '{CE62CE80-0EFD-4035-87C1-8824C5C46E7F}'
username = '100032'
password = 'PypWWegU'

# Add the required attributes and namespaces for PayU to recognize the request
class PayUPlugin(MessagePlugin):
    def marshalled(self, context):
        username_token = context.envelope.childAtPath('Header/wsse:Security/wsse:UsernameToken')
        username_token.getChild('wsse:Password').set('Type', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText')

client = Client(wsdl, plugins=[PayUPlugin()])

security = Security()
token = UsernameToken(username, password)
security.tokens.append(token)
client.set_options(wsse=security)

def set_transaction(currency_code, amount_in_cents, description, return_url, cancel_url):
    additional_information['returnUrl'] = return_url
    additional_information['cancelUrl'] = cancel_url
    response = client.service.setTransaction(
        Api=api,
        Safekey=safekey,
        TransactionType='PAYMENT',
        AdditionalInformation=additional_information,
        Basket=dict(
            amountInCents=amount_in_cents,
            currencyCode=currency_code,
            description=description,
        )
    )
    return response

def get_transaction(payUReference):
    response = client.service.getTransaction(
        Api=api,
        Safekey=safekey,
        AdditionalInformation={
            'payUReference': payUReference
        }
    )
    return response
