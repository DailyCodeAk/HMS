/**
 * user.js - JavaScript functionality for the Hotel Management System user portal
 * Author: Akanimo Akpan
 * Team: WalnutMercury (Team 11)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all user portal functionality
    initializeBookingForm();
    initializeRoomFilters();
    initializeCalendarView();
    initializeRoomService();
    initializeProfileForms();
    initializeFoodOrder();
});

/**
 * Initialize booking form functionality
 */
function initializeBookingForm() {
    const bookingForm = document.querySelector('.booking-section form');
    if (!bookingForm) return;
    
    const checkInInput = document.getElementById('check_in');
    const checkOutInput = document.getElementById('check_out');
    const roomTypeSelect = document.getElementById('room_type');
    const roomCards = document.querySelectorAll('.room-card');
    
    // Set minimum dates for check-in and check-out
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    
    checkInInput.min = formatDate(today);
    checkOutInput.min = formatDate(tomorrow);
    
    // Set default values if not already set
    if (!checkInInput.value) {
        checkInInput.value = formatDate(today);
    }
    
    if (!checkOutInput.value) {
        checkOutInput.value = formatDate(tomorrow);
    }
    
    // Update check-out min date when check-in changes
    checkInInput.addEventListener('change', function() {
        const selectedDate = new Date(this.value);
        const nextDay = new Date(selectedDate);
        nextDay.setDate(selectedDate.getDate() + 1);
        
        checkOutInput.min = formatDate(nextDay);
        
        // If check-out date is before new min date, update it
        if (new Date(checkOutInput.value) <= selectedDate) {
            checkOutInput.value = formatDate(nextDay);
        }
        
        // Fetch available rooms for the new dates
        fetchAvailableRooms();
    });
    
    // Update room list when check-out changes
    checkOutInput.addEventListener('change', function() {
        fetchAvailableRooms();
    });
    
    // Filter room cards by type
    if (roomTypeSelect) {
        roomTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            
            roomCards.forEach(card => {
                if (selectedType === 'all' || card.getAttribute('data-type') === selectedType) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Validate form before submission
    bookingForm.addEventListener('submit', function(event) {
        const selectedRoom = document.querySelector('input[name="room_id"]:checked');
        
        if (!selectedRoom) {
            event.preventDefault();
            alert('Please select a room');
            return;
        }
        
        const checkInDate = new Date(checkInInput.value);
        const checkOutDate = new Date(checkOutInput.value);
        
        if (checkOutDate <= checkInDate) {
            event.preventDefault();
            alert('Check-out date must be after check-in date');
            return;
        }
    });
    
    // Helper function to fetch available rooms via AJAX
    function fetchAvailableRooms() {
        // In a real implementation, this would make an AJAX request
        // For the demo, we'll just simulate filtering rooms
        console.log('Fetching available rooms...');
        
        // Simulate a delay and show all rooms (in production, this would show only available rooms)
        setTimeout(() => {
            roomCards.forEach(card => {
                card.style.display = 'flex';
            });
        }, 500);
    }
}

/**
 * Initialize room filters
 */
function initializeRoomFilters() {
    const filterInputs = document.querySelectorAll('.room-filters input');
    if (!filterInputs.length) return;
    
    filterInputs.forEach(input => {
        input.addEventListener('change', filterRooms);
    });
    
    function filterRooms() {
        const minPrice = parseFloat(document.getElementById('min_price')?.value || 0);
        const maxPrice = parseFloat(document.getElementById('max_price')?.value || 10000);
        const capacity = parseInt(document.getElementById('capacity')?.value || 1);
        const roomType = document.getElementById('room_type')?.value;
        
        const roomCards = document.querySelectorAll('.room-card');
        
        roomCards.forEach(card => {
            const cardPrice = parseFloat(card.getAttribute('data-price'));
            const cardCapacity = parseInt(card.getAttribute('data-capacity'));
            const cardType = card.getAttribute('data-type');
            
            const priceMatch = cardPrice >= minPrice && cardPrice <= maxPrice;
            const capacityMatch = cardCapacity >= capacity;
            const typeMatch = roomType === 'all' || cardType === roomType;
            
            if (priceMatch && capacityMatch && typeMatch) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    }
}

/**
 * Initialize calendar view
 */
function initializeCalendarView() {
    const calendarContainer = document.querySelector('.calendar-container');
    if (!calendarContainer) return;
    
    const currentDate = new Date();
    const currentMonth = currentDate.getMonth();
    const currentYear = currentDate.getFullYear();
    
    renderCalendar(currentMonth, currentYear);
    
    // Prev and next month buttons
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    
    if (prevMonthBtn) {
        prevMonthBtn.addEventListener('click', function() {
            const monthDisplay = document.getElementById('current-month');
            const [month, year] = monthDisplay.getAttribute('data-date').split('-');
            
            let newMonth = parseInt(month) - 1;
            let newYear = parseInt(year);
            
            if (newMonth < 0) {
                newMonth = 11;
                newYear--;
            }
            
            renderCalendar(newMonth, newYear);
        });
    }
    
    if (nextMonthBtn) {
        nextMonthBtn.addEventListener('click', function() {
            const monthDisplay = document.getElementById('current-month');
            const [month, year] = monthDisplay.getAttribute('data-date').split('-');
            
            let newMonth = parseInt(month) + 1;
            let newYear = parseInt(year);
            
            if (newMonth > 11) {
                newMonth = 0;
                newYear++;
            }
            
            renderCalendar(newMonth, newYear);
        });
    }
    
    function renderCalendar(month, year) {
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        const monthDisplay = document.getElementById('current-month');
        
        if (monthDisplay) {
            monthDisplay.textContent = `${monthNames[month]} ${year}`;
            monthDisplay.setAttribute('data-date', `${month}-${year}`);
        }
        
        const calendarBody = document.querySelector('.calendar');
        if (!calendarBody) return;
        
        calendarBody.innerHTML = '';
        
        // Create calendar days
        let date = 1;
        for (let i = 0; i < 6; i++) {
            for (let j = 0; j < 7; j++) {
                if (i === 0 && j < firstDay) {
                    // Empty cells before first day
                    const emptyCell = document.createElement('div');
                    emptyCell.className = 'calendar-day empty';
                    calendarBody.appendChild(emptyCell);
                } else if (date > daysInMonth) {
                    // Empty cells after last day
                    const emptyCell = document.createElement('div');
                    emptyCell.className = 'calendar-day empty';
                    calendarBody.appendChild(emptyCell);
                } else {
                    // Calendar day
                    const dayCell = document.createElement('div');
                    dayCell.className = 'calendar-day';
                    
                    // Check if it's today
                    const currentDate = new Date();
                    if (date === currentDate.getDate() && month === currentDate.getMonth() && year === currentDate.getFullYear()) {
                        dayCell.classList.add('today');
                    }
                    
                    dayCell.innerHTML = `
                        <div class="date">${date}</div>
                        <div class="events"></div>
                    `;
                    
                    calendarBody.appendChild(dayCell);
                    date++;
                }
            }
        }
        
        // In a real app, you would add booking events to the calendar here
        addEventsToCalendar();
    }
    
    function addEventsToCalendar() {
        // This would typically fetch booking data via AJAX
        // For demo, we'll add some mock events
        const events = [
            { date: new Date(currentYear, currentMonth, 15), title: 'Check-in: Room 101' },
            { date: new Date(currentYear, currentMonth, 20), title: 'Check-out: Room 101' },
            { date: new Date(currentYear, currentMonth, 10), title: 'Check-in: Room 202' },
            { date: new Date(currentYear, currentMonth, 12), title: 'Check-out: Room 202' }
        ];
        
        events.forEach(event => {
            const day = event.date.getDate();
            const month = event.date.getMonth();
            const year = event.date.getFullYear();
            
            if (month === currentMonth && year === currentYear) {
                const dayCell = document.querySelector(`.calendar-day:not(.empty):nth-child(${day + document.querySelectorAll('.calendar-day.empty').length})`);
                
                if (dayCell) {
                    const eventsContainer = dayCell.querySelector('.events');
                    const eventElement = document.createElement('div');
                    eventElement.className = 'event';
                    eventElement.textContent = event.title;
                    eventsContainer.appendChild(eventElement);
                }
            }
        });
    }
}

/**
 * Initialize room service functionality
 */
function initializeRoomService() {
    const roomServiceForm = document.querySelector('.room-service-section form');
    if (!roomServiceForm) return;
    
    const serviceTypeSelect = document.getElementById('service_type');
    const notesTextarea = document.getElementById('notes');
    
    if (serviceTypeSelect && notesTextarea) {
        // Show/hide notes placeholder based on service type
        serviceTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            
            switch (selectedType) {
                case 'Food':
                    notesTextarea.placeholder = 'Enter your food order details...';
                    break;
                case 'Cleaning':
                    notesTextarea.placeholder = 'Specify cleaning needs...';
                    break;
                case 'Maintenance':
                    notesTextarea.placeholder = 'Describe the issue that needs maintenance...';
                    break;
                case 'Amenities':
                    notesTextarea.placeholder = 'List the amenities you need...';
                    break;
                default:
                    notesTextarea.placeholder = 'Enter request details...';
            }
        });
        
        // Trigger change event to set initial placeholder
        const event = new Event('change');
        serviceTypeSelect.dispatchEvent(event);
    }
    
    // Form validation
    roomServiceForm.addEventListener('submit', function(event) {
        if (!notesTextarea.value.trim()) {
            event.preventDefault();
            alert('Please provide details for your request');
            return;
        }
    });
}

/**
 * Initialize profile forms
 */
function initializeProfileForms() {
    const profileForm = document.querySelector('.profile-setup form');
    if (!profileForm) return;
    
    profileForm.addEventListener('submit', function(event) {
        const nameInput = document.getElementById('name');
        const phoneInput = document.getElementById('phone');
        const addressInput = document.getElementById('address');
        
        if (!nameInput.value.trim() || !phoneInput.value.trim() || !addressInput.value.trim()) {
            event.preventDefault();
            alert('Please fill in all required fields');
            return;
        }
        
        // Basic phone number validation
        const phonePattern = /^\d{3}[-\s]?\d{3}[-\s]?\d{4}$/;
        if (!phonePattern.test(phoneInput.value.trim())) {
            event.preventDefault();
            alert('Please enter a valid phone number (e.g., 555-123-4567)');
            return;
        }
    });
}

/**
 * Initialize food ordering functionality
 */
function initializeFoodOrder() {
    // Menu tabs functionality
    const tabButtons = document.querySelectorAll('.food-menu-section .tab-btn');
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
    
    // Food order functionality
    const orderItems = [];
    const addToOrderButtons = document.querySelectorAll('.add-to-order');
    const orderSummary = document.getElementById('order-summary');
    const orderItemsContainer = document.getElementById('order-items');
    const orderTotalElement = document.getElementById('order-total');
    const clearOrderButton = document.getElementById('clear-order');
    const placeOrderButton = document.getElementById('place-order');
    
    if (addToOrderButtons.length && orderSummary) {
        // Add to order buttons
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
        if (clearOrderButton) {
            clearOrderButton.addEventListener('click', function() {
                orderItems.length = 0;
                updateOrderSummary();
            });
        }
        
        // Place order
        if (placeOrderButton) {
            placeOrderButton.addEventListener('click', function() {
                const orderModal = document.getElementById('order-modal');
                if (!orderModal) return;
                
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
                }
            });
        }
    }
}

/**
 * Helper function to format a date as YYYY-MM-DD
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}