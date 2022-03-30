from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import braintree
# Create your views here.

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="xt963hmh4232xsgg",
        public_key="fktyn7nyhm8phbj8",
        private_key="51864d06c3f389c470b1bd2e57304b7b"
    )
)


def validate_user_session(id, token):
    UserModel = get_user_model()

    try:
        user = UserModel.objects.get(pk=id)
        if user.session_token == token:
            return True
        return False

    except UserModel.DoesNotExist:
        return False


@csrf_exempt
def generate_token(request, id, token):
    if not validate_user_session(id, token):
        return JsonResponse({'error': 'Invalid Session'})

    return JsonResponse({'client token': gateway.client_token.generate(), 'success': True})


@csrf_exempt
def proccess_payment(request, id, token):
    if not validate_user_session(id, token):
        return JsonResponse({'error': 'Invalid Session'})

    nonce_from_the_client = request.POST['PyamentMethodNonce']
    amount_from_the_client = request.POST['amount']

    result = gateway.transaction.sale({
        'amount': amount_from_the_client,
        'payment_method_nonce': nonce_from_the_client,
        'option': {
            'submit_for_settlement': True
        }
    })

    if result.is_success:
        return JsonResponse({'success': result.is_success,
                            'transaction': {
                                'id': result.transaction.id,
                                'amount': result.transaction.amount
                            }
        })
    else:
        return JsonResponse({'error': True, 'success': False})
