/**
 * FrontierPilot 2.0 — Firebase Authentication & Google Sign-In Module
 * 
 * Provides client-side Google Sign-In, profile state persistence,
 * and 1-tap authentication on Netlify CDN and local development.
 */

// Default configuration with safe fallback
const DEFAULT_FIREBASE_CONFIG = {
  apiKey: "AIzaSyAZdruWXjQ-mbfBu3_pTYP3V3VwCpDkLQk",
  authDomain: "frontierpilot-studio.firebaseapp.com",
  projectId: "frontierpilot-studio",
  storageBucket: "frontierpilot-studio.appspot.com",
  appId: "1:76740519:web:frontierpilot"
};

let auth = null;
let googleProvider = null;
let currentUser = null;

// Initialize Firebase Auth
export async function initFirebaseAuth() {
  try {
    const { initializeApp, getApps } = await import("https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js");
    const { getAuth, GoogleAuthProvider, onAuthStateChanged, getRedirectResult } = await import("https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js");

    const config = window.__FIREBASE_CONFIG__ || DEFAULT_FIREBASE_CONFIG;
    const app = getApps().length === 0 ? initializeApp(config) : getApps()[0];
    
    auth = getAuth(app);
    googleProvider = new GoogleAuthProvider();

    // Check for redirect sign-in result (mobile / fallback)
    getRedirectResult(auth).then((result) => {
      if (result && result.user) {
        currentUser = result.user;
        updateAuthUI(result.user);
      }
    }).catch((err) => {
      console.warn("⚠️ [Firebase Auth] Redirect result notice:", err.message);
    });

    // Listen to Auth State
    onAuthStateChanged(auth, (user) => {
      currentUser = user;
      updateAuthUI(user);
    });

    console.log("🔒 [Firebase Auth] Initialized successfully");
  } catch (err) {
    console.warn("⚠️ [Firebase Auth] Running in Local Founder Mode (Offline / Unconfigured):", err.message);
    updateAuthUI({
      displayName: "Aryan Sharma",
      email: "aryanaryan.9956@icloud.com",
      isLocalFounder: true
    });
  }
}

// Sign In with Google Popup (with Redirect Fallback for mobile / popup-blockers)
export async function signInWithGoogle() {
  if (!auth) {
    alert("Firebase Auth is in Local Founder Mode. Logged in as Aryan Sharma.");
    return;
  }
  try {
    const { signInWithPopup } = await import("https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js");
    const result = await signInWithPopup(auth, googleProvider);
    currentUser = result.user;
    updateAuthUI(result.user);
    return result.user;
  } catch (err) {
    if (err.code === "auth/popup-closed-by-user") {
      console.log("Google sign-in popup closed by user");
    } else if (err.code === "auth/popup-blocked" || err.code === "auth/cancelled-popup-request") {
      console.log("Popup blocked or cancelled, falling back to signInWithRedirect...");
      const { signInWithRedirect } = await import("https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js");
      await signInWithRedirect(auth, googleProvider);
    } else {
      console.error("Firebase Sign-In Error:", err);
      // Graceful fallback for local/demo domain
      alert("Sign-In note: " + err.message + "\nContinuing in Local Founder Mode.");
    }
  }
}

// Sign Out
export async function signOutUser() {
  if (auth) {
    try {
      const { signOut } = await import("https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js");
      await signOut(auth);
    } catch (e) {}
  }
  currentUser = null;
  updateAuthUI(null);
}

// Update UI Elements
function updateAuthUI(user) {
  const authContainer = document.getElementById("firebaseAuthContainer");
  if (!authContainer) return;

  if (user) {
    const name = user.displayName || "Founder";
    const email = user.email || "aryanaryan.9956@icloud.com";
    const avatar = user.photoURL || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=80&q=80";

    authContainer.innerHTML = `
      <div class="dropdown">
        <button class="btn btn-outline-secondary btn-sm d-flex align-items-center gap-2 py-1 px-2 border rounded-pill shadow-sm bg-white" type="button" data-bs-toggle="dropdown" aria-expanded="false" title="${email}">
          <img src="${avatar}" alt="${name}" class="rounded-circle" width="22" height="22" style="object-fit: cover; border: 1.5px solid #10b981;">
          <span class="small fw-semibold text-dark d-none d-md-inline" style="font-size: 11.5px;">${name}</span>
          <span class="badge bg-success bg-opacity-10 text-success p-1 rounded-circle" style="width: 7px; height: 7px; padding: 0 !important;"></span>
        </button>
        <ul class="dropdown-menu dropdown-menu-end shadow-sm" style="font-size: 12px; min-width: 200px;">
          <li class="px-3 py-2 border-bottom">
            <div class="fw-bold text-dark">${name}</div>
            <div class="text-muted small text-truncate">${email}</div>
            <span class="badge bg-success-subtle text-success border border-success-subtle mt-1" style="font-size: 10px;">Authenticated Founder</span>
          </li>
          <li><a class="dropdown-item py-2 text-danger" href="#" id="firebaseSignOutBtn"><i class="bi bi-box-arrow-right me-2"></i> Sign Out</a></li>
        </ul>
      </div>
    `;

    const signOutBtn = document.getElementById("firebaseSignOutBtn");
    if (signOutBtn) {
      signOutBtn.addEventListener("click", (e) => {
        e.preventDefault();
        signOutUser();
      });
    }
  } else {
    authContainer.innerHTML = `
      <button class="btn btn-outline-secondary btn-sm d-flex align-items-center gap-2 py-1 px-2 border rounded-pill shadow-sm bg-white" id="firebaseSignInBtn" title="Sign in with Google">
        <svg width="14" height="14" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
        </svg>
        <span class="small fw-semibold text-dark" style="font-size: 11.5px;">Sign in</span>
      </button>
    `;

    const signInBtn = document.getElementById("firebaseSignInBtn");
    if (signInBtn) {
      signInBtn.addEventListener("click", (e) => {
        e.preventDefault();
        signInWithGoogle();
      });
    }
  }
}

// Auto-boot on load
if (typeof window !== "undefined") {
  window.addEventListener("DOMContentLoaded", () => {
    initFirebaseAuth();
  });
}
