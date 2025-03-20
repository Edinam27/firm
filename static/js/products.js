// static/js/products.js
document.addEventListener('DOMContentLoaded', function() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const productCard = this.closest('.product-card');
            const sizeOption = productCard.querySelector('.size-option.selected');
            
            if (!sizeOption) {
                alert('Please select a size');
                return;
            }

            const size = sizeOption.getAttribute('data-size');
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

            fetch('/api/add-to-cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    product_id: productId,
                    size: size
                }),
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    updateCartCounter();
                    showAddedToCartMessage(productCard);
                } else {
                    throw new Error(data.error || 'Failed to add item to cart');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to add item to cart: ' + error.message);
            });
        });
    });
});

function updateCart(productId, size, action) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch('/api/update-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            product_id: productId,
            size: size,
            action: action
        }),
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCounter();
            updateCartDisplay();
        } else {
            showErrorMessage(data.error || 'Failed to update cart');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Failed to update cart');
    });
}

function showAddedToCartMessage(productCard) {
    const message = document.createElement('div');
    message.className = 'added-to-cart-message';
    message.textContent = 'Added to cart!';
    productCard.appendChild(message);
    
    setTimeout(() => {
        message.remove();
    }, 2000);
}

// products.js
function getCsrfToken() {
    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    return tokenMeta ? tokenMeta.getAttribute('content') : '';
}

// Function to add to cart
function addToCart(productId) {
    const sizeSelect = document.querySelector(`#size-select-${productId}`);
    if (!sizeSelect) {
        showErrorMessage('Please select a size');
        return;
    }
    
    const size = sizeSelect.value;
    if (!size) {
        showErrorMessage('Please select a size');
        return;
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch('/api/add-to-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            product_id: productId,
            size: size
        }),
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCounter();
            showSuccessMessage('Item added to cart!');
        } else {
            showErrorMessage(data.error || 'Failed to add item to cart');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Failed to add item to cart');
    });
}

function showSuccessMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'alert alert-success';
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    setTimeout(() => messageDiv.remove(), 3000);
}

function showErrorMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'alert alert-danger';
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    setTimeout(() => messageDiv.remove(), 3000);
}

// Function to update cart counter
function updateCartCounter() {
    fetch('/api/cart-count')
    .then(response => response.json())
    .then(data => {
        const counter = document.querySelector('.cart-counter');
        if (counter) {
            counter.textContent = data.count;
        }
    });
}