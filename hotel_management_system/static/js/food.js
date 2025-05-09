/**
 * food.js - JavaScript functionality for food management in the Hotel Management System
 * Author: Akanimo Akpan
 * Team: WalnutMercury (Team 11)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all food management functionality
    initializeMenuTabs();
    initializeFoodOrdering();
    initializeAdminMenuManagement();
    initializeOrderProcessing();
    initializeFoodReports();
});

/**
 * Initialize menu tabs functionality
 */
function initializeMenuTabs() {
    const tabButtons = document.querySelectorAll('.menu-tabs .tab-btn');
    const menuCategories = document.querySelectorAll('.menu-category');
    
    if (!tabButtons.length) return;
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            const category = this.getAttribute('data-category');
            
            // Show/hide categories based on selected tab
            if (category === 'all') {
                menuCategories.forEach(cat => cat.style.display = 'block');
            } else {
                menuCategories.forEach(cat => {
                    if (cat.getAttribute('data-category') === category) {
                        cat.style.display = 'block';
                    } else {
                        cat.style.display = 'none';
                    }
                });
            }
        });
    });
}

/**
 * Initialize food ordering system for guests
 */
function initializeFoodOrdering() {
    // Variables for order management
    let orderItems = [];
    const addToOrderButtons = document.querySelectorAll('.add-to-order');
    const orderSummary = document.getElementById('order-summary');
    const orderItemsContainer = document.getElementById('order-items');
    const orderTotalElement = document.getElementById('order-total');
    const clearOrderButton = document.getElementById('clear-order');
    const placeOrderButton = document.getElementById('place-order');
    const orderModal = document.getElementById('order-modal');
    
    if (!orderSummary) return;
    
    // Add to order functionality
    addToOrderButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const itemName = this.getAttribute('data-name');
            const itemPrice = parseFloat(this.getAttribute('data-price'));
            
            // Check if item already in order
            const existingItem = orderItems.find(item => item.id === itemId);
            
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                orderItems.push({
                    id: itemId,
                    name: itemName,
                    price: itemPrice,
                    quantity: 1
                });
            }
            
            // Show notification
            showNotification(`Added ${itemName} to order`);
            
            // Update order summary
            updateOrderSummary();
        });
    });
    
    // Update order summary display
    function updateOrderSummary() {
        if (orderItems.length === 0) {
            orderSummary.style.display = 'none';
            return;
        }
        
        orderSummary.style.display = 'block';
        
        // Update order items display
        orderItemsContainer.innerHTML = '';
        let total = 0;
        
        orderItems.forEach((item, index) => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;
            
            const itemElement = document.createElement('div');
            itemElement.className = 'order-item';
            itemElement.innerHTML = `
                <div class="item-info">
                    <span class="item-name">${item.name}</span>
                    <span class="item-price">$${item.price.toFixed(2)} x ${item.quantity}</span>
                </div>
                <div class="item-actions">
                    <button class="quantity-btn decrease" data-index="${index}">-</button>
                    <span class="quantity">${item.quantity}</span>
                    <button class="quantity-btn increase" data-index="${index}">+</button>
                    <button class="remove-btn" data-index="${index}">×</button>
                </div>
            `;
            
            orderItemsContainer.appendChild(itemElement);
        });
        
        // Update total
        orderTotalElement.textContent = total.toFixed(2);
        
        // Add event listeners for quantity buttons
        addQuantityButtonListeners();
    }
    
    // Add listeners for quantity adjustment buttons
    function addQuantityButtonListeners() {
        const decreaseButtons = document.querySelectorAll('.quantity-btn.decrease');
        const increaseButtons = document.querySelectorAll('.quantity-btn.increase');
        const removeButtons = document.querySelectorAll('.remove-btn');
        
        decreaseButtons.forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                if (orderItems[index].quantity > 1) {
                    orderItems[index].quantity -= 1;
                } else {
                    orderItems.splice(index, 1);
                }
                updateOrderSummary();
            });
        });
        
        increaseButtons.forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                orderItems[index].quantity += 1;
                updateOrderSummary();
            });
        });
        
        removeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                const itemName = orderItems[index].name;
                orderItems.splice(index, 1);
                showNotification(`Removed ${itemName} from order`);
                updateOrderSummary();
            });
        });
    }
    
    // Clear order functionality
    if (clearOrderButton) {
        clearOrderButton.addEventListener('click', function() {
            if (orderItems.length === 0) return;
            
            if (confirm('Are you sure you want to clear your order?')) {
                orderItems = [];
                updateOrderSummary();
                showNotification('Order cleared');
            }
        });
    }
    
    // Place order functionality
    if (placeOrderButton && orderModal) {
        placeOrderButton.addEventListener('click', function() {
            if (orderItems.length === 0) {
                alert('Please add items to your order first');
                return;
            }
            
            // Show modal
            orderModal.style.display = 'block';
            
            // Create hidden fields for order items
            const orderSummaryHidden = document.getElementById('order-summary-hidden');
            if (orderSummaryHidden) {
                orderSummaryHidden.innerHTML = '';
                
                orderItems.forEach((item, index) => {
                    const idField = document.createElement('input');
                    idField.type = 'hidden';
                    idField.name = `items[${index}][menu_item_id]`;
                    idField.value = item.id;
                    
                    const quantityField = document.createElement('input');
                    quantityField.type = 'hidden';
                    quantityField.name = `items[${index}][quantity]`;
                    quantityField.value = item.quantity;
                    
                    orderSummaryHidden.appendChild(idField);
                    orderSummaryHidden.appendChild(quantityField);
                });
            }
            
            // Close modal button
            const closeButton = orderModal.querySelector('.close');
            if (closeButton) {
                closeButton.addEventListener('click', function() {
                    orderModal.style.display = 'none';
                });
            }
            
            // Order type change
            const orderTypeSelect = document.getElementById('order-type');
            const restaurantFields = document.getElementById('restaurant-fields');
            const roomServiceFields = document.getElementById('room-service-fields');
            
            if (orderTypeSelect && restaurantFields && roomServiceFields) {
                orderTypeSelect.addEventListener('change', function() {
                    const orderType = this.value;
                    
                    if (orderType === 'restaurant') {
                        restaurantFields.style.display = 'block';
                        roomServiceFields.style.display = 'none';
                    } else {
                        restaurantFields.style.display = 'none';
                        roomServiceFields.style.display = 'block';
                    }
                });
                
                // Trigger change event to set initial display
                orderTypeSelect.dispatchEvent(new Event('change'));
            }
            
            // Form submission
            const orderForm = document.getElementById('complete-order-form');
            if (orderForm) {
                orderForm.addEventListener('submit', function(event) {
                    // Additional validation could be added here
                    // For example, checking if table number is provided for restaurant orders
                    
                    if (orderTypeSelect.value === 'restaurant') {
                        const tableNumber = document.getElementById('table-number');
                        if (tableNumber && !tableNumber.value.trim()) {
                            event.preventDefault();
                            alert('Please provide a table number');
                            return;
                        }
                    } else {
                        const bookingId = document.getElementById('booking-id');
                        if (bookingId && (!bookingId.value || bookingId.value === '')) {
                            event.preventDefault();
                            alert('Please select a room for delivery');
                            return;
                        }
                    }
                    
                    // In a production environment, you might want to disable the submit button
                    // to prevent double submissions while the form is being processed
                });
            }
        });
    }
    
    // Filter menu items based on search and dietary preferences
    const menuSearchForm = document.querySelector('.menu-search form');
    if (menuSearchForm) {
        menuSearchForm.addEventListener('submit', function(event) {
            // Form will be submitted normally to server for processing
            // But we could add additional client-side filtering here if needed
        });
        
        // Instant filtering for dietary requirements
        const dietaryCheckboxes = document.querySelectorAll('.dietary-filters input[type="checkbox"]');
        dietaryCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                // In a real implementation, this would do client-side filtering
                // For the demo, we'll just submit the form to reload with server-side filtering
                menuSearchForm.submit();
            });
        });
    }
}

