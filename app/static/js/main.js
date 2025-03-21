/**
 * Warewolf - Main JavaScript
 */

// Initialize all components when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Toggle business fields in registration form
    initializeBusinessFieldsToggle();
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