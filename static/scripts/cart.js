var stripe = Stripe('pk_test_5QGT0900AjGInQMQLyStKLJL00h7dju2we');
var sessionID;



function append_pizza(item) {
 $('#cart').append(
   `
   <div>
    <p> Quantity: ${item['quantity']} </p>
    <p> Size: ${item['size']} </p>
    <p> Crust: ${item['style']} </p>
    <p> Toppings: ${item['toppings']} </p>
    <p class="text-right"><span>&#36;</span>${item['price']}
   </div> <hr>
   `
 );
}



function display_cart() {
  order_id = $('#cart').attr('data-id');

  $.get(`/order/${order_id}/serialize`, function(data) {
    result = JSON.parse(data);
    

    result.forEach(function(input) {
      if(input['type'] == 'pizza')
        append_pizza(input);
    });

    $('#cart').append(
      `
      <div>
        <p class='text-right'> Total: <span>&#36;</span>${result[result.length - 1]['total_price']}</p>
      </div>
      `
    );
  });


}

function get_sessionID() {
  $.get("/checkout/session/create", function(data) {

    sessionID = JSON.parse(data)

    $('#checkoutButton').click(function() {
      stripe.redirectToCheckout({
        sessionId: sessionID
      });
    });
  });
}




$(document).ready(function() {
  display_cart();
  get_sessionID();
});