/**
 * Initialize admin menu management
 */
function initializeAdminMenuManagement() {
    // Toggle menu item availability
    const toggleButtons = document.querySelectorAll('.toggle-availability');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const available = this.getAttribute('data-available') === '1' ? 0 : 1;
            const itemName = this.closest('tr').querySelector('td:nth-child(2)').textContent;
            
            // Here you would typically update via AJAX
            // For demo, we'll submit a form to update the backend
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/food/admin/toggle_menu_item';
            form.style.display = 'none';
            
            const idInput = document.createElement('input');
            idInput.type = 'hidden';
            idInput.name = 'id';
            idInput.value = itemId;
            
            const availableInput = document.createElement('input');
            availableInput.type = 'hidden';
            availableInput.name = 'available';
            availableInput.value = available;
            
            form.appendChild(idInput);
            form.appendChild(availableInput);
            document.body.appendChild(form);
            
            // Confirm action
            if (confirm(`Are you sure you want to ${available ? 'enable' : 'disable'} ${itemName}?`)) {
                form.submit();
            } else {
                document.body.removeChild(form);
            }
        });
    });
    
    // Edit menu item
    const editButtons = document.querySelectorAll('.edit-menu-item');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            const row = this.closest('tr');
            const name = row.cells[1].textContent;
            const description = row.cells[2].textContent;
            const price = parseFloat(row.cells[3].textContent.replace('$', ''));
            const category = row.cells[4].textContent;
            
            // Get dietary information
            const dietaryCell = row.cells[5].textContent;
            const isVegetarian = dietaryCell.includes('V');
            const isVegan = dietaryCell.includes('VG');
            const isGlutenFree = dietaryCell.includes('GF');
            const isSpecial = dietaryCell.includes('Special');
            
            // Create edit modal
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h3>Edit Menu Item</h3>
                    <form id="edit-menu-form" action="/food/admin/update_menu_item" method="POST">
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
                                <input type="checkbox" id="edit-is_vegetarian" name="is_vegetarian" value="1" ${isVegetarian ? 'checked' : ''}>
                                <label for="edit-is_vegetarian">Vegetarian</label>
                            </div>
                            <div class="checkbox-container">
                                <input type="checkbox" id="edit-is_vegan" name="is_vegan" value="1" ${isVegan ? 'checked' : ''}>
                                <label for="edit-is_vegan">Vegan</label>
                            </div>
                            <div class="checkbox-container">
                                <input type="checkbox" id="edit-is_gluten_free" name="is_gluten_free" value="1" ${isGlutenFree ? 'checked' : ''}>
                                <label for="edit-is_gluten_free">Gluten-Free</label>
                            </div>
                            <div class="checkbox-container">
                                <input type="checkbox" id="edit-is_special" name="is_special" value="1" ${isSpecial ? 'checked' : ''}>
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
            
            // Form validation
            const form = modal.querySelector('#edit-menu-form');
            form.addEventListener('submit', function(e) {
                const name = document.getElementById('edit-name').value;
                const description = document.getElementById('edit-description').value;
                const price = document.getElementById('edit-price').value;
                
                if (!name.trim() || !description.trim() || !price.trim()) {
                    e.preventDefault();
                    alert('Please fill in all required fields');
                    return;
                }
                
                if (isNaN(parseFloat(price)) || parseFloat(price) <= 0) {
                    e.preventDefault();
                    alert('Please enter a valid price');
                    return;
                }
            });
        });
    });
    
    // Add new menu item form validation
    const addMenuForm = document.querySelector('form[action*="add_menu_item"]');
    if (addMenuForm) {
        addMenuForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name').value;
            const description = document.getElementById('description').value;
            const price = document.getElementById('price').value;
            
            if (!name.trim() || !description.trim() || !price.trim()) {
                e.preventDefault();
                alert('Please fill in all required fields');
                return;
            }
            
            if (isNaN(parseFloat(price)) || parseFloat(price) <= 0) {
                e.preventDefault();
                alert('Please enter a valid price');
                return;
            }
        });
    }
}

