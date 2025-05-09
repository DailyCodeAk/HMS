/**
 * admin.js - JavaScript functionality for the Hotel Management System admin panel
 * Author: Akanimo Akpan
 * Team: WalnutMercury (Team 11)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all admin panel functionality
    initializeModals();
    initializeTabPanels();
    initializeFormValidation();
    initializeDataTables();
    initializeStatusUpdates();
    initializeCharts();
    initializeActionButtons();
});

/**
 * Initialize modal windows
 */
function initializeModals() {
    // Find all modal triggers
    const modalTriggers = document.querySelectorAll('[data-modal-trigger]');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-trigger');
            const modal = document.getElementById(modalId);
            
            if (modal) {
                // Show the modal
                modal.style.display = 'block';
                
                // Add event listener for close button
                const closeBtn = modal.querySelector('.close');
                if (closeBtn) {
                    closeBtn.addEventListener('click', function() {
                        modal.style.display = 'none';
                    });
                }
                
                // Close modal when clicking outside
                window.addEventListener('click', function(event) {
                    if (event.target === modal) {
                        modal.style.display = 'none';
                    }
                });
            }
        });
    });
}

/**
 * Initialize tab panels
 */
function initializeTabPanels() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.getAttribute('data-category') || this.getAttribute('data-status');
            const tabGroup = this.closest('.tabs').getAttribute('data-tab-group') || 'default';
            
            // Remove active class from all buttons in this group
            document.querySelectorAll(`.tabs[data-tab-group="${tabGroup}"] .tab-btn`).forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Handle different tab panel types
            if (this.closest('.tabs').classList.contains('category-tabs')) {
                filterByCategory(category, tabGroup);
            } else if (this.closest('.tabs').classList.contains('status-tabs')) {
                filterByStatus(category, tabGroup);
            }
        });
    });
}

/**
 * Filter elements by category
 */
function filterByCategory(category, tabGroup) {
    const items = document.querySelectorAll(`[data-tab-content="${tabGroup}"] [data-category]`);
    
    items.forEach(item => {
        if (category === 'all' || item.getAttribute('data-category') === category) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Filter elements by status
 */
function filterByStatus(status, tabGroup) {
    const items = document.querySelectorAll(`[data-tab-content="${tabGroup}"] [data-status]`);
    
    items.forEach(item => {
        if (status === 'all' || item.getAttribute('data-status') === status) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate="true"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Check required fields
            const required = form.querySelectorAll('[required]');
            required.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('invalid');
                    
                    // Create error message if not exists
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                } else {
                    field.classList.remove('invalid');
                    
                    // Remove error message if exists
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
            
            // Check number fields
            const numberFields = form.querySelectorAll('input[type="number"]');
            numberFields.forEach(field => {
                if (field.value && (isNaN(parseFloat(field.value)) || !isFinite(field.value))) {
                    isValid = false;
                    field.classList.add('invalid');
                    
                    // Create error message if not exists
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'Please enter a valid number';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                }
            });
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    });
}

/**
 * Initialize data tables
 */
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table[data-sortable="true"]');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sortable]');
        
        headers.forEach(header => {
            header.addEventListener('click', function() {
                const column = this.cellIndex;
                const sortDirection = this.getAttribute('data-sort-direction') === 'asc' ? 'desc' : 'asc';
                
                // Update sort direction attribute
                headers.forEach(h => h.removeAttribute('data-sort-direction'));
                this.setAttribute('data-sort-direction', sortDirection);
                
                // Sort the table
                sortTable(table, column, sortDirection);
            });
        });
    });
}

/**
 * Sort a table by the specified column and direction
 */
function sortTable(table, column, direction) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Sort rows
    rows.sort((a, b) => {
        const cellA = a.cells[column].textContent.trim();
        const cellB = b.cells[column].textContent.trim();
        
        // Check if sorting numbers
        if (!isNaN(parseFloat(cellA)) && !isNaN(parseFloat(cellB))) {
            return direction === 'asc' 
                ? parseFloat(cellA) - parseFloat(cellB)
                : parseFloat(cellB) - parseFloat(cellA);
        }
        
        // Sort strings
        return direction === 'asc'
            ? cellA.localeCompare(cellB)
            : cellB.localeCompare(cellA);
    });
    
    // Reorder rows in the DOM
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Initialize status update functionality
 */
