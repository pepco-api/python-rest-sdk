# coding: utf-8
from __future__ import absolute_import

import json
from base64 import b64decode, b64encode
from datetime import datetime
from typing import Any, Dict
from xml.dom import minidom

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from Crypto.Util import number

from .compat import HTTPError, Request, urlopen


# API Error for catching Exceptions
class ApiError(Exception):
    def __init__(self, code, description=""):
        super(ApiError, self).__init__("Result code: %s (%s)" % (code, description))
        self.code = code


class PasargadApiError(Exception):
    def __init__(self, code, description=""):
        super(PasargadApiError, self).__init__(
            "Result code: %s (%s)" % (code, description)
        )
        self.code = code


class PasargadCryptor:
    ACTION_PURCHASE = "1003"

    def __init__(self, key_pair: RSA):
        self.key_pair = key_pair

    def make_signature(self, data: Dict[str, Any]) -> bytes:
        serialized_data = json.dumps(data).encode("utf-8")
        hash_value = SHA1.new(serialized_data)

        # Use OAEP padding with RSA for secure encryption and signing
        cipher = PKCS1_OAEP.new(self.key_pair)

        # Generate the signature with OAEP padding
        signature = cipher.encrypt(hash_value.digest())

        return b64encode(signature)


class PasargadXmlKeyLoader:
    @staticmethod
    def _process_xml_node(nodelist):
        text_data = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                text_data.append(node.data)
        combined_text = "".join(text_data)
        return number.bytes_to_long(b64decode(combined_text))

    @staticmethod
    def _convert_xml_key_to_pem(xml_private_key_file: str) -> RSA:
        with open(xml_private_key_file, "rb") as file:
            xml_key = file.read()
        doc = minidom.parseString(xml_key)
        modulus = PasargadXmlKeyLoader._get_element_value(doc, "Modulus")
        exponent = PasargadXmlKeyLoader._get_element_value(doc, "Exponent")
        d = PasargadXmlKeyLoader._get_element_value(doc, "D")
        p = PasargadXmlKeyLoader._get_element_value(doc, "P")
        q = PasargadXmlKeyLoader._get_element_value(doc, "Q")
        return RSA.construct((modulus, exponent, d, p, q))

    @staticmethod
    def _get_element_value(doc, element_name: str) -> int:
        element = doc.getElementsByTagName(element_name)[0]
        return number.bytes_to_long(b64decode(element.childNodes[0].data))


class PasargadPaymentGateway:
    URL_GET_TOKEN = "https://pep.shaparak.ir/Api/v1/Payment/GetToken"
    URL_PAYMENT_GATEWAY = "https://pep.shaparak.ir/payment.aspx"
    URL_CHECK_TRANSACTION = (
        "https://pep.shaparak.ir/Api/v1/Payment/CheckTransactionResult"
    )
    URL_VERIFY_PAYMENT = "https://pep.shaparak.ir/Api/v1/Payment/VerifyPayment"
    URL_REFUND = "https://pep.shaparak.ir/Api/v1/Payment/RefundPayment"

    def __init__(self, cryptor: PasargadCryptor):
        self.cryptor = cryptor

    @staticmethod
    def _generate_timestamp():
        return datetime.today().strftime("%Y/%m/%d %H:%M:%S")

    def _request_builder(self, url, data, method="POST"):
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "Sign": self.cryptor.make_signature(data),
            },
        )
        payload = json.dumps(data)
        request.data = payload.encode("utf-8")
        request.add_header("Content-Type", "application/json")
        request.get_method = lambda: method
        try:
            response = urlopen(request)
        except HTTPError as e:
            response = e
        response = json.loads(response.read().decode("utf-8"))
        if not response["IsSuccess"]:
            raise PasargadApiError(400, response["Message"])
        return response

    def generate_payment_url(
        self,
        amount: str,
        invoice_number: str,
        invoice_date: str,
        mobile: str = "",
        email: str = "",
    ) -> str:
        params = {
            "amount": amount,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "mobile": mobile,
            "email": email,
            "action": PasargadCryptor.ACTION_PURCHASE,
            "time_stamp": self._generate_timestamp(),
        }
        response = self._request_builder(self.URL_GET_TOKEN, params, "POST")
        return f"{self.URL_PAYMENT_GATEWAY}?n={response['token']}"

    def check_transaction(
        self, reference_id: str, invoice_number: str, invoice_date: str
    ) -> dict:
        params = {
            "transactionReferenceID": reference_id,
            "invoiceNumber": invoice_number,
            "invoiceDate": invoice_date,
        }
        return self._request_builder(self.URL_CHECK_TRANSACTION, params, "POST")

    def verify_payment(
        self, amount: str, invoice_number: str, invoice_date: str
    ) -> dict:
        params = {
            "amount": amount,
            "invoiceNumber": invoice_number,
            "invoiceDate": invoice_date,
            "timeStamp": self._generate_timestamp(),
        }
        response = self._request_builder(self.URL_VERIFY_PAYMENT, params, "POST")
        return response

    def refund(self, invoice_number: str, invoice_date: str) -> dict:
        params = {
            "invoiceNumber": invoice_number,
            "invoiceDate": invoice_date,
            "timeStamp": self._generate_timestamp(),
        }
        response = self._request_builder(self.URL_REFUND, params, "POST")
        return response
