$(document).ready(function() {
    $('#reservationModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var carId = button.data('car-id'); // Extract info from data-* attributes
        var carName = button.data('car-model');
        var modal = $(this);
        modal.find('.car-id-input').val(carId);
        modal.find('.modal-title').text('Reserve ' + carName);
    });
    $('#reserve-btn').click(function() {
        console.log('submitting form');
        $('#bookingForm').submit();
    });
    $('#pick-up-date').change(function(event) {
        console.log(event.currentTarget.value);
        $('#pick-up-date').val(event.currentTarget.value);
    });
    
    $('#return-date').change(function(event) {
        $('#return-date').val(event.currentTarget.value);
    });
});