/**
 * Initialize order processing for admin
 */
function initializeOrderProcessing() {
    // Tab switching for order status
    const statusTabs = document.querySelectorAll('.status-tabs .tab-btn');
    const orderRows = document.querySelectorAll('#orders-table tbody tr');
    
    if (statusTabs.length) {
        statusTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const status = this.getAttribute('data-status');
                
                // Update active tab
                statusTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Filter order rows
                orderRows.forEach(row => {
                    if (status === 'all' || row.getAttribute('data-status') === status) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // View order items
    const viewItemsButtons = document.querySelectorAll('.view-items');
    viewItemsButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.getAttribute('data-id');
            
            // In a real app, this would fetch order items via AJAX
            // For demo purposes, show a modal with mock data
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.id = 'items-modal';
            modal.style.display = 'block';
            
            // Get any existing order data from the row
            const row = this.closest('tr');
            const guestName = row.cells[1].textContent;
            const orderType = row.cells[2].textContent;
            const location = row.cells[3].textContent;
            const total = row.cells[5].textContent;
            
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h3>Order #${orderId} Details</h3>
                    <p><strong>Guest:</strong> ${guestName}</p>
                    <p><strong>Type:</strong> ${orderType}</p>
                    <p><strong>Location:</strong> ${location}</p>
                    
                    <div id="items-container">
                        <table class="items-table">
                            <thead>
                                <tr>
                                    <th>Item</th>
                                    <th>Quantity</th>
                                    <th>Price</th>
                                    <th>Subtotal</th>
                                </tr>
                            </thead>
                            <tbody id="items-list">
                                <!-- Items will be loaded here via AJAX -->
                                <tr><td colspan="4">Loading items...</td></tr>
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="3"><strong>Total</strong></td>
                                    <td><strong>${total}</strong></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Close modal functionality
            const closeBtn = modal.querySelector('.close');
            closeBtn.addEventListener('click', function() {
                document.body.removeChild(modal);
            });
            
            // In a real app, this would fetch items via AJAX
            // For demo, we'll simulate with mock data after a delay
            setTimeout(() => {
                const itemsList = document.getElementById('items-list');
                if (itemsList) {
                    // Mock items - in a real app, these would come from the server
                    const mockItems = [
                        { name: 'Cheeseburger', quantity: 2, price: 17.99 },
                        { name: 'French Fries', quantity: 1, price: 5.99 },
                        { name: 'Soft Drink', quantity: 2, price: 2.99 }
                    ];
                    
                    let itemsHtml = '';
                    mockItems.forEach(item => {
                        const subtotal = (item.price * item.quantity).toFixed(2);
                        itemsHtml += `
                            <tr>
                                <td>${item.name}</td>
                                <td>${item.quantity}</td>
                                <td>$${item.price.toFixed(2)}</td>
                                <td>$${subtotal}</td>
                            </tr>
                        `;
                    });
                    
                    itemsList.innerHTML = itemsHtml;
                }
            }, 500);
        });
    });
    
    // Update order status
    const updateStatusButtons = document.querySelectorAll('.update-status');
    updateStatusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.getAttribute('data-id');
            const newStatus = this.getAttribute('data-status');
            
            // Create and submit a form to update status
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/food/admin/update_order_status';
            form.style.display = 'none';
            
            const orderIdInput = document.createElement('input');
            orderIdInput.type = 'hidden';
            orderIdInput.name = 'order_id';
            orderIdInput.value = orderId;
            
            const statusInput = document.createElement('input');
            statusInput.type = 'hidden';
            statusInput.name = 'status';
            statusInput.value = newStatus;
            
            form.appendChild(orderIdInput);
            form.appendChild(statusInput);
            document.body.appendChild(form);
            
            // If status is 'cancelled', confirm first
            if (newStatus === 'cancelled') {
                if (confirm('Are you sure you want to cancel this order?')) {
                    form.submit();
                } else {
                    document.body.removeChild(form);
                }
            } else {
                form.submit();
            }
        });
    });
}