function initializeStatusUpdates() {
    const statusButtons = document.querySelectorAll('.update-status-btn');
    
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const itemType = this.getAttribute('data-type');
            const currentStatus = this.getAttribute('data-current-status');
            
            // Create and show status update modal
            const modal = createStatusModal(itemId, itemType, currentStatus);
            document.body.appendChild(modal);
            
            // Show the modal
            modal.style.display = 'block';
            
            // Add event listener for close button
            const closeBtn = modal.querySelector('.close');
            closeBtn.addEventListener('click', function() {
                document.body.removeChild(modal);
            });
            
            // Add event listener for form submission
            const form = modal.querySelector('form');
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                const newStatus = this.status.value;
                
                // Here you would typically submit via AJAX
                // For demo, we'll just simulate a successful update
                alert(`Status for ${itemType} #${itemId} updated from ${currentStatus} to ${newStatus}`);
                
                // Close the modal
                document.body.removeChild(modal);
                
                // Reload the page to reflect changes
                // In a real app, you'd update the UI without a full reload
                location.reload();
            });
        });
    });
}

/**
 * Create a status update modal
 */
function createStatusModal(itemId, itemType, currentStatus) {
    // Create modal container
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    // Define status options based on item type and current status
    let statusOptions = [];
    
    if (itemType === 'booking') {
        statusOptions = ['pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled'];
    } else if (itemType === 'housekeeping') {
        statusOptions = ['pending', 'in_progress', 'completed'];
    } else if (itemType === 'inventory_order') {
        statusOptions = ['pending', 'shipped', 'received', 'cancelled'];
    } else if (itemType === 'food_order') {
        statusOptions = ['pending', 'preparing', 'ready', 'delivered', 'cancelled'];
    } else if (itemType === 'room_service') {
        statusOptions = ['pending', 'in_progress', 'completed', 'cancelled'];
    } else {
        statusOptions = ['pending', 'in_progress', 'completed', 'cancelled'];
    }
    
    // Create modal content
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <h3>Update ${itemType.replace('_', ' ')} Status</h3>
            <form id="update-status-form">
                <div class="form-group">
                    <label for="status">Status:</label>
                    <select id="status" name="status">
                        ${statusOptions.map(status => 
                            `<option value="${status}" ${status === currentStatus ? 'selected' : ''}>${status.replace('_', ' ')}</option>`
                        ).join('')}
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Update Status</button>
            </form>
        </div>
    `;
    
    return modal;
}

/**
 * Initialize charts for reports
 */
function initializeCharts() {
    // Check if canvas elements exist
    const occupancyChart = document.getElementById('occupancy-chart');
    const revenueChart = document.getElementById('revenue-chart');
    const categoryChart = document.getElementById('category-chart');
    const itemsChart = document.getElementById('items-chart');
    
    // If Chart.js is loaded and charts exist, create charts
    if (typeof Chart !== 'undefined') {
        if (occupancyChart) {
            createOccupancyChart(occupancyChart);
        }
        
        if (revenueChart) {
            createRevenueChart(revenueChart);
        }
        
        if (categoryChart) {
            createCategoryChart(categoryChart);
        }
        
        if (itemsChart) {
            createItemsChart(itemsChart);
        }
    }
}

/**
 * Create occupancy chart
 */
function createOccupancyChart(canvas) {
    // Get data from data attributes or API
    const labels = JSON.parse(canvas.getAttribute('data-labels') || '[]');
    const data = JSON.parse(canvas.getAttribute('data-values') || '[]');
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Occupancy Rate (%)',
                data: data,
                borderColor: '#1e3a8a',
                backgroundColor: 'rgba(30, 58, 138, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Room Occupancy Rate'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create revenue chart
 */
function createRevenueChart(canvas) {
    // Get data from data attributes or API
    const labels = JSON.parse(canvas.getAttribute('data-labels') || '[]');
    const data = JSON.parse(canvas.getAttribute('data-values') || '[]');
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue ($)',
                data: data,
                backgroundColor: '#1e3a8a',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Revenue by Period'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create category chart for food sales
 */
function createCategoryChart(canvas) {
    // Get data from data attributes or API
    const labels = JSON.parse(canvas.getAttribute('data-labels') || '[]');
    const data = JSON.parse(canvas.getAttribute('data-values') || '[]');
    
    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#4299e1',
                    '#48bb78',
                    '#ed8936',
                    '#9f7aea',
                    '#f56565'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                },
                title: {
                    display: true,
                    text: 'Sales by Category'
                }
            }
        }
    });
}

/**
 * Create items chart for food sales
 */
function createItemsChart(canvas) {
    // Get data from data attributes or API
    const labels = JSON.parse(canvas.getAttribute('data-labels') || '[]');
    const data = JSON.parse(canvas.getAttribute('data-values') || '[]');
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Quantity Sold',
                data: data,
                backgroundColor: '#4299e1'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Top Selling Items'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

/**
 * Initialize action buttons
 */
function initializeActionButtons() {
    // View details buttons
    const viewButtons = document.querySelectorAll('.view-details-btn');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const itemType = this.getAttribute('data-type');
            
            // Here you would typically fetch details via AJAX
            // For demo, we'll just show a mock response
            alert(`Viewing details for ${itemType} #${itemId}`);
        });
    });
    
    // Toggle availability buttons for food menu
    const toggleButtons = document.querySelectorAll('.toggle-availability');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const available = this.getAttribute('data-available') === '1' ? '0' : '1';
            
            // Here you would typically update via AJAX
            // For demo, we'll just simulate a successful update
            alert(`Menu item ${itemId} ${available === '1' ? 'enabled' : 'disabled'} successfully`);
            
            // Reload the page to reflect changes
            location.reload();
        });
    });
    
    // Edit menu item buttons
    const editMenuButtons = document.querySelectorAll('.edit-menu-item');
    editMenuButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const row = this.closest('tr');
            const name = row.cells[1].textContent;
            const description = row.cells[2].textContent;
            const price = parseFloat(row.cells[3].textContent.replace('$', ''));
            const category = row.cells[4].textContent;
            
            // Create edit modal
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h3>Edit Menu Item</h3>
                    <form id="edit-menu-form">
                        <input type="hidden" id="edit-id" name="id" value="${itemId}">
                        <div class="form-group">
                            <label for="edit-name">Name:</label>
                            <input type="text" id="edit-name" name="name" value="${name}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-description">Description:</label>
                            <textarea id="edit-description" name="description" required>${description}</textarea>
                        </div>
                        <div class="form-group">
                            <label for="edit-price">Price:</label>
                            <input type="number" id="edit-price" name="price" min="0.01" step="0.01" value="${price}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-category">Category:</label>
                            <select id="edit-category" name="category" required>
                                <option value="Breakfast" ${category === 'Breakfast' ? 'selected' : ''}>Breakfast</option>
                                <option value="Lunch" ${category === 'Lunch' ? 'selected' : ''}>Lunch</option>
                                <option value="Dinner" ${category === 'Dinner' ? 'selected' : ''}>Dinner</option>
                                <option value="Dessert" ${category === 'Dessert' ? 'selected' : ''}>Dessert</option>
                                <option value="Beverages" ${category === 'Beverages' ? 'selected' : ''}>Beverages</option>
                            </select>
                        </div>
                        <div class="form-group checkbox-group">
                            <label>Dietary Options:</label>
                            <div class="checkbox-container">
                                <input type="checkbox" id="edit-is_vegetarian" name="is_vegetarian" value="1">
                                <label for="edit-is_vegetarian">Vegetarian</label>
                            </div>
                            <div class="checkbox-container">
                                <input type="checkbox" id="edit-is_vegan" name="is_vegan" value="1">
                                <label for="edit-is_vegan">Vegan</label>
                            </div>
                            <div class="checkbox-container">
                                <input type="checkbox" id="edit-is_gluten_free" name="is_gluten_free" value="1">
                                <label for="edit-is_gluten_free">Gluten-Free</label>
                            </div>
                            <div class="checkbox-container">
                                <input type="checkbox" id="edit-is_special" name="is_special" value="1">
                                <label for="edit-is_special">Daily Special</label>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">Update Item</button>
                    </form>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Close modal functionality
            const close = modal.querySelector('.close');
            close.addEventListener('click', function() {
                document.body.removeChild(modal);
            });
            
            // Form submission
            const form = modal.querySelector('#edit-menu-form');
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Here you would typically make an AJAX request to update the item
                // For demo, we'll just simulate a successful update
                alert(`Menu item ${itemId} updated successfully`);
                document.body.removeChild(modal);
                
                // Reload the page to reflect changes
                location.reload();
            });
        });
    });
}