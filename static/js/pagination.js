/**
 * Pagination functionality for product listings
 */

document.addEventListener("DOMContentLoaded", function() {
  // Get all pagination links
  const paginationLinks = document.querySelectorAll('.pagination .page-link');
  
  // Current page (default to 1)
  let currentPage = 1;
  
  // Total number of pages (can be dynamically set from backend)
  const totalPages = 3;
  
  // Function to update pagination UI
  function updatePaginationUI() {
    // Update active state
    document.querySelectorAll('.pagination .page-item').forEach((item, index) => {
      // Skip first and last items (prev/next buttons)
      if (index > 0 && index <= totalPages) {
        if (index === currentPage) {
          item.classList.add('active');
        } else {
          item.classList.remove('active');
        }
      }
    });
    
    // Enable/disable previous button
    const prevButton = document.querySelector('.pagination .page-item:first-child');
    if (currentPage === 1) {
      prevButton.classList.add('disabled');
      prevButton.querySelector('.page-link').setAttribute('aria-disabled', 'true');
    } else {
      prevButton.classList.remove('disabled');
      prevButton.querySelector('.page-link').setAttribute('aria-disabled', 'false');
    }
    
    // Enable/disable next button
    const nextButton = document.querySelector('.pagination .page-item:last-child');
    if (currentPage === totalPages) {
      nextButton.classList.add('disabled');
      nextButton.querySelector('.page-link').setAttribute('aria-disabled', 'true');
    } else {
      nextButton.classList.remove('disabled');
      nextButton.querySelector('.page-link').setAttribute('aria-disabled', 'false');
    }
  }
  
  // Function to load page content
  function loadPageContent(page) {
    // This would typically be an AJAX call to fetch products for the selected page
    console.log(`Loading products for page ${page}`);
    
    // For demo purposes, we'll just simulate loading by adding a loading class
    const productsContainer = document.querySelector('.row:has(.product-card)');
    productsContainer.classList.add('loading');
    
    // Simulate network delay
    setTimeout(() => {
      productsContainer.classList.remove('loading');
      // Update page indicator
      document.querySelector('.text-muted').textContent = `Showing products for page ${page}`;
    }, 500);
    
    // Update current page and UI
    currentPage = page;
    updatePaginationUI();
  }
  
  // Add click event listeners to pagination links
  paginationLinks.forEach((link, index) => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Handle previous button
      if (index === 0) {
        if (currentPage > 1) {
          loadPageContent(currentPage - 1);
        }
        return;
      }
      
      // Handle next button
      if (index === paginationLinks.length - 1) {
        if (currentPage < totalPages) {
          loadPageContent(currentPage + 1);
        }
        return;
      }
      
      // Handle numbered page links
      const pageNum = parseInt(link.textContent);
      if (pageNum !== currentPage) {
        loadPageContent(pageNum);
      }
    });
  });
  
  // Initialize pagination UI
  updatePaginationUI();
});