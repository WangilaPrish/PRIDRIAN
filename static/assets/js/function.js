$(document).ready(function () {
    // Add to cart functionality
    $("#add-to-cart-btn").on("click", function (e) {
        e.preventDefault(); // Prevent form submission

        // Get product details
        let quantity = $("#product-quantity").val();
        let product_name = $(".product-name").val();
        let product_id = $(".product-id").val();
        let product_image = $(".product-image").val();
        let product_price = $(".current-price").text().replace("ksh ", ""); // Remove "ksh " from price string

        let csrf_token = $('input[name="csrfmiddlewaretoken"]').val(); // CSRF token
        let this_val = $(this);

        console.log("Quantity:", quantity);
        console.log("Name:", product_name);
        console.log("Price:", product_price);
        console.log("Id:", product_id);
        console.log("Image:", product_image);

        $.ajax({
            url: '/add-to-cart/',  // Ensure this matches the URL in your Django view
            type: 'POST',
            data: {
                product_id: product_id,
                quantity: quantity,
                product_name: product_name,
                product_price: product_price,
                product_image: product_image,
                csrfmiddlewaretoken: csrf_token, // CSRF token
            },
            dataType: 'json',
            beforeSend: function () {
                console.log("Adding to cart...");
            },
            success: function (response) {
                if (response.status === 'success') {
                    this_val.html("Item Added"); // Update button text
                    console.log("Successfully added to cart");
                    $(".cart-items-count").text(response.totalcartitems); // Update cart item count
                } else {
                    alert("There was an error adding the item to the cart.");
                }
            },
            error: function () {
                alert("An error occurred. Please try again.");
            }
        });
    });
});
