// Load data and populate dashboard
$(document).ready(function() {
    loadCategoryAnalysis();
    loadCustomerSummary();
    setupChurnPredictionForm();
});

// Smooth scroll navigation
$('.nav-link').click(function(e) {
    e.preventDefault();
    const targetId = $(this).attr('href');
    const targetElement = $(targetId);
    if (targetElement.length) {
        $('html, body').animate({
            scrollTop: targetElement.offset().top - 100
        }, 800);
    }
});

// Load Category Analysis
function loadCategoryAnalysis() {
    $.ajax({
        url: '/api/category-analysis',
        method: 'GET',
        success: function(data) {
            populateCategoryTable(data.categories);
            drawCategoryChart(data.categories);
        },
        error: function(error) {
            console.error('Error loading category data:', error);
            $('#categoryTableBody').html('<tr><td colspan="5" class="error">Error loading data</td></tr>');
        }
    });
}

// Populate Category Table
function populateCategoryTable(categories) {
    const tbody = $('#categoryTableBody');
    tbody.empty();
    
    categories.forEach(cat => {
        tbody.append(`
            <tr>
                <td><strong>${cat.category}</strong></td>
                <td>₹${formatNumber(cat.total_revenue)}</td>
                <td>₹${cat.avg_order_value.toFixed(2)}</td>
                <td>${Math.round(cat.order_count)}</td>
                <td>${cat.return_rate.toFixed(1)}%</td>
            </tr>
        `);
    });
}

// Draw Category Chart
function drawCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // Sort by revenue
    const sorted = categories.sort((a, b) => b.total_revenue - a.total_revenue);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(c => c.category),
            datasets: [
                {
                    label: 'Total Revenue (₹)',
                    data: sorted.map(c => c.total_revenue),
                    backgroundColor: '#048A81',
                    borderRadius: 5,
                    borderSkipped: false
                },
                {
                    label: 'Avg Order Value (₹)',
                    data: sorted.map(c => c.avg_order_value),
                    backgroundColor: '#EF7B45',
                    borderRadius: 5,
                    borderSkipped: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount (₹)'
                    }
                }
            }
        }
    });
}

// Load Customer Summary
function loadCustomerSummary() {
    $.ajax({
        url: '/api/customer-summary',
        method: 'GET',
        success: function(data) {
            $('#totalCustomers').text(data.total_customers.toLocaleString());
            $('#avgCustomerValue').text('₹' + formatNumber(data.avg_customer_value));
            $('#avgOrdersPerCustomer').text(data.avg_orders_per_customer.toFixed(2));
            
            populateTopCustomersTable(data.top_10_customers);
        },
        error: function(error) {
            console.error('Error loading customer data:', error);
        }
    });
}

// Populate Top Customers Table
function populateTopCustomersTable(customers) {
    const tbody = $('#topCustomersBody');
    tbody.empty();
    
    Object.entries(customers).forEach(([customerId, data]) => {
        tbody.append(`
            <tr>
                <td><strong>#${customerId}</strong></td>
                <td>₹${formatNumber(data[0])}</td>
                <td>${Math.round(data[1])}</td>
                <td>₹${data[2].toFixed(2)}</td>
            </tr>
        `);
    });
}

// Setup Churn Prediction Form
function setupChurnPredictionForm() {
    $('#churnForm').on('submit', function(e) {
        e.preventDefault();
        
        const data = {
            total_spend: parseFloat($('#totalSpend').val()),
            order_count: parseInt($('#orderCount').val()),
            days_since_order: parseInt($('#daysSinceOrder').val()),
            return_rate: parseFloat($('#returnRate').val()) / 100 || 0,
            avg_order_value: parseFloat($('#avgOrderValue').val()) || 50
        };
        
        $.ajax({
            url: '/api/predict-churn',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(result) {
                displayChurnResult(result);
            },
            error: function(error) {
                console.error('Error predicting churn:', error);
                alert('Error making prediction. Please try again.');
            }
        });
    });
}

// Display Churn Prediction Result
function displayChurnResult(result) {
    const probability = (result.churn_probability * 100).toFixed(1);
    const risk = result.churn_risk.toLowerCase();
    
    $('#churnProb').text(probability + '%');
    $('#churnRisk')
        .text(result.churn_risk)
        .removeClass('high medium low')
        .addClass(risk);
    $('#churnRecommendation').text(result.recommendation);
    
    $('#predictionResult').removeClass('hidden');
    
    // Smooth scroll to result
    $('html, body').animate({
        scrollTop: $('#predictionResult').offset().top - 100
    }, 500);
}

// Export Data
function exportData() {
    window.location.href = '/api/export-csv';
}

// Utility function to format numbers
function formatNumber(num) {
    return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
