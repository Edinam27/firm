// cart.js - Handles all shopping cart functionality

// Cart object to manage cart operations
const Cart = {
    // Get cart from localStorage or initialize empty cart
    getCart: function() {
      const cart = localStorage.getItem('pureflow_cart');
      return cart ? JSON.parse(cart) : [];
    },
    
    // Save cart to localStorage
    saveCart: function(cart) {
      localStorage.setItem('pureflow_cart', JSON.stringify(cart));
      this.updateCartCount();
    },
    
    // Add item to cart
    addItem: function(product) {
      const cart = this.getCart();
      
      // Check if product already exists in cart
      const existingItemIndex = cart.findIndex(item => 
        item.id === product.id && item.size === product.size
      );
      
      if (existingItemIndex > -1) {
        // Update quantity if product already in cart
        cart[existingItemIndex].quantity += product.quantity;
      } else {
        // Add new item to cart
        cart.push(product);
      }
      
      this.saveCart(cart);
      
      // Show notification
      this.showNotification(`${product.name} (${product.size}) added to cart!`);
    },
    
    // Remove item from cart
    removeItem: function(index) {
      const cart = this.getCart();
      cart.splice(index, 1);
      this.saveCart(cart);
    },
    
    // Update item quantity
    updateQuantity: function(index, quantity) {
      const cart = this.getCart();
      cart[index].quantity = quantity;
      this.saveCart(cart);
    },
    
    // Clear entire cart
    clearCart: function() {
      localStorage.removeItem('pureflow_cart');
      this.updateCartCount();
    },
    
    // Calculate cart total
    getTotal: function() {
      const cart = this.getCart();
      return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    },
    
    // Update cart count in the header
    updateCartCount: function() {
      const cart = this.getCart();
      const count = cart.reduce((total, item) => total + item.quantity, 0);
      
      // Update the cart count display in the header
      const cartCountElement = document.querySelector('.cart-count');
      if (cartCountElement) {
        cartCountElement.textContent = count;
        
        // Show/hide the count badge
        if (count > 0) {
          cartCountElement.classList.remove('d-none');
        } else {
          cartCountElement.classList.add('d-none');
        }
      }
    },
    
    // Show notification when item is added to cart
    showNotification: function(message) {
      // Create notification element if it doesn't exist
      let notification = document.getElementById('cart-notification');
      
      if (!notification) {
        notification = document.createElement('div');
        notification.id = 'cart-notification';
        notification.className = 'cart-notification';
        document.body.appendChild(notification);
        
        // Add styles if not already in CSS
        const style = document.createElement('style');
        style.textContent = `
          .cart-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #4CAF50;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            z-index: 1000;
            transform: translateY(-100px);
            opacity: 0;
            transition: all 0.3s ease;
          }
          .cart-notification.show {
            transform: translateY(0);
            opacity: 1;
          }
        `;
        document.head.appendChild(style);
      }
      
      // Set message and show notification
      notification.textContent = message;
      notification.classList.add('show');
      
      // Hide notification after 3 seconds
      setTimeout(() => {
        notification.classList.remove('show');
      }, 3000);
    }
  };
  
  // Initialize cart functionality when DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    // Update cart count on page load
    Cart.updateCartCount();
    
    // Add event listeners to all "Add to Cart" buttons
    const addToCartButtons = document.querySelectorAll('.btn-custom');
    
    addToCartButtons.forEach(button => {
      if (button.textContent.trim() === 'Add to Cart') {
        button.addEventListener('click', function(event) {
          // Get product information from the card
          const productCard = this.closest('.product-card');
          if (!productCard) return;
          
          const productName = productCard.querySelector('.card-title').textContent;
          const productCategory = productCard.querySelector('.product-category').textContent || 'Product';
          const priceElement = productCard.querySelector('.price');
          const priceText = priceElement.textContent.replace('$', '').trim();
          
          // Handle sale prices (with strikethrough)
          let price;
          if (priceText.includes('$')) {
            // If there's a sale price, get the second price (after the strikethrough)
            price = parseFloat(priceText.split(' ').pop());
          } else {
            price = parseFloat(priceText);
          }
          
          // Get selected size
          const sizeElement = productCard.querySelector('.size-option.active');
          const size = sizeElement ? sizeElement.textContent.trim() : 'Standard';
          
          // Get product image
          const imageElement = productCard.querySelector('.card-img-top');
          const imageUrl = imageElement ? imageElement.getAttribute('src') : '';
          
          // Create unique ID based on product name and size
          const productId = `${productName.replace(/\s+/g, '-').toLowerCase()}-${size.toLowerCase()}`;
          
          // Create product object
          const product = {
            id: productId,
            name: productName,
            category: productCategory,
            price: price,
            size: size,
            quantity: 1,
            imageUrl: imageUrl
          };
          
          // Add to cart
          Cart.addItem(product);
        });
      }
    });
  });
  
  // Export Cart object for use in other scripts
  window.Cart = Cart;