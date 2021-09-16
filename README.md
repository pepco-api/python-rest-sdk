# Python SDK for Pasargad IPG

Python SDK for Pasargad Internet Payment Gateway (RESTful API)

## Installation

```bash
pip install pypep-pepco
```

## Usage
 - Read API Documentation, [Click Here! (دانلود مستندات کامل درگاه پرداخت)](https://www.pep.co.ir/wp-content/uploads/2019/06/1-__PEP_IPG_REST-13971020.Ver3_.00.pdf)
 - Save your private key into an `.xml` file inside your project directory.
 
 
## Redirect User to Payment Gateway
```python
    from pypep import Pasargad

    # Create an object from Pasargad client
    # e.q: pasargad = Pasargad(123123,444444,"https://pep.co.ir/ipgtest","cert.xml")
    pasargad = Pasargad('<merchant_code>', '<terminal_id>', '<redirect_url>', '<certification_file>')
    payment_url = pasargad.redirect(
        amount=15000,
        invoice_number="15001",
        invoice_date="2021/08/23 15:51:00",
        # mobile="091111", #optional
        # email="test@test.local" #optional
    )
```

This method, will return a `string` like this:

```bash
// output:
// https://pep.shaparak.ir/payment.aspx?n=LySl+5tYkxL5qNMBRthW7DWzV8e3ALnTJUqiCS0V/io=
// Redirect User to the generated URL to make payment
```

## Checking and Verifying Transaction
After Payment Process, User is going to be returned to your redirect_url

payment gateway is going to answer the payment result with sending below parameters to your redirectURL (as `QueryString` parameters):
 - InvoiceNumber (iN field) 
 - InvoiceDate (iD field) 
 - TransactionReferenceID (tref field) 
 
Store this information in a proper data storage and let's check transaction result by sending a check api request to the Bank:

```python
    from pypep import Pasargad

# Create an object from Pasargad client
# e.q: pasargad = Pasargad(123123,444444,"https://pep.co.ir/ipgtest","cert.xml")
pasargad = Pasargad('<merchant_code>', '<terminal_id>', '<redirect_url>', '<certification_file>')

response = pasargad.check_transaction(
    reference_id="637653306794022509",
    invoice_number="15001",
    invoice_date="2021/08/23 15:51:00",
)
```

Successful result:
```json
{
    "TraceNumber": 13,
    "ReferenceNumber": 100200300400500,
    "TransactionDate": "2021/08/08 11:58:23",
    "Action": "1003",
    "TransactionReferenceID": "636843820118990203",
    "InvoiceNumber": "4029",
    "InvoiceDate": "2021/08/08 11:54:03",
    "MerchantCode": 100123,
    "TerminalCode": 200123,
    "Amount": 15000,
    "IsSuccess": true,
    "Message": " "
}
```
If you got `IsSuccess` with `true` value, so everything is O.K!

Now, for your successful transaction, you should call `verifyPayment()` method to keep the money and Bank makes sure the checking process done properly:

```python
    from pypep import Pasargad

# Create an object from Pasargad client
# e.q: pasargad = Pasargad(123123,444444,"https://pep.co.ir/ipgtest","cert.xml")
pasargad = Pasargad('<merchant_code>', '<terminal_id>', '<redirect_url>', '<certification_file>')

response = pasargad.verify_payment(
    amount=15000,
    invoice_number="15001",
    invoice_date="2021/08/23 15:51:00",
)
```

...and the successful response looks like this response:
```json
{
 "IsSuccess": true,
 "Message": " ",
 "MaskedCardNumber": "5022-29**-****-2328",
 "HashedCardNumber": "2DDB1E270C598677AE328AA37C2970E3075E1DB....",
 "ShaparakRefNumber": "100200300400500"
}
```

## Payment Refund
If for any reason, you decided to cancel an order in early hours after taking the order (maximum 2 hours later), you can refund the client payment to his/her bank card.

for this, use `refund()` method:


```python
    from pypep import Pasargad
    # Create an object from Pasargad client
    # e.q: pasargad = Pasargad(123123,444444,"https://pep.co.ir/ipgtest","cert.xml")
    pasargad = Pasargad('<merchant_code>', '<terminal_id>', '<redirect_url>', '<certification_file>')

    response = pasargad.refund(
        invoice_number="15001",
        invoice_date="2021/08/23 15:51:00",
    )
```

# Support
Please use your credentials to login into [Support Panel](https://my.pep.co.ir)
Contact Author/Maintainer: [Reza Seyf](https://twitter.com/seyfcode)
