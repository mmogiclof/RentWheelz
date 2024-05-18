$(document).ready(function() {
    $('#reservationModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var carId = button.data('car-id'); // Extract info from data-* attributes
        var carName = button.data('car-model');
        var modal = $(this);
        if(carId == undefined) {return;}
        modal.find('.car-id-input').val(carId);
        modal.find('.modal-title').text('Reserve ' + carName);
    });

    switch (window.location.search) {
        case '':
            $('.nav-tabs .nav-link:contains("All")').addClass('active');
            break;

        case '?status=Confirmed':
            $('.nav-tabs .nav-link:contains("Confirmed")').addClass('active');;
            break;
        case '?status=Completed':
            $('.nav-tabs .nav-link:contains("Completed")').addClass('active');;
            break;
        case '?status=Cancelled':
            $('.nav-tabs .nav-link:contains("Cancelled")').addClass('active');;
            break;
    }


    $('#reservationModal').on('hidden.bs.modal', function (e) {
        $('.flash-message').remove();
        $('#bookingForm').trigger('reset');

    });
    $('#reserve-btn').click(function(e) {
        $('.flash-message').remove();
        fetch('/api/v1/reservations/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams(new FormData(document.querySelector('#bookingForm')))
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                $('#reservationModal .modal-body').prepend('<div class="flash-message alert alert-danger" role="alert"><span>' + data.error + '</span></div>');
                return;
            }
            alert('Reservation successful!');
            window.location.href = '/bookings';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    $('#pick-up-date').change(function(event) {
        $('#pick-up-date').val(event.currentTarget.value);
    });
    
    $('#return-date').change(function(event) {
        $('#return-date').val(event.currentTarget.value);
    });
});