// static/js/checkout.js
document.addEventListener('DOMContentLoaded', function() {
    const steps = document.querySelectorAll('.step');
    const formSteps = document.querySelectorAll('.form-step');
    const nextBtn = document.querySelector('.next-step');
    const prevBtn = document.querySelector('.prev-step');
    let currentStep = 1; // Fixed: Initialize currentStep to 1

    // Validate current step before proceeding
    async function validateStep(step) {
        const currentFormStep = document.querySelector(`.form-step[data-step="${step}"]`);
        const inputs = currentFormStep.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        });

        return isValid;
    }

    function updateSteps() {
        steps.forEach(step => {
            const stepNum = parseInt(step.dataset.step);
            if (stepNum === currentStep) {
                step.classList.add('active');
            } else if (stepNum < currentStep) {
                step.classList.add('completed');
                step.classList.remove('active');
            } else {
                step.classList.remove('active', 'completed');
            }
        });

        formSteps.forEach(step => {
            if (parseInt(step.dataset.step) === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        // Fixed: Show/hide prev button and update next button text
        prevBtn.style.display = currentStep === 1 ? 'none' : 'block';
        nextBtn.textContent = currentStep === formSteps.length ? 'Place Order' : 'Next';
    }

    nextBtn.addEventListener('click', async function() {
        if (currentStep < formSteps.length) {
            if (await validateStep(currentStep)) {
                currentStep++;
                updateSteps();
            }
        } else {
            await placeOrder();
        }
    });

    // Add missing prev button handler
    prevBtn.addEventListener('click', function() {
        if (currentStep > 1) {
            currentStep--;
            updateSteps();
        }
    });

    async function placeOrder() {
        const formData = new FormData();
        const shippingInputs = document.querySelectorAll('.form-step input'); // Fixed: Remove incorrect data-step selector
        
        shippingInputs.forEach(input => {
            formData.append(input.name, input.value);
        });

        try {
            const response = await fetch('/api/place-order', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'  // Added for CSRF protection
                }
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            if (data.success) {
                window.location.href = '/order-confirmation';
            } else {
                alert(data.message || 'There was an error processing your order. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An unexpected error occurred. Please try again.');
        }
    }

    // Initialize payment method selection
    const paymentMethods = document.querySelectorAll('.payment-method');
    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            paymentMethods.forEach(m => m.classList.remove('selected'));
            this.classList.add('selected');
        });
    });

    // Initialize the steps on page load
    updateSteps();
});