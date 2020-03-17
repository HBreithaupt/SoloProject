function get_orders() {
  $.get("/order/history", function(data) {
    result = JSON.parse(data);

    result.forEach(function(divider, index) {
      $("#order_history").append(`<div id=${index}></div><hr>`);
      console.log(divider)

      divider.forEach(function(input) {
        $(`div[id=${index}]`).append(`<p>${input['date_total'] ? input['date_total'] : input['description']}</p>`);
      });
    });
  });
}





$(document).ready(function() {
  $('#update_account_button').click(function() {
    console.log('got here');
  });

  get_orders();
});
