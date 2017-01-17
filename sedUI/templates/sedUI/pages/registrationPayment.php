{% block content %}
	{% load staticfiles %}
	<div align="center">
		<form action="/registration/" onsubmit="get_action(this)" method="post" style="margin: auto"> {% csrf_token %}
  		{{ wizard.management_form }}
			<label for="Question" style="font-size: 32px">Select a Payment Method</label>
			<br>
			<div class="input-group" align="center">
				<label class="radio-inline" style="font-size: 16px">
					<input id="Pay_Online" type="radio" name="optradio">{{wizard.form.payment_method.1}}
				</label>
				<label class="radio-inline" style="font-size: 16px">
					<input id="Pay_Mail" type="radio" name="optradio">{{wizard.form.payment_method.0}}
				</label>
			</div>
			<br>
			<script src="https://checkout.stripe.com/checkout.js"></script>
			<input type="submit" name="submit" id="submit" value="Next" class="btn btn-primary">
			<script type="text/javascript">
				var handler = StripeCheckout.configure({
				  key: 'pk_test_92kS90THLx5tJ1giZLy7JIcO',
				  image: 'http://54.152.243.242:8000/static/img/images/sedLogo.jpg',
				  locale: 'auto',
				  token: function(token) {
				    // You can access the token ID with `token.id`.
				    // Get the token ID to your server-side code for use.
				  }
				});

				document.getElementById('submit').addEventListener('click', function(e) {
					if(document.getElementById('Pay_Online').checked) {
					  // Open Checkout with further options:
					  handler.open({
					    name: 'Scout Engineering Day',
					    description: 'Courses Cost',
					    amount: 2000
					  });
					  e.preventDefault();
					}
					if(document.getElementById('Pay_Mail').checked) {
						window.alert("Please send check to...");
					}
				});


				// Close Checkout on page navigation:
				window.addEventListener('popstate', function() {
				  handler.close();
				});
			</script>

	  </form>
	</div>
{% endblock %}
