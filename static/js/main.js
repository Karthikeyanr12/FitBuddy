/**
 * FitBuddy - Interactive Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // Configure Marked.js if loaded
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    // Handle Generation Form Submit State
    const planForm = document.getElementById('plan-form');
    if (planForm) {
        planForm.addEventListener('submit', (e) => {
            const btn = document.getElementById('generate-btn');
            const spinner = document.getElementById('generate-spinner');
            const loadingState = document.getElementById('loading-state');
            
            if (btn && spinner) {
                const btnSpan = btn.querySelector('span');
                if (btnSpan) btnSpan.textContent = 'Generating Plan with AI...';
                spinner.classList.remove('hidden');
                btn.disabled = true;
            }

            if (loadingState) {
                loadingState.classList.remove('hidden');
                loadingState.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    }

    // Handle Feedback Form Submit State
    const feedbackForm = document.getElementById('feedback-form');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', (e) => {
            const btn = document.getElementById('update-btn');
            const spinner = document.getElementById('update-spinner');
            if (btn && spinner) {
                const btnSpan = btn.querySelector('span');
                if (btnSpan) btnSpan.textContent = 'Revising Plan with AI...';
                spinner.classList.remove('hidden');
                btn.disabled = true;
            }
        });
    }
});

/**
 * Toast Notification Utility
 */
function showToast(message, duration = 3000) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');
    if (!toast || !toastMsg) return;

    toastMsg.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}
