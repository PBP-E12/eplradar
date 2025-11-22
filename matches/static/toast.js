function showToast(title, message, type = 'success') {
  const toast = document.getElementById('toast-component');
  const toastTitle = document.getElementById('toast-title');
  const toastMessage = document.getElementById('toast-message');
  const toastIcon = document.getElementById('toast-icon');
  
  toastTitle.textContent = title;
  toastMessage.textContent = message;
  
  // Reset classes
  toast.classList.remove('bg-green-100', 'border-green-400', 'bg-red-100', 'border-red-400');
  
  if (type === 'success') {
    toast.classList.add('bg-green-100', 'border-green-400');
    toastIcon.textContent = '✅';
  } else if (type === 'error') {
    toast.classList.add('bg-red-100', 'border-red-400');
    toastIcon.textContent = '❌';
  }
  
  // Show toast
  toast.classList.remove('opacity-0', 'translate-y-64');
  toast.classList.add('opacity-100', 'translate-y-0');
  
  // Auto hide after 3 seconds
  setTimeout(() => {
    hideToast();
  }, 3000);
}

function hideToast() {
  const toast = document.getElementById('toast-component');
  toast.classList.remove('opacity-100', 'translate-y-0');
  toast.classList.add('opacity-0', 'translate-y-64');
}