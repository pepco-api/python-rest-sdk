# coding: utf-8
from __future__ import absolute_import
import json
from .compat import HTTPError, Request, urlopen, urlencode
from Crypto.Util import number
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from datetime import datetime
from base64 import b64encode, b64decode
from xml.dom import minidom

# API Error for catching Exceptions
class ApiError(Exception):
    def __init__(self, code, description=''):
        super(ApiError, self).__init__(
            'Result code: %s (%s)' % (code, description))
        self.code = code

########################################
# Pasargad Payment API Wrapper
# -----
#
# @author: Reza Seyf <rseyf@hotmail.com>
#
# ######################################
class Pasargad(object):
    ACTION_PURCHASE = "1003"
    URL_GET_TOKEN = "https://pep.shaparak.ir/Api/v1/Payment/GetToken"
    URL_PAYMENT_GATEWAY = "https://pep.shaparak.ir/payment.aspx"
    URL_CHECK_TRANSACTION = "https://pep.shaparak.ir/Api/v1/Payment/CheckTransactionResult"
    URL_VERIFY_PAYMENT = "https://pep.shaparak.ir/Api/v1/Payment/VerifyPayment"
    URL_REFUND = "https://pep.shaparak.ir/Api/v1/Payment/RefundPayment"

    ### Pasargad Constructor ====================
    def __init__(self, merchant_code, terminal_id, redirect_url, certification_file):
        # type: (str, str, str, str) -> dict
        """
        :param merchant_code: Merchant Code of the merchant
        :param terminal_id: TerminalId of the merchant
        :param redirect_url: Redirect URL
        :param certification_file:  Certificate file location
        """
        self.merchant_code = merchant_code
        self.terminal_id = terminal_id
        self.redirect_url = redirect_url
        self.certification_file = certification_file
        self.key_pair = self._convertXMLKeyToPem(self.certification_file)

    ### Make Sign Data ====================
    def _make_sign(self, data):
        # type: (dict) -> bytes
        keyPair = self.key_pair
        # Sign the message using the PKCS#1 v1.5 signature scheme (RSASP1)
        serializedData = json.dumps(data).encode('utf8')
        hash = SHA1.new(serializedData)
        signer = PKCS115_SigScheme(keyPair)
        signature = signer.sign(hash)
        finalSign = b64encode(signature)
        return finalSign

    ### Process RSA key ====================
    def _processXmlNode(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        string = ''.join(rc)
        return number.bytes_to_long(b64decode(string))

    def _convertXMLKeyToPem(self, xmlPrivateKeyFile):
        with open(xmlPrivateKeyFile, 'rb') as pkFile:
            xmlPrivateKey = pkFile.read()
        rsaKeyValue = minidom.parseString(xmlPrivateKey)
        modulus = self._processXmlNode(
            rsaKeyValue.getElementsByTagName('Modulus')[0].childNodes)
        exponent = self._processXmlNode(
            rsaKeyValue.getElementsByTagName('Exponent')[0].childNodes)
        d = self._processXmlNode(
            rsaKeyValue.getElementsByTagName('D')[0].childNodes)
        p = self._processXmlNode(
            rsaKeyValue.getElementsByTagName('P')[0].childNodes)
        q = self._processXmlNode(
            rsaKeyValue.getElementsByTagName('Q')[0].childNodes)
        privateKey = RSA.construct((modulus, exponent, d, p, q))
        return privateKey


    ### Generate Timestamp in format of "Y/m/d H:i:s" ========
    def _generate_timestamp(self):
        return datetime.today().strftime('%Y/%m/%d %H:%M:%S')

    ### API Request Builder ============================
    def _requestBuilder(self, url, data, method='POST'):
        # type: (str, dict, str) -> dict
        request = Request(url, headers={
            'Accept': 'application/json',
            'Sign': self._make_sign(data),
        })

        # serialize json
        payload = json.dumps(data)
        request.data = payload.encode("utf-8")
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: method
        try:
            response = urlopen(request)
        except HTTPError as e:
            response = e

        response = json.loads(response.read().decode('utf-8'))
        if response['IsSuccess'] != True:
            raise ApiError(400, response['Message'])
        else:
            return response

    ### Generate Redirect Address for payment ====================================
    def redirect(self, amount, invoice_number, invoice_date, mobile='', email=''):
        # type: (str, str, str, str, str) -> dict
        """
        Generate Payment URL 
        :param amount: Invoice amount
        :param invoice_number: invoice number
        :param invoice_date: Invoice date in format of "Y/m/d H:i:s"
        :param mobile: optional - invoice owner mobile number
        :param email:  optional - invoice owner email address
        :return: str 
        """
        params = {
            'Amount': amount,
            'InvoiceNumber': invoice_number,
            'InvoiceDate': invoice_date,
            'Mobile': mobile,
            'Email': email,
            'Action': self.ACTION_PURCHASE,
            'MerchantCode': self.merchant_code,
            'TerminalCode': self.terminal_id,
            'RedirectAddress': self.redirect_url,
            'TimeStamp': self._generate_timestamp(),
        }
        response = self._requestBuilder(self.URL_GET_TOKEN, params, 'POST')
        return self.URL_PAYMENT_GATEWAY + "?n=" + response["Token"]

    ### check transaction ================================================
    def checkTransaction(self, reference_id, invoice_number, invoice_date):
        # type: (str, str, str) -> dict
        """
        Check Transaction 
        :param reference_id: Transaction reference Id
        :param invoice_number: invoice number 
        :param invoice_date: invoice date
        :return: str 
        """
        params = {
            'transactionReferenceID': reference_id,
            'invoiceNumber': invoice_number,
            'invoiceDate': invoice_date,
            'merchantCode': self.merchant_code,
            'terminalCode': self.terminal_id,
        }
        response = self._requestBuilder(
            self.URL_CHECK_TRANSACTION, params, 'POST')
        return response

    #### Verify Payment =========================================
    def verifyPayment(self, amount, invoice_number, invoice_date):
        # type: (str, str, str) -> dict
        """
        Verify Payment 
        :param amount: invoice amount
        :param invoice_number: invoice number 
        :param invoice_date: invoice date
        :return: str 
        """
        params = {
            'amount': amount,
            'invoiceNumber': invoice_number,
            'invoiceDate': invoice_date,
            'merchantCode': self.merchant_code,
            'terminalCode': self.terminal_id,
            'timeStamp': self._generate_timestamp(),
        }
        response = self._requestBuilder(
            self.URL_VERIFY_PAYMENT, params, 'POST')
        return response

    ### Refund ====================================
    def refund(self, invoice_number, invoice_date):
        # type: (str, str) -> dict
        """
        Refund
        :param invoice_number: invoice number 
        :param invoice_date: invoice date
        :return: str
        """
        params = {
            'invoiceNumber': invoice_number,
            'invoiceDate': invoice_date,
            'merchantCode': self.merchant_code,
            'terminalCode': self.terminal_id,
            'timeStamp': self._generate_timestamp(),
        }
        response = self._requestBuilder(self.URL_REFUND, params, 'POST')
        return response