/**
 * Warewolf - Main JavaScript
 */

// Initialize all components when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Toggle business fields in registration form
    initializeBusinessFieldsToggle();
    
    // Initialize dropdown menus with improved behavior
    initializeDropdowns();
    
    // Log authentication status for debugging
    logAuthStatus();
});

// Function to initialize the business fields toggle on the registration form
function initializeBusinessFieldsToggle() {
    const roleSelect = document.getElementById('role');
    const businessFields = document.getElementById('business-fields');
    
    if (roleSelect && businessFields) {
        function toggleBusinessFields() {
            if (roleSelect.value === 'owner') {
                businessFields.classList.remove('hidden');
            } else {
                businessFields.classList.add('hidden');
            }
        }
        
        // Initial check
        toggleBusinessFields();
        
        // Add event listener
        roleSelect.addEventListener('change', toggleBusinessFields);
    }
}

// Function to handle dropdown menus with better mobile support
function initializeDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown, .user-dropdown');
    
    dropdowns.forEach(dropdown => {
        const dropdownToggle = dropdown.querySelector('a');
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        
        if (!dropdownMenu || !dropdownToggle) return;
        
        // Variables to track mouse status
        let isOverButton = false;
        let isOverMenu = false;
        let isMouseLeaving = false;
        
        // Add event listeners for both click and hover
        dropdownToggle.addEventListener('mouseenter', function() {
            isOverButton = true;
            dropdownMenu.classList.add('show');
        });
        
        dropdownToggle.addEventListener('mouseleave', function() {
            isOverButton = false;
            
            // Use timeout to check if mouse moved to menu
            setTimeout(function() {
                if (!isOverMenu && !isOverButton) {
                    dropdownMenu.classList.remove('show');
                }
            }, 100);
        });
        
        dropdownMenu.addEventListener('mouseenter', function() {
            isOverMenu = true;
        });
        
        dropdownMenu.addEventListener('mouseleave', function() {
            isOverMenu = false;
            
            // Use timeout to check if mouse moved to button
            setTimeout(function() {
                if (!isOverButton && !isOverMenu) {
                    dropdownMenu.classList.remove('show');
                }
            }, 100);
        });
        
        // Toggle dropdown on click (better for mobile)
        dropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                const dropdownMenu = dropdown.querySelector('.dropdown-menu');
                if (dropdownMenu) {
                    dropdownMenu.classList.remove('show');
                }
            }
        });
    });
}

// Log authentication status for debugging
function logAuthStatus() {
    // Check if we have user elements that indicate logged-in status
    const userDropdown = document.querySelector('.user-dropdown');
    const logoutLink = document.querySelector('a[href="/auth/logout"]');
    
    if (userDropdown || logoutLink) {
        console.log('User appears to be logged in');
    } else {
        console.log('User appears to be logged out');
    }
} 