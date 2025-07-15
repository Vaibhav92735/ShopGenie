from flask import Flask, request, jsonify, render_template_string
import uuid
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp3', 'wav', 'ogg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Generate unique user ID based on username
def get_user_id(username):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, username))

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E Kart - Smart Shopping Assistant</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        animation: {
                            'float': 'float 3s ease-in-out infinite',
                            'slide-up': 'slideUp 0.5s ease-out',
                            'pulse-slow': 'pulse 2s infinite',
                            'bounce-slow': 'bounce 2s infinite',
                        },
                        keyframes: {
                            float: {
                                '0%, 100%': { transform: 'translateY(0px)' },
                                '50%': { transform: 'translateY(-10px)' },
                            },
                            slideUp: {
                                '0%': { transform: 'translateY(30px)', opacity: '0' },
                                '100%': { transform: 'translateY(0)', opacity: '1' },
                            }
                        }
                    }
                }
            }
        </script>
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                position: relative;
                overflow-x: hidden;
            }
            
            .bg-pattern {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
                z-index: 0;
            }
            
            .glass-effect {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .card-hover {
                transition: all 0.3s ease;
            }
            
            .card-hover:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }
            
            .gradient-text {
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .loading {
                position: relative;
                overflow: hidden;
            }
            
            .loading::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
                animation: loading 1.5s infinite;
            }
            
            @keyframes loading {
                0% { left: -100%; }
                100% { left: 100%; }
            }
            
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 16px 24px;
                border-radius: 12px;
                color: white;
                font-weight: 500;
                transform: translateX(400px);
                transition: transform 0.3s ease;
                z-index: 1000;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            .notification.show {
                transform: translateX(0);
            }
            
            .notification.success {
                background: linear-gradient(45deg, #4ade80, #22c55e);
            }
            
            .notification.error {
                background: linear-gradient(45deg, #f87171, #ef4444);
            }
        </style>
    </head>
    <body class="font-sans antialiased">
        <div class="bg-pattern"></div>
        
        <div class="relative z-10 min-h-screen flex items-center justify-center p-4">
            <div class="container max-w-4xl mx-auto">
                <!-- Header -->
                <div class="text-center mb-12">
                    <h1 class="text-6xl font-bold text-white mb-4 animate-float">
                        🛒 E Kart
                    </h1>
                    <p class="text-xl text-white/80 mb-8">Smart Shopping Assistant with AI</p>
                    <div class="flex justify-center space-x-4 text-white/60">
                        <span class="flex items-center"><span class="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>Text Queries</span>
                        <span class="flex items-center"><span class="w-2 h-2 bg-blue-400 rounded-full mr-2 animate-pulse"></span>Image Upload</span>
                        <span class="flex items-center"><span class="w-2 h-2 bg-purple-400 rounded-full mr-2 animate-pulse"></span>Voice Commands</span>
                    </div>
                </div>

                <!-- Login Form -->
                <div id="loginSection" class="max-w-md mx-auto mb-8">
                    <form id="userForm" class="glass-effect rounded-2xl p-8 card-hover animate-slide-up">
                        <div class="text-center mb-6">
                            <h2 class="text-2xl font-bold text-white mb-2">Welcome Back!</h2>
                            <p class="text-white/70">Sign in to continue shopping</p>
                        </div>
                        <div class="mb-6">
                            <input 
                                type="text" 
                                id="username" 
                                placeholder="Enter your username" 
                                required 
                                class="w-full p-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-white/40 transition-all duration-200"
                            >
                        </div>
                        <button 
                            type="submit" 
                            class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 font-semibold shadow-lg"
                        >
                            <span class="flex items-center justify-center">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
                                </svg>
                                Sign In
                            </span>
                        </button>
                    </form>
                </div>

                <!-- Main Dashboard -->
                <div id="userSection" class="hidden animate-slide-up">
                    <!-- Welcome Header -->
                    <div class="glass-effect rounded-2xl p-6 mb-8 text-center card-hover">
                        <h2 class="text-3xl font-bold text-white mb-2">
                            Welcome back, <span id="displayUsername" class="gradient-text"></span>! 👋
                        </h2>
                        <p class="text-white/70">What would you like to add to your cart today?</p>
                    </div>

                    <div class="grid lg:grid-cols-3 gap-8">
                        <!-- Input Methods -->
                        <div class="lg:col-span-2 space-y-6">
                            <!-- Text Query -->
                            <div class="glass-effect rounded-2xl p-6 card-hover">
                                <div class="flex items-center mb-4">
                                    <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center mr-3">
                                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                                        </svg>
                                    </div>
                                    <h3 class="text-xl font-bold text-white">Text Query</h3>
                                </div>
                                <form id="textForm" action="/process-text/" method="POST">
                                    <div class="mb-4">
                                        <input 
                                            type="text" 
                                            name="user_query" 
                                            placeholder="Try: 'Add milk to cart' or 'Show my cart'" 
                                            required 
                                            class="w-full p-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-green-400 transition-all duration-200"
                                        >
                                    </div>
                                    <button 
                                        type="submit" 
                                        class="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-3 rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-200 transform hover:scale-105 font-semibold"
                                    >
                                        Send Query
                                    </button>
                                </form>
                            </div>

                            <!-- Image Upload -->
                            <div class="glass-effect rounded-2xl p-6 card-hover">
                                <div class="flex items-center mb-4">
                                    <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center mr-3">
                                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                        </svg>
                                    </div>
                                    <h3 class="text-xl font-bold text-white">Image Recognition</h3>
                                </div>
                                <form id="imageForm" action="/process-image/" method="POST" enctype="multipart/form-data">
                                    <div class="mb-4">
                                        <label class="block w-full">
                                            <input 
                                                type="file" 
                                                name="image" 
                                                accept="image/*" 
                                                required 
                                                class="hidden"
                                                onchange="handleFileSelect(this, 'imagePreview')"
                                            >
                                            <div class="w-full p-8 border-2 border-dashed border-white/30 rounded-xl text-center cursor-pointer hover:border-white/50 transition-all duration-200">
                                                <div id="imagePreview" class="text-white/70">
                                                    <svg class="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                                                    </svg>
                                                    <p>Click to upload an image</p>
                                                    <p class="text-sm mt-2 opacity-60">PNG, JPG, JPEG up to 10MB</p>
                                                </div>
                                            </div>
                                        </label>
                                    </div>
                                    <button 
                                        type="submit" 
                                        class="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white py-3 rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-200 transform hover:scale-105 font-semibold"
                                    >
                                        Analyze Image
                                    </button>
                                </form>
                            </div>

                            <!-- Voice Upload -->
                            <div class="glass-effect rounded-2xl p-6 card-hover">
                                <div class="flex items-center mb-4">
                                    <div class="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center mr-3">
                                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                                        </svg>
                                    </div>
                                    <h3 class="text-xl font-bold text-white">Voice Command</h3>
                                </div>
                                <form id="voiceForm" action="/process-voice/" method="POST" enctype="multipart/form-data">
                                    <div class="mb-4">
                                        <label class="block w-full">
                                            <input 
                                                type="file" 
                                                name="audio" 
                                                accept="audio/*" 
                                                required 
                                                class="hidden"
                                                onchange="handleFileSelect(this, 'audioPreview')"
                                            >
                                            <div class="w-full p-8 border-2 border-dashed border-white/30 rounded-xl text-center cursor-pointer hover:border-white/50 transition-all duration-200">
                                                <div id="audioPreview" class="text-white/70">
                                                    <svg class="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V3a1 1 0 011 1v11.586l2.707 2.707A1 1 0 0120 19H4a1 1 0 01-.707-1.707L6 14.586V4a1 1 0 011-1h6a1 1 0 011 1v0z"></path>
                                                    </svg>
                                                    <p>Click to upload audio</p>
                                                    <p class="text-sm mt-2 opacity-60">MP3, WAV, OGG</p>
                                                </div>
                                            </div>
                                        </label>
                                    </div>
                                    <button 
                                        type="submit" 
                                        class="w-full bg-gradient-to-r from-purple-500 to-purple-600 text-white py-3 rounded-xl hover:from-purple-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 font-semibold"
                                    >
                                        Process Voice
                                    </button>
                                </form>
                            </div>
                        </div>

                        <!-- Cart Section -->
                        <div class="lg:col-span-1">
                            <div class="glass-effect rounded-2xl p-6 card-hover sticky top-8">
                                <div class="flex items-center mb-6">
                                    <div class="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center mr-3">
                                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m1.6 8L5 3H3m4 10h10m-10 0a2 2 0 100 4 2 2 0 000-4zm10 0a2 2 0 100 4 2 2 0 000-4z"></path>
                                        </svg>
                                    </div>
                                    <h3 class="text-xl font-bold text-white">Your Cart</h3>
                                </div>
                                <div id="cart" class="space-y-3">
                                    <div class="flex items-center justify-center py-8">
                                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                                        <span class="ml-3 text-white/70">Loading cart...</span>
                                    </div>
                                </div>
                                <div class="mt-6 pt-4 border-t border-white/20">
                                    <div class="flex justify-between items-center text-white">
                                        <span class="font-semibold">Total Items:</span>
                                        <span id="cartCount" class="bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-bold">0</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Notification -->
        <div id="notification" class="notification"></div>

        <script>
            let currentUser = null;

            function showNotification(message, type = 'success') {
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.className = `notification ${type}`;
                notification.classList.add('show');
                
                setTimeout(() => {
                    notification.classList.remove('show');
                }, 3000);
            }

            function handleFileSelect(input, previewId) {
                const file = input.files[0];
                const preview = document.getElementById(previewId);
                
                if (file) {
                    const fileName = file.name;
                    const fileSize = (file.size / 1024 / 1024).toFixed(2);
                    preview.innerHTML = `
                        <div class="text-green-400">
                            <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            <p class="font-semibold">${fileName}</p>
                            <p class="text-sm opacity-60">${fileSize} MB</p>
                        </div>
                    `;
                }
            }

            function updateCartDisplay(cartData) {
                const cartElement = document.getElementById('cart');
                const cartCount = document.getElementById('cartCount');
                
                if (!cartData || cartData.length === 0) {
                    cartElement.innerHTML = `
                        <div class="text-center py-8 text-white/60">
                            <svg class="w-16 h-16 mx-auto mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m1.6 8L5 3H3m4 10h10m-10 0a2 2 0 100 4 2 2 0 000-4zm10 0a2 2 0 100 4 2 2 0 000-4z"></path>
                            </svg>
                            <p>Your cart is empty</p>
                            <p class="text-sm mt-2">Add items using text, voice, or image!</p>
                        </div>
                    `;
                    cartCount.textContent = '0';
                } else {
                    const cartHTML = cartData.map(item => `
                        <div class="bg-white/10 rounded-lg p-3 flex items-center justify-between">
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                                <span class="text-white font-medium">${item}</span>
                            </div>
                            <button class="text-red-400 hover:text-red-300 transition-colors">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                </svg>
                            </button>
                        </div>
                    `).join('');
                    
                    cartElement.innerHTML = cartHTML;
                    cartCount.textContent = cartData.length;
                }
            }

            async function fetchCart(username) {
                try {
                    const formData = new FormData();
                    formData.append("user_query", "Show the cart");

                    const response = await fetch('/process-text/', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) throw new Error('Failed to fetch cart');
                    
                    const result = await response.json();
                    updateCartDisplay(result.cart || []);
                } catch (error) {
                    console.error('Error fetching cart:', error);
                    updateCartDisplay([]);
                    showNotification('Error loading cart', 'error');
                }
            }

            async function submitForm(form, endpoint) {
                const formData = new FormData(form);
                const button = form.querySelector('button[type="submit"]');
                const originalText = button.innerHTML;
                
                // Show loading state
                button.innerHTML = `
                    <div class="flex items-center justify-center">
                        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Processing...
                    </div>
                `;
                button.disabled = true;

                try {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) throw new Error('Request failed');

                    const result = await response.json();
                    updateCartDisplay(result.cart || []);
                    showNotification('Cart updated successfully!', 'success');
                    
                    // Reset form
                    form.reset();
                    
                } catch (error) {
                    console.error('Error:', error);
                    showNotification('Error processing request', 'error');
                } finally {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }
            }

            // Event Listeners
            document.getElementById('userForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('username').value;
                const button = e.target.querySelector('button[type="submit"]');
                const originalText = button.innerHTML;
                
                // Show loading state
                button.innerHTML = `
                    <div class="flex items-center justify-center">
                        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Signing in...
                    </div>
                `;
                button.disabled = true;

                try {
                    // Set username on server
                    const formData = new FormData();
                    formData.append('username', username);
                    
                    const response = await fetch('/login/', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) throw new Error('Login failed');
                    
                    const result = await response.json();
                    currentUser = username;
                    
                    // Set usernames in all forms (as backup)
                    document.getElementById('displayUsername').textContent = username;
                    
                    // Show dashboard
                    document.getElementById('loginSection').style.display = 'none';
                    document.getElementById('userSection').style.display = 'block';
                    
                    // Load cart
                    await fetchCart(username);
                    showNotification(`Welcome back, ${username}!`, 'success');
                    
                } catch (error) {
                    console.error('Login error:', error);
                    showNotification('Login failed. Please try again.', 'error');
                } finally {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }
            });

            document.getElementById('textForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                await submitForm(e.target, '/process-text/');
            });

            document.getElementById('imageForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                await submitForm(e.target, '/process-image/');
            });

            document.getElementById('voiceForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                await submitForm(e.target, '/process-voice/');
            });
        </script>
    </body>
    </html>
    ''')

# Global variable to store current username
current_username = None

@app.route('/login/', methods=['POST'])
def login():
    global current_username
    username = request.form.get('username')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    current_username = username
    return jsonify({'success': True, 'username': username})

@app.route('/process-text/', methods=['POST'])
def process_text():
    global current_username
    user_query = request.form.get('user_query')
    
    # Use global username or fallback to form data
    username = current_username or request.form.get('username')

    if not username or not user_query:
        return jsonify({'error': 'Missing username or query'}), 400

    try:
        response = requests.post('http://localhost:8000/process-text/', data={
            'username': username,
            'user_query': user_query
        })
        response.raise_for_status()
        api_response = response.json()

        # Extract product names from the cart
        cart_items = api_response.get("cart", {}).get("products", [])
        product_list = [item.get("product_name") for item in cart_items]

        print("Resolved cart product names:", product_list)

        return jsonify({'cart': product_list})
    except requests.RequestException as e:
        return jsonify({'error': f'API error: {str(e)}'}), 500

@app.route('/process-image/', methods=['POST'])
def process_image():
    global current_username
    
    # Use global username or fallback to form data
    username = current_username or request.form.get('username')
    
    if 'image' not in request.files or not username:
        return jsonify({'error': 'Missing image or username'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                response = requests.post('http://localhost:8000/process-image/', 
                                      files={'image': f}, 
                                      data={'username': username})
                response.raise_for_status()
                api_response = response.json()
                cart_items = api_response.get("cart", {}).get("products", [])
                product_list = [item.get("product_name") for item in cart_items]
                return jsonify({'cart': product_list})
        except requests.RequestException as e:
            return jsonify({'error': f'API error: {str(e)}'}), 500
        finally:
            os.remove(file_path)
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process-voice/', methods=['POST'])
def process_voice():
    username = 'vaibhav123'
    audio = request.files.get('audio')

    print(f"Received voice request: username={username}, audio={audio.filename if audio else 'None'}")

    if not username or not audio or audio.filename == '':
        return jsonify({'error': 'Missing audio or username'}), 400

    if allowed_file(audio.filename):
        filename = secure_filename(audio.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio.save(path)

        try:
            with open(path, 'rb') as f:
                response = requests.post(
                    'http://localhost:8000/process-voice/',
                    data={'username': username},
                    files={'audio': f}
                )
            response.raise_for_status()
            api_response = response.json()
            cart_items = api_response.get("cart", {}).get("products", [])
            product_list = [item.get("product_name") for item in cart_items]
            return jsonify({'cart': product_list})
        except requests.RequestException as e:
            return jsonify({'error': f'API error: {str(e)}'}), 500
        finally:
            os.remove(path)
    return jsonify({'error': 'Invalid audio file type'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8001)