function retrieve_alerts() {
  $.get('/alerts/retrieve', function(data) {
    result = JSON.parse(data);

    if(result.length > 0)
      $('#error_modal').modal('show');

    result.forEach(function(input) {
      $('#error_body').append(
        `<p>${input}</p>`
      );
    });
  });
}


function alert_body() {
  $('body').append(
    `<div id="error_modal" class="modal" tabindex="-1" role="dialog">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Alerts</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="close" name="button">
              <span aria-hidden='true'>&times;</span>
            </button>
          </div>
          <div id="error_body" class="modal-body">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" id="error_modal_close" data-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>`
  );
}


function get_num_in_cart() {
  $.get("/order/products/num/retrieve", function(data) {
    $("#cart_display").html(`Order(${JSON.parse(data)})`);
  });
}

$(document).ready(function () {
  alert_body();
  retrieve_alerts();
  get_num_in_cart();

  if($('#error_body p').length) {
    $('#error_modal').modal('show');
  }
})