/**
 * Initialize food reports charts and filters
 */
function initializeFoodReports() {
    // If Chart.js is loaded and charts exist, create charts
    if (typeof Chart !== 'undefined') {
        const categoryChart = document.getElementById('category-chart');
        const itemsChart = document.getElementById('items-chart');
        
        if (categoryChart) {
            createCategoryChart(categoryChart);
        }
        
        if (itemsChart) {
            createItemsChart(itemsChart);
        }
    }
    
    // Report date range form
    const reportForm = document.querySelector('.form-container form');
    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            const startDate = document.getElementById('start_date').value;
            const endDate = document.getElementById('end_date').value;
            
            if (!startDate || !endDate) {
                e.preventDefault();
                alert('Please select both start and end dates');
                return;
            }
            
            if (new Date(startDate) > new Date(endDate)) {
                e.preventDefault();
                alert('Start date must be before end date');
                return;
            }
        });
    }
}

/**
 * Create category chart for food sales
 */
function createCategoryChart(canvas) {
    // Get data from data attributes
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
    // Get data from data attributes
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
 * Show notification message
 */
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Position in bottom right corner
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = type === 'success' ? '#48bb78' : '#f56565';
    notification.style.color = 'white';
    notification.style.padding = '10px 20px';
    notification.style.borderRadius = '4px';
    notification.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
    notification.style.zIndex = '1000';
    
    // Animate in
    notification.style.transform = 'translateY(100%)';
    notification.style.opacity = '0';
    notification.style.transition = 'transform 0.3s, opacity 0.3s';
    
    setTimeout(() => {
        notification.style.transform = 'translateY(0)';
        notification.style.opacity = '1';
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateY(100%)';
        notification.style.opacity = '0';
        
        // Remove from DOM after animation
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}