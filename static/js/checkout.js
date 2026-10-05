$(document).ready(function () {
  $(".payWithRazorpay").on("click", function (e) {
    e.preventDefault();

    var fname = $("[name='fname']").val().trim();
    var lname = $("[name='lname']").val().trim();
    var email = $("[name='email']").val().trim();
    var phone = $("[name='phone']").val().trim();
    var address = $("[name='address']").val().trim();
    var city = $("[name='city']").val().trim();
    var state = $("[name='state']").val().trim();
    var country = $("[name='country']").val().trim();
    var pincode = $("[name='pincode']").val().trim();
    var token = $('[name="csrfmiddlewaretoken"]').val();

    if (
      fname === "" ||
      lname === "" ||
      email === "" ||
      phone === "" ||
      address === "" ||
      city === "" ||
      state === "" ||
      country === "" ||
      pincode === ""
    ) {
      swal("Alert!", "All fields are mandatory!", "error");
      return false;
    } else {
      $.ajax({
        method: "GET",
        url: "/proceed-to-pay",
        success: function (response) {
          // console.log(response);
          var options = {
            key: response.key_id,
            amount: Math.round(response.total_price * 100),
            currency: "INR",
            name: "Sadia Shop",
            description: "Test Transaction",
            image: "https://example.com/your_logo",
            // order_id: "order_9A33XWu170gUtm",
            handler: function (responseb) {
              data = {
                fname: fname,
                lname: lname,
                email: email,
                phone: phone,
                address: address,
                city: city,
                state: state,
                country: country,
                pincode: pincode,
                payment_mode: "Paid by Razorpay",
                payment_id: responseb.razorpay_payment_id,
                csrfmiddlewaretoken: token,
              };
              $.ajax({
                method: "POST",
                url: "/place-order",
                data: data,
                success: function (responsec) {
                  swal("Congrats!", responsec.status, "success").then(
                    (value) => {
                        window.location.href = "/my-orders";
                    }
                  );
                },
              });
            },
            prefill: {
              name: fname + " " + lname,
              email: email,
              contact: phone,
            },
            notes: {
              address: address,
            },
            theme: {
              color: "#3399cc",
            },
          };

          var rzp1 = new Razorpay(options);
          rzp1.open();
        },
      });
    }
  });
});
