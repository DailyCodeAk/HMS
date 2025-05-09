document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const menuCategories = document.querySelectorAll('.menu-category');
    
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
    
    // Order functionality
    let orderItems = [];
    const orderSummary = document.getElementById('order-summary');
    const orderItemsContainer = document.getElementById('order-items');
    const orderTotalElement = document.getElementById('order-total');
    const clearOrderButton = document.getElementById('clear-order');
    const placeOrderButton = document.getElementById('place-order');
    const orderModal = document.getElementById('order-modal');
    const closeModalButton = orderModal.querySelector('.close');
    const orderTypeSelect = document.getElementById('order-type');
    const restaurantFields = document.getElementById('restaurant-fields');
    const roomServiceFields = document.getElementById('room-service-fields');
    
    // Add to order buttons
    const addToOrderButtons = document.querySelectorAll('.add-to-order');
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
            
            updateOrderSummary();
        });
    });
    
    // Update order summary
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
                orderItems.splice(index, 1);
                updateOrderSummary();
            });
        });
    }
    
    // Clear order
    clearOrderButton.addEventListener('click', function() {
        orderItems = [];
        updateOrderSummary();
    });
    
    // Place order
    placeOrderButton.addEventListener('click', function() {
        // Show modal
        orderModal.style.display = 'block';
        
        // Create hidden fields for order items
        const orderSummaryHidden = document.getElementById('order-summary-hidden');
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
    });
    
    // Close modal
    closeModalButton.addEventListener('click', function() {
        orderModal.style.display = 'none';
    });
    
    // Order type change
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
}); 